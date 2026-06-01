from collections import Counter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.chat_message import ChatMessage
from models.chat_session import ChatSession
from models.feedback import UserFeedback
from models.manual_intervention import ManualIntervention
from models.system_log import SystemLog
from models.text_feedback import UserTextFeedback
from utils.llm_client import generate_response

router = APIRouter(prefix="/admin", tags=["admin"])


def _top_items(values: list[str], n: int = 6) -> list[dict]:
    clean_values = [v.strip() for v in values if v and v.strip()]
    counter = Counter(clean_values)
    return [{"name": name, "count": count} for name, count in counter.most_common(n)]


@router.get("/analysis-summary")
def get_admin_analysis_summary(db: Session = Depends(get_db)):
    sessions = db.query(ChatSession).all()
    messages = db.query(ChatMessage).all()
    feedbacks = db.query(UserFeedback).all()
    text_feedbacks = db.query(UserTextFeedback).all()
    manual_records = db.query(ManualIntervention).all()

    session_count = len(sessions)
    message_count = len(messages)
    feedback_count = len(feedbacks)
    text_feedback_count = len(text_feedbacks)
    manual_count = len(manual_records)

    user_messages = [m for m in messages if m.role == "user"]
    assistant_messages = [m for m in messages if m.role == "assistant"]
    satisfied_count = sum(1 for f in feedbacks if f.feedback_type == "satisfied")
    unsatisfied_count = sum(1 for f in feedbacks if f.feedback_type == "unsatisfied")

    resolution_rate = round((satisfied_count / feedback_count) * 100, 2) if feedback_count else 0
    top_topics = _top_items([s.conversation_topic for s in sessions])
    top_intents = _top_items([s.user_intent for s in sessions])
    manual_reasons = _top_items([m.transfer_reason for m in manual_records])
    recent_text_feedbacks = [
        {
            "id": f.id,
            "content": (f.content or "").strip()[:180],
            "status": f.status,
            "source": f.source,
        }
        for f in sorted(text_feedbacks, key=lambda x: x.id, reverse=True)[:20]
    ]

    snapshot = {
        "session_count": session_count,
        "message_count": message_count,
        "feedback_count": feedback_count,
        "text_feedback_count": text_feedback_count,
        "manual_intervention_count": manual_count,
        "user_message_count": len(user_messages),
        "assistant_message_count": len(assistant_messages),
        "satisfied_count": satisfied_count,
        "unsatisfied_count": unsatisfied_count,
        "resolution_rate": resolution_rate,
        "top_topics": top_topics,
        "top_intents": top_intents,
        "top_manual_reasons": manual_reasons,
        "recent_text_feedbacks": recent_text_feedbacks,
    }

    prompt = (
        "你是电商商户运营分析顾问。请基于下面的数据输出中文综合运营分析，面向商户的商品与服务运营优化，"
        "不要对客服系统本身提出改造建议。\n"
        "输出要求：\n"
        "1) 使用分点叙述，必须输出4-6个要点；\n"
        "2) 每个要点都以“1. / 2. / 3.”编号开头，避免大段自然段；\n"
        "3) 必须覆盖：用户咨询主题与意图、满意度与转化风险、用户反馈内容洞察、面向商户产品/服务的改进建议；\n"
        "4) 建议必须聚焦商户提供的商品、履约、售后、说明信息、营销策略，不要建议“优化本系统/模型/机器人”。\n\n"
        f"系统数据快照：{snapshot}"
    )

    llm_summary = generate_response(prompt)

    db.add(
        SystemLog(
            level="INFO",
            message=(
                "Admin analysis summary generated: "
                f"sessions={session_count}, messages={message_count}, feedbacks={feedback_count}"
            ),
        )
    )
    db.commit()

    return {
        "summary": llm_summary,
        "snapshot": snapshot,
    }
