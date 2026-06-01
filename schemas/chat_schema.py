from pydantic import BaseModel
from datetime import datetime

class ChatSessionBase(BaseModel):
    user_id: int

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionRead(ChatSessionBase):
    id: int
    created_at: datetime
    conversation_topic: str | None = None
    user_intent: str | None = None
    conversation_progress: str | None = None

    model_config = {
        "from_attributes": True
    }

# ---- ChatMessage ----
class ChatMessageBase(BaseModel):
    session_id: int
    role: str
    content: str

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageRead(ChatMessageBase):
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

# ---- Send Message Request ----
class SendMessageRequest(BaseModel):
    user_id: int
    user_input: str
    session_id: int | None = None
