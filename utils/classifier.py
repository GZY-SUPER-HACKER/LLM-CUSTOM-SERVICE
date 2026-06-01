from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from utils.rule_manager import RuleManager, Rule
from utils.llm_client import generate_response
import re

class ConfidenceLevel(Enum):
    VERY_HIGH = (0.95, 1.0, "非常确定")
    HIGH = (0.85, 0.95, "确定")
    MEDIUM = (0.70, 0.85, "较确定")
    LOW = (0.50, 0.70, "不确定")
    VERY_LOW = (0.0, 0.50, "很不确定")

    def __init__(self, min_val: float, max_val: float, description: str):
        self.min_val = min_val
        self.max_val = max_val
        self.description = description

    @classmethod
    def from_score(cls, score: float) -> 'ConfidenceLevel':
        for level in cls:
            if level.min_val <= score <= level.max_val:
                return level
        return cls.VERY_LOW

@dataclass
class ClassificationResult:
    intent_type: str
    confidence: float
    confidence_level: ConfidenceLevel
    method: str
    matched_rules: List[str]
    verification_passed: bool
    verification_details: str
    alternative_results: List[Dict] = None

    def to_dict(self) -> dict:
        return {
            "intent_type": self.intent_type,
            "confidence": self.confidence,
            "confidence_level": self.confidence_level.description,
            "method": self.method,
            "matched_rules": self.matched_rules,
            "verification_passed": self.verification_passed,
            "verification_details": self.verification_details,
            "alternative_results": self.alternative_results or []
        }

