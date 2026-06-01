from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from database import Base


class UserTextFeedback(Base):
    __tablename__ = "user_text_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    session_id = Column(String(255), nullable=True, index=True)
    content = Column(Text, nullable=False)
    source = Column(String(30), nullable=False, default="manual_text")
    status = Column(String(20), default="submitted")
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
