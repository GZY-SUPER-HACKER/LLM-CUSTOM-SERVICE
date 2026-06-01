from pydantic import BaseModel
from datetime import datetime

class KnowledgeDocBase(BaseModel):
    domain: str | None = "general"
    title: str
    source: str | None = None
    vector_id: str | None = None
    description: str | None = None

class KnowledgeDocCreate(KnowledgeDocBase):
    pass

class KnowledgeDocUpdate(BaseModel):
    domain: str | None = None
    title: str | None = None
    source: str | None = None
    description: str | None = None


class KnowledgeImportRequest(BaseModel):
    title: str
    source: str | None = "manual_input"
    domain: str | None = "general"
    content: str
    chunk_size: int = 500
    chunk_overlap: int = 80


class KnowledgeImportResponse(BaseModel):
    imported_count: int
    vector_ids: list[str]
    batch_id: str | None = None
    title: str
    source: str | None = None
    domain: str | None = None


class KnowledgeBatchUndoResponse(BaseModel):
    batch_id: str
    removed_count: int


class KnowledgeChangeLogRead(BaseModel):
    id: int
    action: str
    batch_id: str | None = None
    doc_id: int | None = None
    vector_id: str | None = None
    title: str | None = None
    source: str | None = None
    domain: str | None = None
    detail: str | None = None
    undone: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class KnowledgeDocRead(KnowledgeDocBase):
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