class HybridClassifier:
    RULE_BASED_INTENTS = [
        "consultation",
        "after_sales",
        "info_query",
        "transfer_human",
        "complaint"
    ]

    LLM_BASED_INTENTS = [
        "technical_support",
        "product_suggestion",
        "chitchat",
        "other"
    ]

    HIGH_PRIORITY_INTENTS = ["transfer_human", "complaint", "after_sales"]

    def __init__(self):
        self.rule_manager = RuleManager()
        self.classification_cache: Dict[str, ClassificationResult] = {}
        self.max_cache_size = 1000
        self.llm_fallback_enabled = True
        self.verification_enabled = True

    def classify(self, user_input: str, use_cache: bool = True) -> ClassificationResult:
        if use_cache and user_input in self.classification_cache:
            return self.classification_cache[user_input]

        matched_rule = self._rule_based_match(user_input)

        if matched_rule:
            result = self._create_rule_based_result(user_input, matched_rule)
        else:
            result = self._llm_based_classify(user_input)

        if len(self.classification_cache) >= self.max_cache_size:
            oldest_key = next(iter(self.classification_cache))
            del self.classification_cache[oldest_key]

        self.classification_cache[user_input] = result
        return result

    def _rule_based_match(self, user_input: str) -> Optional[Tuple[Rule, List[str]]]:
        all_matches = self.rule_manager.match(user_input)

        if not all_matches:
            return None

        matched_rules = []
        for rule, priority in all_matches:
            matched_rules.append(rule.rule_id)

        return (all_matches[0][0], matched_rules)

    def _create_rule_based_result(
        self,
        user_input: str,
        matched: Tuple[Rule, List[str]]
    ) -> ClassificationResult:
        rule, matched_rules = matched

        confidence = self._calculate_rule_confidence(rule, matched_rules)

        if self.verification_enabled:
            verification_passed, verification_details = self._verify_result(
                user_input, rule.intent_type, "rule"
            )
        else:
            verification_passed, verification_details = True, "验证已禁用"

        alternative_results = self._get_alternative_results(matched_rules)

        return ClassificationResult(
            intent_type=rule.intent_type,
            confidence=confidence,
            confidence_level=ConfidenceLevel.from_score(confidence),
            method="rule_based",
            matched_rules=matched_rules,
            verification_passed=verification_passed,
            verification_details=verification_details,
            alternative_results=alternative_results
        )

    def _calculate_rule_confidence(self, rule: Rule, all_matched_rules: List[str]) -> float:
        base_confidence = 0.75

        if rule.priority == 3:
            base_confidence += 0.10
        elif rule.priority == 2:
            base_confidence += 0.05

        match_bonus = min(len(all_matched_rules) * 0.03, 0.10)
        base_confidence += match_bonus

        if rule.intent_type in self.HIGH_PRIORITY_INTENTS:
            base_confidence += 0.05

        return min(base_confidence, 0.95)

    def _llm_based_classify(self, user_input: str) -> ClassificationResult:
        if not self.llm_fallback_enabled:
            return ClassificationResult(
                intent_type="other",
                confidence=0.5,
                confidence_level=ConfidenceLevel.from_score(0.5),
                method="default",
                matched_rules=[],
                verification_passed=False,
                verification_details="LLM分类已禁用，使用默认分类"
            )

        try:
            intent_type = self._call_llm_classifier(user_input)
            confidence = 0.85

            if self.verification_enabled:
                verification_passed, verification_details = self._verify_result(
                    user_input, intent_type, "llm"
                )
            else:
                verification_passed, verification_details = True, "验证已禁用"

            return ClassificationResult(
                intent_type=intent_type,
                confidence=confidence,
                confidence_level=ConfidenceLevel.from_score(confidence),
                method="llm_based",
                matched_rules=[],
                verification_passed=verification_passed,
                verification_details=verification_details
            )
        except Exception as e:
            return ClassificationResult(
                intent_type="other",
                confidence=0.4,
                confidence_level=ConfidenceLevel.VERY_LOW,
                method="fallback",
                matched_rules=[],
                verification_passed=False,
                verification_details=f"LLM分类失败: {str(e)}"
            )

    def _call_llm_classifier(self, user_input: str) -> str:
        prompt = f"""请分析以下用户输入的意图类别，从以下类别中选择最匹配的一个：
- technical_support: 技术支持类，需要技术帮助、安装指导、配置支持等
- product_suggestion: 产品建议类，提出改进意见、功能建议等
- chitchat: 闲聊类，问候、寒暄等非业务对话
- other: 其他类型，无法明确归类

用户输入：{user_input}

请只返回类别名称（technical_support/product_suggestion/chitchat/other），不要其他内容："""

        response = generate_response(prompt)
        response = response.strip().lower()

        valid_intents = ["technical_support", "product_suggestion", "chitchat", "other"]
        if response not in valid_intents:
            return "other"

        return response

    def _verify_result(
        self,
        user_input: str,
        intent_type: str,
        method: str
    ) -> Tuple[bool, str]:
        verification_prompt = f"""请判断以下用户输入的意图分类是否正确：

用户输入：{user_input}
分类结果：{intent_type}

请判断这个分类是否合理，返回"是"或"否"，只返回一个字符："""

        try:
            response = generate_response(verification_prompt)
            response = response.strip()

            if "是" in response:
                return True, "分类结果已通过验证"
            elif "否" in response:
                return False, "分类结果未通过验证，建议重新分类"
            else:
                return True, "验证结果不确定"
        except Exception as e:
            return True, f"验证过程出现异常: {str(e)}"

    def _get_alternative_results(self, matched_rules: List[str]) -> List[Dict]:
        alternatives = []
        for rule_id in matched_rules[1:4]:
            for intent_type, rules in self.rule_manager.rules.items():
                for rule in rules:
                    if rule.rule_id == rule_id:
                        alternatives.append({
                            "intent_type": intent_type,
                            "rule_id": rule_id,
                            "confidence": 0.6
                        })
                        break
        return alternatives

    def classify_batch(self, inputs: List[str]) -> List[ClassificationResult]:
        return [self.classify(inp, use_cache=True) for inp in inputs]

    def clear_cache(self):
        self.classification_cache.clear()

    def get_statistics(self) -> dict:
        return {
            "cache_size": len(self.classification_cache),
            "max_cache_size": self.max_cache_size,
            "rule_count": sum(len(rules) for rules in self.rule_manager.rules.values()),
            "rule_statistics": self.rule_manager.get_statistics()
        }

    def update_rule(
        self,
        intent_type: str,
        rule_id: str,
        updates: dict
    ) -> bool:
        return self.rule_manager.update_rule(intent_type, rule_id, updates)

    def add_rule(self, intent_type: str, rule: Rule) -> bool:
        return self.rule_manager.add_rule(intent_type, rule)

    def remove_rule(self, intent_type: str, rule_id: str) -> bool:
        return self.rule_manager.remove_rule(intent_type, rule_id)