from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FeedbackCreate(BaseModel):
    """创建反馈的请求模型"""
    message_id: str
    user_id: str
    session_id: str
    feedback_type: str  # 'satisfied' or 'unsatisfied'
    status: Optional[str] = 'submitted'
    
    class Config:
        json_schema_extra = {
            "example": {
                "message_id": "msg_1234567890",
                "user_id": "user_123",
                "session_id": "session_456",
                "feedback_type": "satisfied",
                "status": "submitted"
            }
        }

class FeedbackResponse(BaseModel):
    """反馈的响应模型"""
    id: int
    message_id: str
    user_id: str
    session_id: str
    feedback_type: str
    timestamp: datetime
    status: str
    feedback_source: str = 'chat_reaction'
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "message_id": "msg_1234567890",
                "user_id": "user_123",
                "session_id": "session_456",
                "feedback_type": "satisfied",
                "timestamp": "2024-01-01T12:00:00",
                "status": "submitted"
            }
        }


class FeedbackStatusUpdate(BaseModel):
    """更新反馈状态的请求模型"""
    status: str


class TextFeedbackCreate(BaseModel):
    user_id: str
    session_id: Optional[str] = None
    content: str
    status: Optional[str] = 'submitted'


class TextFeedbackResponse(BaseModel):
    id: int
    user_id: str
    session_id: Optional[str] = None
    content: str
    source: str
    timestamp: datetime
    status: str