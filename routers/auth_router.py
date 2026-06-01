from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from crud.user_crud import create_user, get_user_by_username, verify_password
from schemas.auth_schema import LoginRequest, LoginResponse, RegisterRequest, Token
from schemas.user_schema import UserRead
from utils.auth_utils import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_active_user
from models.system_log import SystemLog

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """用户登录"""
    # 查找用户
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token, expires_at = create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role},
        expires_delta=access_token_expires
    )

    db.add(SystemLog(level="INFO", message=f"User login: user_id={user.id}, username={user.username}, role={user.role}"))
    db.commit()
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_at=expires_at,
        user_id=user.id,
        username=user.username,
        role=user.role
    )

@router.post("/register", response_model=UserRead)
async def register(register_data: RegisterRequest, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    existing_user = get_user_by_username(db, register_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # 创建新用户
    new_user = create_user(db, register_data)
    db.add(SystemLog(level="INFO", message=f"User registered: user_id={new_user.id}, username={new_user.username}"))
    db.commit()
    return new_user

@router.get("/me", response_model=UserRead)
async def get_current_user_info(current_user = Depends(get_current_active_user)):
    """获取当前用户信息"""
    return current_user
