from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from utils.llm_client import generate_response

class EmotionType(Enum):
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SATISFIED = "satisfied"
    ANGRY = "angry"
    FRUSTRATED = "frustrated"
    ANXIOUS = "anxious"
    SAD = "sad"
    DISAPPOINTED = "disappointed"
    SURPRISED = "surprised"
    CONFUSED = "confused"
    EMOTIONALLY_AGITATED = "emotionally_agitated"

class EmotionIntensity(Enum):
    MILD = (0.0, 0.3, "轻微")
    MODERATE = (0.3, 0.6, "中等")
    STRONG = (0.6, 0.8, "强烈")
    EXTREME = (0.8, 1.0, "极端")

    def __init__(self, min_val: float, max_val: float, description: str):
        self.min_val = min_val
        self.max_val = max_val
        self.description = description

    @classmethod
    def from_score(cls, score: float) -> 'EmotionIntensity':
        for level in cls:
            if level.min_val <= score <= level.max_val:
                return level
        return cls.MODERATE

@dataclass
class EmotionResult:
    emotion_type: str
    intensity: float
    intensity_level: EmotionIntensity
    method: str
    matched_patterns: List[str]
    confidence: float
    suggestion: str
    is_emotionally_agitated: bool
    multi_dimensional_analysis: Dict

    def to_dict(self) -> dict:
        return {
            "emotion_type": self.emotion_type,
            "intensity": self.intensity,
            "intensity_level": self.intensity_level.description,
            "method": self.method,
            "matched_patterns": self.matched_patterns,
            "confidence": self.confidence,
            "suggestion": self.suggestion,
            "is_emotionally_agitated": self.is_emotionally_agitated,
            "multi_dimensional_analysis": self.multi_dimensional_analysis
        }

