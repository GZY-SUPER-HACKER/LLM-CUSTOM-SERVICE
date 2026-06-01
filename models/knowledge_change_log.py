from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from database import Base


class KnowledgeChangeLog(Base):
    __tablename__ = "knowledge_change_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(50), nullable=False, index=True)
    batch_id = Column(String(100), nullable=True, index=True)
    doc_id = Column(Integer, nullable=True, index=True)
    vector_id = Column(String(255), nullable=True, index=True)
    title = Column(String(200), nullable=True)
    source = Column(String(255), nullable=True)
    domain = Column(String(100), nullable=True)
    detail = Column(Text, nullable=True)
    undone = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
