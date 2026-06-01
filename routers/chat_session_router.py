from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.chat_session import ChatSession
from models.system_log import SystemLog
from schemas.chat_schema import ChatSessionCreate, ChatSessionRead

router = APIRouter(prefix="/chat_sessions", tags=["Chat Sessions"])

@router.post("/", response_model=ChatSessionRead)
def create_session(session: ChatSessionCreate, db: Session = Depends(get_db)):
    db_session = ChatSession(**session.model_dump())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    db.add(SystemLog(level="INFO", message=f"Chat session created: session_id={db_session.id}, user_id={db_session.user_id}"))
    db.commit()
    return db_session

@router.get("/", response_model=list[ChatSessionRead])
def get_sessions(db: Session = Depends(get_db)):
    return db.query(ChatSession).all()


@router.delete("/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    user_id = session.user_id
    db.delete(session)
    db.commit()
    db.add(SystemLog(level="WARNING", message=f"Chat session deleted: session_id={session_id}, user_id={user_id}"))
    db.commit()
    return {"message": "会话删除成功"}
