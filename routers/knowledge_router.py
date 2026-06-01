import re
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session
from database import get_db
from models.knowledge_doc import KnowledgeDoc
from models.knowledge_change_log import KnowledgeChangeLog
from schemas.knowledge_schema import (
    KnowledgeBatchUndoResponse,
    KnowledgeChangeLogRead,
    KnowledgeDocCreate,
    KnowledgeDocRead,
    KnowledgeDocUpdate,
    KnowledgeImportRequest,
    KnowledgeImportResponse,
)
from utils.rag_engine import _embed_text, _index

router = APIRouter(prefix="/knowledge_docs", tags=["Knowledge Docs"])

@router.post("/", response_model=KnowledgeDocRead)
def create_doc(doc: KnowledgeDocCreate, db: Session = Depends(get_db)):
    payload = doc.model_dump()
    payload["domain"] = payload.get("domain") or "general"
    payload["source"] = payload.get("source") or "manual_input"
    text_for_embed = (payload.get("description") or payload["title"]).strip()
    if not text_for_embed:
        raise HTTPException(status_code=400, detail="知识内容不能为空")

    vector_id = payload.get("vector_id") or f"kb_{uuid.uuid4().hex}"
    payload["vector_id"] = vector_id

    db_doc = KnowledgeDoc(**payload)
    db.add(db_doc)
    try:
        db.commit()
        db.refresh(db_doc)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"MySQL写入失败: {exc}")

    try:
        _index.upsert(
            vectors=[
                {
                    "id": vector_id,
                    "values": _embed_text(text_for_embed),
                    "metadata": {
                        "title": payload["title"],
                        "source": payload["source"],
                        "domain": payload["domain"],
                        "chunk_index": 1,
                        "content": text_for_embed[:800],
                    },
                }
            ]
        )
    except Exception as exc:
        db.delete(db_doc)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Pinecone写入失败，已回滚MySQL: {exc}")

    _log_change(db=db, action="manual_create", doc=db_doc, detail="手动新增知识条目")
    return db_doc

@router.get("/", response_model=list[KnowledgeDocRead])
def get_docs(
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=1000),
    keyword: str | None = Query(None),
    domain: str | None = Query(None),
    source: str | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(KnowledgeDoc)
    if keyword:
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            (KnowledgeDoc.title.like(kw)) | (KnowledgeDoc.description.like(kw))
        )
    if domain:
        query = query.filter(KnowledgeDoc.domain == domain.strip())
    if source:
        query = query.filter(KnowledgeDoc.source.like(f"%{source.strip()}%"))

    return query.order_by(KnowledgeDoc.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{doc_id}", response_model=KnowledgeDocRead)
def get_doc(doc_id: int, db: Session = Depends(get_db)):
    row = db.query(KnowledgeDoc).filter(KnowledgeDoc.id == doc_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="知识条目不存在")
    return row


@router.put("/{doc_id}", response_model=KnowledgeDocRead)
def update_doc(doc_id: int, payload: KnowledgeDocUpdate, db: Session = Depends(get_db)):
    row = db.query(KnowledgeDoc).filter(KnowledgeDoc.id == doc_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="知识条目不存在")

    data = payload.model_dump(exclude_unset=True)
    old_snapshot = {
        "domain": row.domain,
        "title": row.title,
        "source": row.source,
        "description": row.description,
        "vector_id": row.vector_id,
    }
    old_vector_id = row.vector_id or f"kb_{uuid.uuid4().hex}"
    for key, value in data.items():
        setattr(row, key, value)
    if not row.domain:
        row.domain = "general"
    if not row.source:
        row.source = "manual_input"
    if not row.vector_id:
        row.vector_id = old_vector_id

    text_for_embed = (row.description or row.title or "").strip()
    if not text_for_embed:
        raise HTTPException(status_code=400, detail="知识内容不能为空")

    try:
        _index.upsert(
            vectors=[
                {
                    "id": row.vector_id,
                    "values": _embed_text(text_for_embed),
                    "metadata": {
                        "title": row.title,
                        "source": row.source,
                        "domain": row.domain,
                        "chunk_index": 1,
                        "content": text_for_embed[:800],
                    },
                }
            ]
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Pinecone更新失败: {exc}")

    try:
        db.commit()
        db.refresh(row)
    except Exception as exc:
        db.rollback()
        try:
            previous_text = (old_snapshot["description"] or old_snapshot["title"] or "").strip()
            if previous_text and old_snapshot["vector_id"]:
                _index.upsert(
                    vectors=[
                        {
                            "id": old_snapshot["vector_id"],
                            "values": _embed_text(previous_text),
                            "metadata": {
                                "title": old_snapshot["title"],
                                "source": old_snapshot["source"] or "manual_input",
                                "domain": old_snapshot["domain"] or "general",
                                "chunk_index": 1,
                                "content": previous_text[:800],
                            },
                        }
                    ]
                )
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"MySQL更新失败，已尝试回滚Pinecone: {exc}")

    _log_change(db=db, action="manual_update", doc=row, detail="手动更新知识条目")
    return row


@router.delete("/{doc_id}")
def delete_doc(doc_id: int, db: Session = Depends(get_db)):
    row = db.query(KnowledgeDoc).filter(KnowledgeDoc.id == doc_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="知识条目不存在")
    backup_text = (row.description or row.title or "").strip()
    backup_vector_id = row.vector_id
    if row.vector_id:
        try:
            _index.delete(ids=[row.vector_id])
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Pinecone删除失败: {exc}")

    _log_change(
        db=db,
        action="manual_delete",
        doc=row,
        detail="手动删除知识条目",
    )
    db.delete(row)
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        if backup_vector_id and backup_text:
            try:
                _index.upsert(
                    vectors=[
                        {
                            "id": backup_vector_id,
                            "values": _embed_text(backup_text),
                            "metadata": {
                                "title": row.title,
                                "source": row.source or "manual_input",
                                "domain": row.domain or "general",
                                "chunk_index": 1,
                                "content": backup_text[:800],
                            },
                        }
                    ]
                )
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=f"MySQL删除失败，已尝试恢复Pinecone: {exc}")
    return {"message": "知识条目删除成功"}


