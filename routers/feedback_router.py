from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from crud.feedback_crud import (
    create_feedback,
    get_feedback_by_message,
    update_feedback_status,
    get_all_feedbacks,
    delete_feedback,
)
from models.system_log import SystemLog
from models.text_feedback import UserTextFeedback
from schemas.feedback_schema import (
    FeedbackCreate,
    FeedbackResponse,
    FeedbackStatusUpdate,
    TextFeedbackCreate,
    TextFeedbackResponse,
)

router = APIRouter(prefix="/feedback", tags=["feedback"])

@router.post("/", response_model=FeedbackResponse)
async def submit_feedback(
    feedback: FeedbackCreate,
    db: Session = Depends(get_db)
):
    """
    提交用户反馈
    
    Args:
        feedback: 反馈数据
        db: 数据库会话
    
    Returns:
        FeedbackResponse: 创建的反馈记录
    
    Raises:
        HTTPException: 当反馈创建失败时
    """
    try:
        # 创建反馈记录
        db_feedback = create_feedback(
            db=db,
            message_id=feedback.message_id,
            user_id=feedback.user_id,
            session_id=feedback.session_id,
            feedback_type=feedback.feedback_type,
            status=feedback.status
        )

        # 写入系统日志（真实数据）
        db.add(SystemLog(level="INFO", message=f"New feedback submitted: feedback_id={db_feedback.id}, message_id={db_feedback.message_id}"))
        db.commit()
        
        return FeedbackResponse(
            id=db_feedback.id,
            message_id=db_feedback.message_id,
            user_id=db_feedback.user_id,
            session_id=db_feedback.session_id,
            feedback_type=db_feedback.feedback_type,
            timestamp=db_feedback.timestamp,
            status=db_feedback.status,
            feedback_source='chat_reaction'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"反馈提交失败: {str(e)}")


@router.get("/", response_model=list[FeedbackResponse])
async def list_feedbacks(
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    feedbacks = get_all_feedbacks(db=db, skip=skip, limit=limit)
    return [
        FeedbackResponse(
            id=f.id,
            message_id=f.message_id,
            user_id=f.user_id,
            session_id=f.session_id,
            feedback_type=f.feedback_type,
            timestamp=f.timestamp,
            status=f.status,
            feedback_source='chat_reaction',
        )
        for f in feedbacks
    ]

@router.get("/message/{message_id}", response_model=FeedbackResponse)
async def get_feedback(
    message_id: str,
    db: Session = Depends(get_db)
):
    """
    获取指定消息的反馈
    
    Args:
        message_id: 消息ID
        db: 数据库会话
    
    Returns:
        FeedbackResponse: 反馈记录
    
    Raises:
        HTTPException: 当反馈不存在时
    """
    feedback = get_feedback_by_message(db=db, message_id=message_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="反馈记录不存在")
    
    return FeedbackResponse(
        id=feedback.id,
        message_id=feedback.message_id,
        user_id=feedback.user_id,
        session_id=feedback.session_id,
        feedback_type=feedback.feedback_type,
        timestamp=feedback.timestamp,
        status=feedback.status,
        feedback_source='chat_reaction'
    )

@router.put("/{feedback_id}/status")
async def update_feedback(
    feedback_id: int,
    payload: FeedbackStatusUpdate,
    db: Session = Depends(get_db)
):
    """
    更新反馈状态
    
    Args:
        feedback_id: 反馈ID
        status: 新状态
        db: 数据库会话
    
    Returns:
        dict: 更新结果
    
    Raises:
        HTTPException: 当反馈不存在时
    """
    feedback = update_feedback_status(db=db, feedback_id=feedback_id, status=payload.status)
    if not feedback:
        raise HTTPException(status_code=404, detail="反馈记录不存在")
    
    db.add(SystemLog(level="INFO", message=f"Feedback status updated: feedback_id={feedback_id}, status={payload.status}"))
    db.commit()
    return {"message": "反馈状态更新成功", "status": payload.status}


@router.delete("/{feedback_id}")
async def remove_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
):
    ok = delete_feedback(db=db, feedback_id=feedback_id)
    if not ok:
        raise HTTPException(status_code=404, detail="反馈记录不存在")
    db.add(SystemLog(level="WARNING", message=f"Feedback deleted: feedback_id={feedback_id}"))
    db.commit()
    return {"message": "反馈删除成功"}


@router.post("/text", response_model=TextFeedbackResponse)
async def submit_text_feedback(
    payload: TextFeedbackCreate,
    db: Session = Depends(get_db)
):
    content = (payload.content or '').strip()
    if not content:
        raise HTTPException(status_code=400, detail="反馈内容不能为空")

    row = UserTextFeedback(
        user_id=payload.user_id,
        session_id=payload.session_id,
        content=content,
        source='manual_text',
        status=payload.status or 'submitted'
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    db.add(SystemLog(level="INFO", message=f"Text feedback submitted: text_feedback_id={row.id}, user_id={row.user_id}"))
    db.commit()

    return TextFeedbackResponse(
        id=row.id,
        user_id=row.user_id,
        session_id=row.session_id,
        content=row.content,
        source=row.source,
        timestamp=row.timestamp,
        status=row.status,
    )


@router.get("/text", response_model=list[TextFeedbackResponse])
async def list_text_feedbacks(
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(UserTextFeedback)
        .order_by(UserTextFeedback.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        TextFeedbackResponse(
            id=r.id,
            user_id=r.user_id,
            session_id=r.session_id,
            content=r.content,
            source=r.source,
            timestamp=r.timestamp,
            status=r.status,
        )
        for r in rows
    ]


@router.delete("/text/{feedback_id}")
async def remove_text_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
):
    row = db.query(UserTextFeedback).filter(UserTextFeedback.id == feedback_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="文本反馈不存在")
    db.delete(row)
    db.commit()
    db.add(SystemLog(level="WARNING", message=f"Text feedback deleted: text_feedback_id={feedback_id}"))
    db.commit()
    return {"message": "文本反馈删除成功"}