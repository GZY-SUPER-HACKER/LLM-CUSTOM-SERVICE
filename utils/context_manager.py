import re
from typing import Dict, Tuple, Optional
from utils.llm_client import generate_response
from utils.classifier import HybridClassifier, ClassificationResult, ConfidenceLevel
from utils.emotion_recognizer import EmotionRecognizer, EmotionResult

class ContextManager:
    _classifier = None
    _emotion_recognizer = None

    @classmethod
    def get_classifier(cls) -> HybridClassifier:
        if cls._classifier is None:
            cls._classifier = HybridClassifier()
        return cls._classifier

    @classmethod
    def get_emotion_recognizer(cls) -> EmotionRecognizer:
        if cls._emotion_recognizer is None:
            cls._emotion_recognizer = EmotionRecognizer()
        return cls._emotion_recognizer

    @staticmethod
    def classify_intent(user_input: str) -> Tuple[str, ClassificationResult]:
        classifier = ContextManager.get_classifier()
        result = classifier.classify(user_input)
        return result.intent_type, result

    @staticmethod
    def recognize_emotion(user_input: str) -> Tuple[str, EmotionResult]:
        recognizer = ContextManager.get_emotion_recognizer()
        result = recognizer.recognize(user_input)
        return result.emotion_type, result

    @staticmethod
    def should_transfer_human(user_input: str) -> Tuple[bool, str]:
        _, intent_result = ContextManager.classify_intent(user_input)
        _, emotion_result = ContextManager.recognize_emotion(user_input)

        if intent_result.intent_type == "transfer_human":
            return True, "用户明确请求转人工"

        should_transfer, emotion_suggestion = EmotionRecognizer.should_transfer_human(emotion_result)
        if should_transfer:
            return True, emotion_suggestion

        return False, "暂无需转人工"

    @staticmethod
    def extract_topic(history_text: str, user_input: str) -> str:
        product_patterns = [
            r"手机|电脑|平板|耳机|音箱|手表|电视|冰箱|空调|洗衣机",
            r"商品|产品|服务|订单|物流|配送|快递",
            r"价格|费用|退款|退货|维修|售后"
        ]

        combined_text = f"{history_text}\n用户: {user_input}"

        for pattern in product_patterns:
            match = re.search(pattern, combined_text)
            if match:
                return match.group(0)

        prompt = f"""请为以下对话提取一个简洁的主题（不超过10个字）：
{combined_text}"""

        try:
            topic = generate_response(prompt)
            return topic.strip()[:20]
        except:
            return "日常咨询"

    @staticmethod
    def generate_progress_summary(history_text: str, user_input: str, ai_reply: str) -> str:
        combined_text = f"{history_text}\n用户: {user_input}\n助手: {ai_reply}"

        prompt = f"""请为以下对话生成一个简洁的进展摘要（50-100字），包含关键决策点和当前状态：
{combined_text}"""

        try:
            summary = generate_response(prompt)
            summary = summary.strip()
            if len(summary) > 100:
                summary = summary[:97] + "..."
            return summary
        except:
            return "对话进行中，用户咨询相关问题，助手提供了相应回答。"

    @staticmethod
    def build_structured_context(session_data: Dict) -> str:
        topic = session_data.get('conversation_topic', '未设定')
        intent = session_data.get('user_intent', '未分类')
        progress = session_data.get('conversation_progress', '对话开始')
        emotion = session_data.get('user_emotion', '中性')
        confidence = session_data.get('confidence', 0.0)

        structured_context = f"""【对话主题】: {topic}
【用户意图】: {intent}
【用户情绪】: {emotion}
【置信度】: {confidence:.2f}
【对话进展】: {progress}"""

        return structured_context

    @staticmethod
    def update_context(db, session_id: int, user_input: str, ai_reply: str) -> Dict:
        from models.chat_session import ChatSession
        from models.chat_message import ChatMessage

        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            return {}

        previous_messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.id.desc()).limit(5).all()

        history_text = "\n".join(
            [f"{m.role}: {m.content}" for m in reversed(previous_messages)]
        )

        intent, intent_result = ContextManager.classify_intent(user_input)
        emotion, emotion_result = ContextManager.recognize_emotion(user_input)
        topic = ContextManager.extract_topic(history_text, user_input)
        progress = ContextManager.generate_progress_summary(history_text, user_input, ai_reply)

        session.conversation_topic = topic
        session.user_intent = intent
        session.conversation_progress = progress
        db.commit()

        return {
            'conversation_topic': topic,
            'user_intent': intent,
            'user_intent_type': intent,
            'user_emotion': emotion,
            'intent_confidence': intent_result.confidence,
            'emotion_intensity': emotion_result.intensity,
            'conversation_progress': progress,
            'classification_details': intent_result.to_dict(),
            'emotion_details': emotion_result.to_dict()
        }

    @staticmethod
    def get_statistics() -> Dict:
        classifier = ContextManager.get_classifier()
        recognizer = ContextManager.get_emotion_recognizer()

        return {
            'classifier': classifier.get_statistics(),
            'emotion_recognizer': recognizer.get_statistics()
        }