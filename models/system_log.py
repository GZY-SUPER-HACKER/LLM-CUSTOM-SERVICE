from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20))  # INFO / WARNING / ERROR
    message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
