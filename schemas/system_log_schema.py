from pydantic import BaseModel
from datetime import datetime

class SystemLogBase(BaseModel):
    level: str
    message: str

class SystemLogCreate(SystemLogBase):
    pass

class SystemLogRead(SystemLogBase):
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
