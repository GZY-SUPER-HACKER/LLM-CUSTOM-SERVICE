from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from crud import user_crud
from schemas.user_schema import UserCreate, UserRead
from utils.auth_utils import get_current_active_user, get_admin_user
from models.system_log import SystemLog

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    created = user_crud.create_user(db, user)
    db.add(SystemLog(level="INFO", message=f"User created: user_id={created.id}, username={created.username}"))
    db.commit()
    return created

@router.get("/", response_model=list[UserRead])
def get_users(db: Session = Depends(get_db)):
    return user_crud.get_users(db)

@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    # 普通用户只能查看自己的信息，管理员可以查看所有用户信息
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return user_crud.get_user_by_id(db, user_id)
