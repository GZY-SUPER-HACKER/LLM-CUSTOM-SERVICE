from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str = "user"

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
