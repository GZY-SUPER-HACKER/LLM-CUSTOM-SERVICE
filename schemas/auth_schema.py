from pydantic import BaseModel, EmailStr
from datetime import datetime

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "user"

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime

class TokenData(BaseModel):
    user_id: int
    username: str
    role: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user_id: int
    username: str
    role: str
