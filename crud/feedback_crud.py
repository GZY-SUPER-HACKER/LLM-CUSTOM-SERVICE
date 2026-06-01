from sqlalchemy.orm import Session
from models.feedback import UserFeedback
import hashlib

def create_feedback(db: Session, message_id: str, user_id: str, session_id: str, 
                 feedback_type: str, status: str = 'submitted') -> UserFeedback:
    """
    创建用户反馈记录
    
    Args:
        db: 数据库会话
        message_id: 消息ID
        user_id: 用户ID
        session_id: 会话ID
        feedback_type: 反馈类型 ('satisfied' or 'unsatisfied')
        status: 反馈状态
    
    Returns:
        UserFeedback: 创建的反馈记录
    """
    # 对敏感信息进行加密处理
    encrypted_user_id = encrypt_user_id(user_id)
    
    feedback = UserFeedback(
        message_id=message_id,
        user_id=encrypted_user_id,
        session_id=session_id,
        feedback_type=feedback_type,
        status=status
    )
    
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback

def get_feedback_by_message(db: Session, message_id: str) -> UserFeedback:
    """
    根据消息ID获取反馈
    
    Args:
        db: 数据库会话
        message_id: 消息ID
    
    Returns:
        UserFeedback: 反馈记录
    """
    return db.query(UserFeedback).filter(UserFeedback.message_id == message_id).first()

def get_feedbacks_by_user(db: Session, user_id: str, skip: int = 0, limit: int = 100):
    """
    获取用户的所有反馈
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        skip: 跳过的记录数
        limit: 返回的记录数限制
    
    Returns:
        list: 用户反馈列表
    """
    encrypted_user_id = encrypt_user_id(user_id)
    return db.query(UserFeedback).filter(
        UserFeedback.user_id == encrypted_user_id
    ).offset(skip).limit(limit).all()

def update_feedback_status(db: Session, feedback_id: int, status: str) -> UserFeedback:
    """
    更新反馈状态
    
    Args:
        db: 数据库会话
        feedback_id: 反馈ID
        status: 新状态
    
    Returns:
        UserFeedback: 更新后的反馈记录
    """
    feedback = db.query(UserFeedback).filter(UserFeedback.id == feedback_id).first()
    if feedback:
        feedback.status = status
        db.commit()
        db.refresh(feedback)
    return feedback


def get_all_feedbacks(db: Session, skip: int = 0, limit: int = 200) -> list[UserFeedback]:
    return (
        db.query(UserFeedback)
        .order_by(UserFeedback.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def delete_feedback(db: Session, feedback_id: int) -> bool:
    feedback = db.query(UserFeedback).filter(UserFeedback.id == feedback_id).first()
    if not feedback:
        return False
    db.delete(feedback)
    db.commit()
    return True

def encrypt_user_id(user_id: str) -> str:
    """
    对用户ID进行加密处理
    
    Args:
        user_id: 原始用户ID
    
    Returns:
        str: 加密后的用户ID
    """
    # 使用SHA-256哈希进行简单的加密处理
    # 在实际应用中，应使用更安全的加密方法
    return hashlib.sha256(user_id.encode()).hexdigest()