class EmotionRecognizer:
    EMOTION_KEYWORDS = {
        "angry": ["愤怒", "生气", "气愤", "恼火", "发火", "怒", "不爽"],
        "frustrated": ["失望", "绝望", "无奈", "受挫", "挫败", "沮丧"],
        "disappointed": ["失望", "不满", "失望透顶", "后悔"],
        "confused": ["困惑", "疑惑", "不懂", "不明白", "糊涂"],
        "anxious": ["焦虑", "担忧", "着急", "紧张", "不安", "慌"],
        "sad": ["悲伤", "难过", "伤心", "痛苦", "沮丧"],
        "happy": ["开心", "高兴", "满意", "愉快", "兴奋"],
        "satisfied": ["满意", "满足", "认可", "赞"],
        "surprised": ["惊讶", "意外", "吃惊", "震惊"],
    }

    def __init__(self):
        self.recognition_cache: Dict[str, EmotionResult] = {}
        self.max_cache_size = 1000
        self.emotionally_agitated_threshold = 0.6

    def recognize(self, user_input: str, use_cache: bool = True) -> EmotionResult:
        if use_cache and user_input in self.recognition_cache:
            return self.recognition_cache[user_input]

        emotion_result = self._llm_based_recognize(user_input)

        if len(self.recognition_cache) >= self.max_cache_size:
            oldest_key = next(iter(self.recognition_cache))
            del self.recognition_cache[oldest_key]

        self.recognition_cache[user_input] = emotion_result
        return emotion_result

    def _llm_based_recognize(self, user_input: str) -> EmotionResult:
        try:
            emotion_data = self._call_llm_recognizer(user_input)
            emotion_type = emotion_data.get("emotion_type", "neutral")
            intensity = emotion_data.get("intensity", 0.0)
            suggestion = emotion_data.get("suggestion", "正常处理")
            multi_dimensional = emotion_data.get("multi_dimensional_analysis", {})
            is_agitated = emotion_data.get("is_emotionally_agitated", False)

            if isinstance(emotion_type, str):
                emotion_type_lower = emotion_type.lower()
                for key in ["angry", "frustrated", "disappointed", "anxious", "confused", "sad"]:
                    if key in emotion_type_lower:
                        emotion_type = key
                        break

            intensity_level = EmotionIntensity.from_score(intensity)

            return EmotionResult(
                emotion_type=emotion_type,
                intensity=intensity,
                intensity_level=intensity_level,
                method="llm_based",
                matched_patterns=[],
                confidence=0.90,
                suggestion=suggestion,
                is_emotionally_agitated=is_agitated,
                multi_dimensional_analysis=multi_dimensional
            )
        except Exception as e:
            return self._default_result()

    def _call_llm_recognizer(self, user_input: str) -> dict:
        prompt = f"""请对以下用户输入进行多维度情绪分析：

用户输入：{user_input}

请从以下维度进行评估：
1. 主要情绪类型：愤怒(angry)、沮丧(frustrated)、失望(disappointed)、困惑(confused)、焦虑(anxious)、悲伤(sad)、开心(happy)、满意(satisfied)、惊讶(surprised)、中性(neutral)
2. 情绪强度：0.0-1.0之间的数值（0.0最轻微，1.0最强烈）
3. 是否情绪激动：boolean值，当用户表现出强烈的负面情绪（如愤怒、沮丧、失望等）且强度>=0.6时为true
4. 情绪激动维度分析：
   - 语气激烈程度（0.0-1.0）：用户语气是否激烈、强硬
   - 负面情绪程度（0.0-1.0）：负面情绪的强烈程度
   - 诉求紧急程度（0.0-1.0）：用户是否表现出需要立即处理的紧迫感
   - 失控风险（0.0-1.0）：情绪失控或矛盾升级的可能性
5. 建议的处理方式

请返回严格的JSON格式（不要添加任何markdown代码块标记）：
{{
    "emotion_type": "情绪类型英文",
    "intensity": 0.0-1.0的数值,
    "is_emotionally_agitated": true或false,
    "multi_dimensional_analysis": {{
        "tone_intensity": 0.0-1.0,
        "negative_emotion_degree": 0.0-1.0,
        "urgency_level": 0.0-1.0,
        "loss_of_control_risk": 0.0-1.0
    }},
    "suggestion": "处理建议"
}}

只返回JSON，不要其他内容："""

        response = generate_response(prompt)
        response = response.strip()

        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]

        import json
        try:
            result = json.loads(response)
            return result
        except:
            return self._fallback_analysis(user_input)

    def _fallback_analysis(self, user_input: str) -> dict:
        intensity = 0.1
        emotion_type = "neutral"
        is_agitated = False

        for emotion, keywords in self.EMOTION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in user_input:
                    intensity = max(intensity, 0.5)
                    emotion_type = emotion
                    if intensity >= 0.6:
                        is_agitated = True
                    break

        return {
            "emotion_type": emotion_type,
            "intensity": intensity,
            "is_emotionally_agitated": is_agitated,
            "multi_dimensional_analysis": {
                "tone_intensity": intensity * 0.8,
                "negative_emotion_degree": intensity,
                "urgency_level": intensity * 0.5,
                "loss_of_control_risk": intensity * 0.6
            },
            "suggestion": "正常处理" if not is_agitated else "建议转人工处理"
        }

    def _default_result(self) -> EmotionResult:
        return EmotionResult(
            emotion_type="neutral",
            intensity=0.0,
            intensity_level=EmotionIntensity.MILD,
            method="llm_based",
            matched_patterns=[],
            confidence=0.5,
            suggestion="正常处理",
            is_emotionally_agitated=False,
            multi_dimensional_analysis={
                "tone_intensity": 0.0,
                "negative_emotion_degree": 0.0,
                "urgency_level": 0.0,
                "loss_of_control_risk": 0.0
            }
        )

    def recognize_batch(self, inputs: List[str]) -> List[EmotionResult]:
        return [self.recognize(inp, use_cache=True) for inp in inputs]

    def clear_cache(self):
        self.recognition_cache.clear()

    def get_statistics(self) -> dict:
        emotion_stats = {}
        for text, result in self.recognition_cache.items():
            emotion_type = result.emotion_type
            if emotion_type not in emotion_stats:
                emotion_stats[emotion_type] = {"count": 0, "total_intensity": 0}
            emotion_stats[emotion_type]["count"] += 1
            emotion_stats[emotion_type]["total_intensity"] += result.intensity

        for emotion_type in emotion_stats:
            count = emotion_stats[emotion_type]["count"]
            total = emotion_stats[emotion_type]["total_intensity"]
            emotion_stats[emotion_type]["avg_intensity"] = total / count if count > 0 else 0

        return {
            "cache_size": len(self.recognition_cache),
            "emotion_distribution": emotion_stats
        }

    @staticmethod
    def should_transfer_human(emotion_result: EmotionResult) -> Tuple[bool, str]:
        if emotion_result.is_emotionally_agitated:
            return True, "大模型判断用户情绪激动，建议立即转人工处理"

        if emotion_result.emotion_type in ["angry", "frustrated"]:
            if emotion_result.intensity >= 0.8:
                return True, "检测到用户强烈负面情绪，建议立即转人工"

        if emotion_result.emotion_type == "disappointed" and emotion_result.intensity >= 0.85:
            return True, "用户极度失望，建议转人工处理"

        multi_dim = emotion_result.multi_dimensional_analysis
        if multi_dim:
            loss_risk = multi_dim.get("loss_of_control_risk", 0)
            urgency = multi_dim.get("urgency_level", 0)
            tone_intensity = multi_dim.get("tone_intensity", 0)

            if loss_risk >= 0.8 or (urgency >= 0.85 and tone_intensity >= 0.75):
                return True, "多维度分析显示情绪失控风险高，建议立即转人工"

        return False, "暂无需转人工"

    def get_transfer_info(self, emotion_result: EmotionResult, session_context: Dict = None) -> Dict:
        return {
            "should_transfer": self.should_transfer_human(emotion_result)[0],
            "reason": self.should_transfer_human(emotion_result)[1],
            "emotion_type": emotion_result.emotion_type,
            "intensity": emotion_result.intensity,
            "intensity_level": emotion_result.intensity_level.description,
            "is_emotionally_agitated": emotion_result.is_emotionally_agitated,
            "confidence": emotion_result.confidence,
            "multi_dimensional_analysis": emotion_result.multi_dimensional_analysis,
            "session_context": session_context or {},
            "suggestion": emotion_result.suggestion
        }