def _split_sentences(text: str) -> list[str]:
    text = (text or "").strip()
    if not text:
        return []
    pieces = re.split(r"(?<=[。！？!?\.])\s+|\n{2,}", text)
    return [p.strip() for p in pieces if p and p.strip()]


def _semantic_chunk(text: str, target_size: int = 500, max_size: int = 800) -> list[str]:
    sentences = _split_sentences(text)
    if not sentences:
        return []
    if len(sentences) == 1:
        only = sentences[0]
        return [only[i : i + max_size] for i in range(0, len(only), max_size)]

    embs = [_embed_text(s) for s in sentences]

    def cosine(a: list[float], b: list[float]) -> float:
        dot = 0.0
        na = 0.0
        nb = 0.0
        for ai, bi in zip(a, b):
            dot += ai * bi
            na += ai * ai
            nb += bi * bi
        if na <= 0 or nb <= 0:
            return 0.0
        return dot / ((na**0.5) * (nb**0.5))

    chunks: list[str] = []
    current = sentences[0]
    for i in range(1, len(sentences)):
        sent = sentences[i]
        score = cosine(embs[i - 1], embs[i])
        if (len(current) >= target_size and score < 0.62) or len(current) + len(sent) > max_size:
            chunks.append(current.strip())
            current = sent
        else:
            current = f"{current}\n{sent}"
    if current.strip():
        chunks.append(current.strip())
    return chunks


def _create_change_log(
    action: str,
    detail: str,
    doc: KnowledgeDoc | None = None,
    batch_id: str | None = None,
) -> KnowledgeChangeLog:
    return KnowledgeChangeLog(
        action=action,
        batch_id=batch_id,
        doc_id=doc.id if doc else None,
        vector_id=doc.vector_id if doc else None,
        title=doc.title if doc else None,
        source=doc.source if doc else None,
        domain=doc.domain if doc else None,
        detail=detail,
    )


def _log_change(
    db: Session,
    action: str,
    detail: str,
    doc: KnowledgeDoc | None = None,
    batch_id: str | None = None,
) -> None:
    log = _create_change_log(action=action, detail=detail, doc=doc, batch_id=batch_id)
    db.add(log)
    db.commit()


def _read_pdf_bytes(content: bytes) -> str:
    try:
        from pypdf import PdfReader
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"缺少PDF解析依赖 pypdf: {exc}")

    import io

    text_list = []
    reader = PdfReader(io.BytesIO(content))
    for page in reader.pages:
        text_list.append(page.extract_text() or "")
    return "\n".join(text_list).strip()


def _parse_upload_content(filename: str, raw: bytes) -> str:
    lower_name = (filename or "").lower()
    if lower_name.endswith(".pdf"):
        return _read_pdf_bytes(raw)
    # txt / md 统一按 utf-8 优先读取
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("gbk", errors="ignore")


