from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.chat_message import ChatMessage
from models.chat_session import ChatSession
from models.system_log import SystemLog
from schemas.chat_schema import ChatMessageRead, SendMessageRequest
from utils.rag_engine import generate_answer_with_knowledge
from utils.context_manager import ContextManager
from utils.manual_service import ManualService

router = APIRouter(prefix="/chat", tags=["Chat Engine"])

@router.post("/send_message", response_model=list[ChatMessageRead])
def send_message(
    request: SendMessageRequest,
    db: Session = Depends(get_db)
):
    user_id = request.user_id
    user_input = request.user_input
    session_id = request.session_id
    """
    主聊天接口：
    1. 自动检测或创建 chat_session
    2. 保存用户消息
    3. 检查是否需要转人工
    4. 调用 RAG 检索 + LLM 生成回答
    5. 保存 AI 回复
    6. 更新结构化上下文信息
    7. 返回当前会话完整消息记录
    """
    # 1. 如果没有 session_id，或者 session_id 不存在，就创建一个新的会话
    if session_id is None:
        new_session = ChatSession(user_id=user_id)
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        session_id = new_session.id
        db.add(SystemLog(level="INFO", message=f"Chat session created (chat): session_id={session_id}, user_id={user_id}"))
        db.commit()
    else:
        existing_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not existing_session:
            new_session = ChatSession(user_id=user_id)
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            session_id = new_session.id
            db.add(SystemLog(level="INFO", message=f"Chat session created (chat, missing id): session_id={session_id}, user_id={user_id}"))
            db.commit()

    # 2. 保存用户消息
    user_msg = ChatMessage(session_id=session_id, role="user", content=user_input)
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)
    db.add(SystemLog(level="INFO", message=f"User message: session_id={session_id}, message_id={user_msg.id}"))
    db.commit()

    # 3. 检查是否需要转人工
    should_transfer, transfer_reason = ContextManager.should_transfer_human(user_input)
    if should_transfer:
        record = ManualService.create_manual_intervention(db, session_id, transfer_reason)
        if record:
            db.add(SystemLog(level="WARNING", message=f"Transfer to human (auto): session_id={session_id}, record_id={record.id}"))
            db.commit()
        ai_reply = ManualService.get_transfer_response(transfer_reason)
    else:
        # 4. 获取上下文历史（最近 5 条）
        previous_messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.id.desc()).limit(5).all()
        history_text = "\n".join(
            [f"{m.role}: {m.content}" for m in reversed(previous_messages)]
        )

        # 5. 调用 RAG 工作流：知识检索 + LLM 回答
        ai_reply = generate_answer_with_knowledge(user_input, db, history_text, session_id)

    # 6. 保存 AI 回复
    ai_msg = ChatMessage(session_id=session_id, role="assistant", content=ai_reply)
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)
    db.add(SystemLog(level="INFO", message=f"Assistant message: session_id={session_id}, message_id={ai_msg.id}"))
    db.commit()

    # 7. 更新结构化上下文信息
    ContextManager.update_context(db, session_id, user_input, ai_reply)

    # 8. 返回本会话所有消息
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).all()
    return messages
