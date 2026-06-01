from sqlalchemy.orm import Session
from models.manual_intervention import ManualIntervention
from models.chat_session import ChatSession
from models.chat_message import ChatMessage
from utils.emotion_recognizer import EmotionRecognizer
from typing import Dict, Optional, Tuple

class ManualService:
    @staticmethod
    def create_manual_intervention(db: Session, session_id: int, transfer_reason: str) -> ManualIntervention:
        """
        创建人工干预记录
        """
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            return None

        emotion_recognizer = EmotionRecognizer()
        session_context = {
            "conversation_topic": session.conversation_topic or "未知",
            "user_intent": session.user_intent or "未知",
            "conversation_progress": session.conversation_progress or "对话进行中"
        }

        last_message = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id,
            ChatMessage.role == "user"
        ).order_by(ChatMessage.id.desc()).first()

        if last_message:
            emotion_result = emotion_recognizer.recognize(last_message.content)
            transfer_info = emotion_recognizer.get_transfer_info(emotion_result, session_context)

            db_record = ManualIntervention(
                session_id=session_id,
                emotion_type=transfer_info["emotion_type"],
                emotion_intensity=transfer_info["intensity"],
                emotion_level=transfer_info["intensity_level"],
                is_emotionally_agitated=transfer_info["is_emotionally_agitated"],
                emotion_confidence=transfer_info["confidence"],
                tone_intensity=transfer_info["multi_dimensional_analysis"].get("tone_intensity"),
                negative_emotion_degree=transfer_info["multi_dimensional_analysis"].get("negative_emotion_degree"),
                urgency_level=transfer_info["multi_dimensional_analysis"].get("urgency_level"),
                loss_of_control_risk=transfer_info["multi_dimensional_analysis"].get("loss_of_control_risk"),
                transfer_reason=transfer_reason,
                conversation_topic=session.conversation_topic,
                user_intent=session.user_intent,
                conversation_progress=session.conversation_progress,
                note=f"情绪识别自动触发转人工 - {transfer_info['suggestion']}"
            )
        else:
            db_record = ManualIntervention(
                session_id=session_id,
                transfer_reason="用户会话无消息记录",
                conversation_topic=session.conversation_topic,
                user_intent=session.user_intent,
                conversation_progress=session.conversation_progress
            )

        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record

    @staticmethod
    def get_transfer_response(transfer_reason: str) -> str:
        """
        获取转人工响应消息
        """
        return f"非常抱歉给您带来不好的体验。{transfer_reason}，我们将为您转接人工客服，请稍候..."