@router.post("/import/chunked", response_model=KnowledgeImportResponse)
def import_chunked_knowledge(payload: KnowledgeImportRequest, db: Session = Depends(get_db)):
    content = (payload.content or "").strip()
    if not content:
        raise HTTPException(status_code=400, detail="导入内容不能为空")

    chunks = _semantic_chunk(
        content,
        target_size=max(120, payload.chunk_size),
        max_size=max(200, payload.chunk_size + max(100, payload.chunk_overlap)),
    )
    if not chunks:
        raise HTTPException(status_code=400, detail="未能切分出有效知识片段")

    vector_rows = []
    db_rows = []
    batch_id = f"batch_{uuid.uuid4().hex}"
    for idx, chunk in enumerate(chunks, start=1):
        vector_id = f"kb_{uuid.uuid4().hex}"
        embedding = _embed_text(chunk)
        vector_rows.append(
            {
                "id": vector_id,
                "values": embedding,
                "metadata": {
                    "title": payload.title,
                    "source": payload.source or "manual_input",
                    "domain": payload.domain or "general",
                    "chunk_index": idx,
                    "content": chunk[:800],
                },
            }
        )
        db_rows.append(
            KnowledgeDoc(
                domain=payload.domain or "general",
                title=f"{payload.title} - 分块{idx}",
                source=payload.source or "manual_input",
                vector_id=vector_id,
                description=chunk,
            )
        )

    try:
        _index.upsert(vectors=vector_rows)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"向量写入失败: {exc}")

    try:
        for row in db_rows:
            db.add(row)
        db.flush()
        for row in db_rows:
            db.add(
                _create_change_log(
                    action="batch_import",
                    batch_id=batch_id,
                    doc=row,
                    detail=f"批量导入创建分块#{row.title}",
                )
            )
        db.commit()
    except Exception as exc:
        db.rollback()
        vector_ids = [v["id"] for v in vector_rows]
        if vector_ids:
            try:
                _index.delete(ids=vector_ids)
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=f"MySQL写入失败，已尝试回滚Pinecone: {exc}")

    for row in db_rows:
        db.refresh(row)

    return KnowledgeImportResponse(
        imported_count=len(db_rows),
        vector_ids=[r.vector_id for r in db_rows],
        batch_id=batch_id,
        title=payload.title,
        source=payload.source,
        domain=payload.domain,
    )


@router.post("/import/files", response_model=KnowledgeImportResponse)
async def import_files_chunked(
    title: str = Form(...),
    source: str = Form("manual_upload"),
    domain: str = Form("general"),
    chunk_size: int = Form(500),
    chunk_overlap: int = Form(80),
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    full_text_parts: list[str] = []
    for f in files:
        file_name = f.filename or ""
        if not file_name.lower().endswith((".txt", ".md", ".pdf")):
            raise HTTPException(status_code=400, detail=f"暂不支持文件类型: {file_name}")
        raw = await f.read()
        parsed = _parse_upload_content(file_name, raw).strip()
        if parsed:
            full_text_parts.append(parsed)

    merged = "\n\n".join(full_text_parts).strip()
    if not merged:
        raise HTTPException(status_code=400, detail="上传文件未解析到有效内容")

    req = KnowledgeImportRequest(
        title=title,
        source=source,
        domain=domain,
        content=merged,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return import_chunked_knowledge(req, db)


@router.get("/change_logs", response_model=list[KnowledgeChangeLogRead])
def list_change_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return (
        db.query(KnowledgeChangeLog)
        .order_by(KnowledgeChangeLog.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/change_logs/batches")
def list_batch_change_logs(db: Session = Depends(get_db)):
    logs = (
        db.query(KnowledgeChangeLog)
        .filter(KnowledgeChangeLog.action == "batch_import", KnowledgeChangeLog.batch_id.isnot(None))
        .order_by(KnowledgeChangeLog.created_at.desc())
        .all()
    )
    grouped: dict[str, dict] = {}
    for log in logs:
        if not log.batch_id:
            continue
        if log.batch_id not in grouped:
            grouped[log.batch_id] = {
                "batch_id": log.batch_id,
                "title": log.title,
                "source": log.source,
                "domain": log.domain,
                "created_at": log.created_at,
                "imported_count": 0,
                "undone": False,
            }
        grouped[log.batch_id]["imported_count"] += 1
        grouped[log.batch_id]["undone"] = grouped[log.batch_id]["undone"] or bool(log.undone)
    return list(grouped.values())


@router.post("/batches/{batch_id}/undo", response_model=KnowledgeBatchUndoResponse)
def undo_batch_import(batch_id: str, db: Session = Depends(get_db)):
    logs = (
        db.query(KnowledgeChangeLog)
        .filter(
            KnowledgeChangeLog.batch_id == batch_id,
            KnowledgeChangeLog.action == "batch_import",
            KnowledgeChangeLog.undone == False,  # noqa: E712
        )
        .all()
    )
    if not logs:
        raise HTTPException(status_code=404, detail="未找到可回滚的批量导入记录")

    vector_ids = [x.vector_id for x in logs if x.vector_id]
    if vector_ids:
        try:
            _index.delete(ids=vector_ids)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"回滚时向量删除失败: {exc}")

    doc_ids = [x.doc_id for x in logs if x.doc_id is not None]
    removed = 0
    for doc_id in doc_ids:
        doc = db.query(KnowledgeDoc).filter(KnowledgeDoc.id == doc_id).first()
        if doc:
            db.delete(doc)
            removed += 1
    for log in logs:
        log.undone = True

    db.commit()

    undo_log = KnowledgeChangeLog(
        action="batch_undo",
        batch_id=batch_id,
        detail=f"回滚批量导入，删除 {removed} 条知识",
        undone=False,
    )
    db.add(undo_log)
    db.commit()

    return KnowledgeBatchUndoResponse(batch_id=batch_id, removed_count=removed)
