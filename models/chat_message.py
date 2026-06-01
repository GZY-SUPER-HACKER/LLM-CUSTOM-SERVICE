from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"))
    role = Column(String(20))  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
