from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ManualInterventionBase(BaseModel):
    session_id: int
    handler: Optional[str] = None
    note: Optional[str] = None

class ManualInterventionCreate(ManualInterventionBase):
    emotion_type: Optional[str] = None
    emotion_intensity: Optional[float] = None
    emotion_level: Optional[str] = None
    is_emotionally_agitated: Optional[bool] = None
    emotion_confidence: Optional[float] = None
    tone_intensity: Optional[float] = None
    negative_emotion_degree: Optional[float] = None
    urgency_level: Optional[float] = None
    loss_of_control_risk: Optional[float] = None
    transfer_reason: Optional[str] = None
    conversation_topic: Optional[str] = None
    user_intent: Optional[str] = None
    conversation_progress: Optional[str] = None

class ManualInterventionRead(ManualInterventionBase):
    id: int
    emotion_type: Optional[str] = None
    emotion_intensity: Optional[float] = None
    emotion_level: Optional[str] = None
    is_emotionally_agitated: Optional[bool] = None
    emotion_confidence: Optional[float] = None
    tone_intensity: Optional[float] = None
    negative_emotion_degree: Optional[float] = None
    urgency_level: Optional[float] = None
    loss_of_control_risk: Optional[float] = None
    transfer_reason: Optional[str] = None
    conversation_topic: Optional[str] = None
    user_intent: Optional[str] = None
    conversation_progress: Optional[str] = None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }