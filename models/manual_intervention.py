from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime, Float, Boolean
from sqlalchemy.sql import func
from database import Base

class ManualIntervention(Base):
    __tablename__ = "manual_interventions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="SET NULL"))
    handler = Column(String(50))
    note = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    emotion_type = Column(String(50), nullable=True)
    emotion_intensity = Column(Float, nullable=True)
    emotion_level = Column(String(20), nullable=True)
    is_emotionally_agitated = Column(Boolean, nullable=True)
    emotion_confidence = Column(Float, nullable=True)

    tone_intensity = Column(Float, nullable=True)
    negative_emotion_degree = Column(Float, nullable=True)
    urgency_level = Column(Float, nullable=True)
    loss_of_control_risk = Column(Float, nullable=True)

    transfer_reason = Column(Text, nullable=True)
    conversation_topic = Column(String(100), nullable=True)
    user_intent = Column(String(50), nullable=True)
    conversation_progress = Column(Text, nullable=True)