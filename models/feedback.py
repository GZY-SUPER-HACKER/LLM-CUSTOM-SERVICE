from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class UserFeedback(Base):
    __tablename__ = "user_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    feedback_type = Column(String(20), nullable=False)  # 'satisfied' or 'unsatisfied'
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(20), default='submitted')  # 'submitted', 'processing', 'processed'