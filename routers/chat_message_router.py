from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.chat_message import ChatMessage
from models.system_log import SystemLog
from schemas.chat_schema import ChatMessageCreate, ChatMessageRead

router = APIRouter(prefix="/chat_messages", tags=["Chat Messages"])

@router.post("/", response_model=ChatMessageRead)
def create_message(message: ChatMessageCreate, db: Session = Depends(get_db)):
    db_msg = ChatMessage(**message.model_dump())
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)
    # 避免日志爆炸：只记录 assistant 消息
    if db_msg.role == "assistant":
        db.add(SystemLog(level="INFO", message=f"Assistant message created: message_id={db_msg.id}, session_id={db_msg.session_id}"))
        db.commit()
    return db_msg

@router.get("/", response_model=list[ChatMessageRead])
def get_messages(db: Session = Depends(get_db)):
    return db.query(ChatMessage).all()

@router.get("/session/{session_id}", response_model=list[ChatMessageRead])
def get_messages_by_session(session_id: int, db: Session = Depends(get_db)):
    return db.query(ChatMessage).filter(ChatMessage.session_id == session_id).all()
