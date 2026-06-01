from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Text
from sqlalchemy.sql import func
from database import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    conversation_topic = Column(String(255), nullable=True)
    user_intent = Column(String(100), nullable=True)
    conversation_progress = Column(Text, nullable=True)
