from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class KnowledgeDoc(Base):
    __tablename__ = "knowledge_docs"
    domain = Column(String(100), index=True)  # 新增领域字段
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    source = Column(String(255))  # 文件名、网页URL、上传来源等
    vector_id = Column(String(255))  # 对应向量数据库ID
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


