from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.system_log import SystemLog
from schemas.system_log_schema import SystemLogCreate, SystemLogRead

router = APIRouter(prefix="/system_logs", tags=["System Logs"])

@router.post("/", response_model=SystemLogRead)
def create_log(log: SystemLogCreate, db: Session = Depends(get_db)):
    db_log = SystemLog(**log.model_dump())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

@router.get("/", response_model=list[SystemLogRead])
def get_logs(db: Session = Depends(get_db)):
    return db.query(SystemLog).all()
