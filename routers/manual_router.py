from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.manual_intervention import ManualIntervention
from schemas.manual_schema import ManualInterventionCreate, ManualInterventionRead
from utils.manual_service import ManualService
from models.system_log import SystemLog

router = APIRouter(prefix="/manual_interventions", tags=["Manual Interventions"])

@router.post("/", response_model=ManualInterventionRead)
def create_manual_record(record: ManualInterventionCreate, db: Session = Depends(get_db)):
    db_record = ManualIntervention(**record.model_dump())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    db.add(SystemLog(level="WARNING", message=f"Manual intervention created: session_id={db_record.session_id}, record_id={db_record.id}"))
    db.commit()
    return db_record

@router.get("/", response_model=list[ManualInterventionRead])
def get_manual_records(db: Session = Depends(get_db)):
    return db.query(ManualIntervention).all()

@router.post("/transfer_with_emotion/{session_id}", response_model=ManualInterventionRead)
def transfer_to_human_with_emotion(session_id: int, db: Session = Depends(get_db)):
    record = ManualService.create_manual_intervention(db, session_id, "用户手动请求转人工")
    if record:
        db.add(SystemLog(level="WARNING", message=f"Transfer to human triggered: session_id={session_id}, record_id={record.id}"))
        db.commit()
    return record


@router.get("/session/{session_id}", response_model=list[ManualInterventionRead])
def get_manual_records_by_session(session_id: int, db: Session = Depends(get_db)):
    return (
        db.query(ManualIntervention)
        .filter(ManualIntervention.session_id == session_id)
        .order_by(ManualIntervention.created_at.asc())
        .all()
    )