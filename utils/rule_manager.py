import re
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum

class IntentType(Enum):
    CONSULTATION = "consultation"
    AFTER_SALES = "after_sales"
    INFO_QUERY = "info_query"
    TRANSFER_HUMAN = "transfer_human"
    COMPLAINT = "complaint"
    TECHNICAL_SUPPORT = "technical_support"
    PRODUCT_SUGGESTION = "product_suggestion"
    CHITCHAT = "chitchat"
    OTHER = "other"

class RulePriority(Enum):
    HIGH = 3
    MEDIUM = 2
    LOW = 1

class Rule:
    def __init__(
        self,
        rule_id: str,
        intent_type: str,
        patterns: List[str],
        priority: int = RulePriority.MEDIUM.value,
        description: str = "",
        examples: List[str] = None,
        version: str = "1.0.0"
    ):
        self.rule_id = rule_id
        self.intent_type = intent_type
        self.patterns = [re.compile(p, re.IGNORECASE) for p in patterns]
        self.priority = priority
        self.description = description
        self.examples = examples or []
        self.version = version
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.match_count = 0
        self.success_count = 0

    def match(self, text: str) -> bool:
        for pattern in self.patterns:
            if pattern.search(text):
                self.match_count += 1
                return True
        return False

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "intent_type": self.intent_type,
            "patterns": [p.pattern for p in self.patterns],
            "priority": self.priority,
            "description": self.description,
            "examples": self.examples,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "match_count": self.match_count,
            "success_count": self.success_count
        }

class RuleManager:
    def __init__(self):
        self.rules: Dict[str, List[Rule]] = {}
        self.rule_versions: Dict[str, List[dict]] = {}
        self._initialize_default_rules()

    def _initialize_default_rules(self):
        self._add_consultation_rules()
        self._add_after_sales_rules()
        self._add_info_query_rules()
        self._add_transfer_human_rules()
        self._add_complaint_rules()
        self._add_technical_support_rules()
        self._add_product_suggestion_rules()
        self._add_chitchat_rules()

    def _add_consultation_rules(self):
        consultation_rules = [
            Rule(
                rule_id="consultation_price",
                intent_type="consultation",
                patterns=[
                    r"多少钱|价格|费用|收费|报价|价目表|贵不贵|便宜",
                    r"咨询|了解|想知道|请问|问一下",
                    r"如何|怎样|怎么.*做|.*流程",
                    r"能不能|可以.*吗|是否.*可以"
                ],
                priority=RulePriority.MEDIUM.value,
                description="价格和费用咨询",
                examples=["这个产品多少钱", "请问价格是多少", "怎么收费的"]
            ),
            Rule(
                rule_id="consultation_product",
                intent_type="consultation",
                patterns=[
                    r"功能|特点|特性|规格|参数",
                    r"有什么.*功能|哪些.*特点",
                    r".*是什么|是什么.*东西"
                ],
                priority=RulePriority.MEDIUM.value,
                description="产品功能咨询",
                examples=["这个产品有什么功能", "有哪些特点", "规格参数是什么"]
            ),
            Rule(
                rule_id="consultation_usage",
                intent_type="consultation",
                patterns=[
                    r"如何使用|怎样使用|怎么用",
                    r"使用.*方法|操作.*步骤",
                    r".*教程|.*指南|.*说明"
                ],
                priority=RulePriority.MEDIUM.value,
                description="使用方法咨询",
                examples=["如何使用这个功能", "怎么操作", "有使用教程吗"]
            )
        ]
        self.rules["consultation"] = consultation_rules

    def _add_after_sales_rules(self):
        after_sales_rules = [
            Rule(
                rule_id="aftersales_return",
                intent_type="after_sales",
                patterns=[
                    r"退货|退换|退还|退回",
                    r"七天.*退货|无理由.*退货",
                    r"可以退吗|能退.*吗"
                ],
                priority=RulePriority.HIGH.value,
                description="退货相关",
                examples=["我要退货", "可以七天无理由退货吗", "怎么申请退货"]
            ),
            Rule(
                rule_id="aftersales_refund",
                intent_type="after_sales",
                patterns=[
                    r"退款|退钱|返还|偿还",
                    r"什么时候.*退款|多久.*到账",
                    r"申请退款|退款.*流程"
                ],
                priority=RulePriority.HIGH.value,
                description="退款相关",
                examples=["申请退款", "什么时候能退款", "退款多久到账"]
            ),
            Rule(
                rule_id="aftersales_repair",
                intent_type="after_sales",
                patterns=[
                    r"维修|修理|检修|修复",
                    r"坏了|故障|损坏|出问题",
                    r"报修|申请维修|需要.*修理"
                ],
                priority=RulePriority.HIGH.value,
                description="维修相关",
                examples=["产品坏了怎么维修", "申请维修", "有故障怎么办"]
            ),
            Rule(
                rule_id="aftersales_quality",
                intent_type="after_sales",
                patterns=[
                    r"质量.*问题|质量.*差|质量.*不好",
                    r"瑕疵|缺陷|破损",
                    r"与描述不符|货不对板"
                ],
                priority=RulePriority.HIGH.value,
                description="质量问题",
                examples=["质量有问题", "产品有瑕疵", "和描述不符"]
            )
        ]
        self.rules["after_sales"] = after_sales_rules

    def _add_info_query_rules(self):
        info_query_rules = [
            Rule(
                rule_id="infoquery_order",
                intent_type="info_query",
                patterns=[
                    r"订单.*状态|订单.*查询|查.*订单",
                    r"发货.*没|到哪了|物流.*信息",
                    r"订单号|订单.*编号"
                ],
                priority=RulePriority.HIGH.value,
                description="订单信息查询",
                examples=["查询订单状态", "我的订单到哪了", "订单号是多少"]
            ),
            Rule(
                rule_id="infoquery_account",
                intent_type="info_query",
                patterns=[
                    r"账户.*信息|账号.*资料|个人信息",
                    r"我的.*账户|账户.*余额|积分",
                    r"修改.*信息|更新.*资料"
                ],
                priority=RulePriority.MEDIUM.value,
                description="账户信息查询",
                examples=["查看我的账户信息", "积分有多少", "怎么修改个人信息"]
            ),
            Rule(
                rule_id="infoquery_product",
                intent_type="info_query",
                patterns=[
                    r"产品.*详情|商品.*信息|库存",
                    r"有没有货|还有.*吗|何时.*到货",
                    r"产品.*编号|型号|款式"
                ],
                priority=RulePriority.MEDIUM.value,
                description="产品信息查询",
                examples=["这个产品还有货吗", "产品详情是什么", "库存还剩多少"]
            ),
            Rule(
                rule_id="infoquery_delivery",
                intent_type="info_query",
                patterns=[
                    r"配送.*时间|发货.*时间|什么时候.*发货",
                    r"几天.*到|多久.*送达",
                    r"快递.*单号|物流.*跟踪"
                ],
                priority=RulePriority.MEDIUM.value,
                description="配送信息查询",
                examples=["几天能到", "什么时候发货", "查一下物流"]
            )
        ]
        self.rules["info_query"] = info_query_rules

    def _add_transfer_human_rules(self):
        transfer_human_rules = [
            Rule(
                rule_id="transfer_keyword",
                intent_type="transfer_human",
                patterns=[
                    r"转人工|转客服|人工客服|真人客服",
                    r"我要.*人工|找.*人工|人工.*服务"
                ],
                priority=RulePriority.HIGH.value,
                description="转人工关键词",
                examples=["转人工", "我要人工客服", "找真人服务"]
            ),
            Rule(
                rule_id="transfer_explicit",
                intent_type="transfer_human",
                patterns=[
                    r"你们.*解决不了|处理不了",
                    r"我要投诉|要.*经理|找.*领导",
                    r"机器.*不行|AI.*不行|智能.*不行"
                ],
                priority=RulePriority.HIGH.value,
                description="明确要求转人工",
                examples=["你们处理不了", "我要投诉你们", "机器解决不了我的问题"]
            ),
            Rule(
                rule_id="transfer_repeated",
                intent_type="transfer_human",
                patterns=[
                    r"说了.*遍|已经.*次|反复.*问",
                    r"同一个.*问题|一直.*解决不了",
                    r"很生气|非常.*不满|忍无可忍"
                ],
                priority=RulePriority.HIGH.value,
                description="重复多次未解决",
                examples=["我说了三遍了", "同一个问题一直解决不了", "已经问了很多次"]
            )
        ]
        self.rules["transfer_human"] = transfer_human_rules

    def _add_complaint_rules(self):
        complaint_rules = [
            Rule(
                rule_id="complaint_explicit",
                intent_type="complaint",
                patterns=[
                    r"投诉|举报|控诉",
                    r"非常.*不满|极其.*失望|十分.*气愤",
                    r"太差了|太烂了|垃圾|废物"
                ],
                priority=RulePriority.HIGH.value,
                description="明确投诉表达",
                examples=["我要投诉", "太差了", "非常不满"]
            ),
            Rule(
                rule_id="complaint_implicit",
                intent_type="complaint",
                patterns=[
                    r"失望|气愤|恼火|愤怒",
                    r"很不满意|一点.*不好|完全不.*满意",
                    r".*问题.*解决不了|.*一直.*拖"
                ],
                priority=RulePriority.MEDIUM.value,
                description="隐含投诉表达",
                examples=["很失望", "一直拖", "什么问题都解决不了"]
            ),
            Rule(
                rule_id="complaint_negative",
                intent_type="complaint",
                patterns=[
                    r"讨厌|厌烦|恶心|受不了",
                    r"怎么.*这么.*差|为什么.*这么.*烂",
                    r"再也不.*买|不会.*再.*来"
                ],
                priority=RulePriority.LOW.value,
                description="负面情绪表达",
                examples=["太讨厌了", "怎么这么差", "再也不买了"]
            )
        ]
        self.rules["complaint"] = complaint_rules

    def _add_technical_support_rules(self):
        technical_support_rules = [
            Rule(
                rule_id="tech_installation",
                intent_type="technical_support",
                patterns=[
                    r"安装|装机|部署|搭建",
                    r"怎么安装|如何.*安装|安装.*步骤",
                    r"安装.*不上|安装.*失败|安装.*问题"
                ],
                priority=RulePriority.MEDIUM.value,
                description="安装指导",
                examples=["怎么安装", "安装失败", "需要帮助安装"]
            ),
            Rule(
                rule_id="tech_config",
                intent_type="technical_support",
                patterns=[
                    r"配置|设置|调整|调试",
                    r"如何配置|怎么设置|配置.*参数",
                    r"配置.*不对|设置.*错误|配置.*问题"
                ],
                priority=RulePriority.MEDIUM.value,
                description="配置指导",
                examples=["怎么配置", "配置参数", "设置不对怎么办"]
            ),
            Rule(
                rule_id="tech_error",
                intent_type="technical_support",
                patterns=[
                    r"错误|报错|异常|失败",
                    r".*出错了|.*报错了|.*不正常",
                    r"错误信息|报错.*什么|什么.*错误"
                ],
                priority=RulePriority.MEDIUM.value,
                description="错误处理",
                examples=["系统出错了", "报什么错误", "出现异常怎么办"]
            )
        ]
        self.rules["technical_support"] = technical_support_rules

    def _add_product_suggestion_rules(self):
        product_suggestion_rules = [
            Rule(
                rule_id="suggestion_improve",
                intent_type="product_suggestion",
                patterns=[
                    r"建议|意见|想法|看法",
                    r"希望.*能|希望.*有|希望.*可以",
                    r"改进|优化|改善|提升"
                ],
                priority=RulePriority.MEDIUM.value,
                description="改进建议",
                examples=["建议增加这个功能", "希望能支持", "可以优化一下"]
            ),
            Rule(
                rule_id="suggestion_feedback",
                intent_type="product_suggestion",
                patterns=[
                    r"反馈|反映|报告",
                    r".*问题.*反馈|.*情况.*反映",
                    r"给你们.*建议|提.*意见"
                ],
                priority=RulePriority.MEDIUM.value,
                description="反馈意见",
                examples=["反馈一个问题", "给你们提个建议", "反映个情况"]
            )
        ]
        self.rules["product_suggestion"] = product_suggestion_rules

    def _add_chitchat_rules(self):
        chitchat_rules = [
            Rule(
                rule_id="chitchat_greeting",
                intent_type="chitchat",
                patterns=[
                    r"^你好|^嗨|^哈喽|^hi|^hello",
                    r"早上好|下午好|晚上好",
                    r"在吗|在不在|有人吗"
                ],
                priority=RulePriority.HIGH.value,
                description="问候语",
                examples=["你好", "早上好", "在吗"]
            ),
            Rule(
                rule_id="chitchat_farewell",
                intent_type="chitchat",
                patterns=[
                    r"再见|拜拜|下次见",
                    r"谢谢|感谢|辛苦了",
                    r"好的|知道了|明白了"
                ],
                priority=RulePriority.HIGH.value,
                description="告别语",
                examples=["再见", "谢谢", "好的知道了"]
            ),
            Rule(
                rule_id="chitchat_casual",
                intent_type="chitchat",
                patterns=[
                    r"随便问问|聊聊|随便聊聊",
                    r"天气.*怎么样|今天.*如何",
                    r"你是谁|你会.*什么"
                ],
                priority=RulePriority.LOW.value,
                description="闲聊",
                examples=["随便聊聊", "你是谁啊", "天气怎么样"]
            )
        ]
        self.rules["chitchat"] = chitchat_rules

    def add_rule(self, intent_type: str, rule: Rule) -> bool:
        if intent_type not in self.rules:
            self.rules[intent_type] = []
        self.rules[intent_type].append(rule)
        return True

    def remove_rule(self, intent_type: str, rule_id: str) -> bool:
        if intent_type not in self.rules:
            return False
        self.rules[intent_type] = [r for r in self.rules[intent_type] if r.rule_id != rule_id]
        return True

    def update_rule(self, intent_type: str, rule_id: str, updates: dict) -> bool:
        if intent_type not in self.rules:
            return False
        for rule in self.rules[intent_type]:
            if rule.rule_id == rule_id:
                if "patterns" in updates:
                    rule.patterns = [re.compile(p, re.IGNORECASE) for p in updates["patterns"]]
                if "priority" in updates:
                    rule.priority = updates["priority"]
                if "description" in updates:
                    rule.description = updates["description"]
                if "examples" in updates:
                    rule.examples = updates["examples"]
                rule.version = self._increment_version(rule.version)
                rule.updated_at = datetime.now()
                return True
        return False

    def _increment_version(self, version: str) -> str:
        parts = version.split(".")
        if len(parts) == 3:
            parts[2] = str(int(parts[2]) + 1)
        return ".".join(parts)

    def get_rule(self, intent_type: str, rule_id: str) -> Optional[Rule]:
        if intent_type not in self.rules:
            return None
        for rule in self.rules[intent_type]:
            if rule.rule_id == rule_id:
                return rule
        return None

    def get_all_rules(self, intent_type: str = None) -> Dict[str, List[Rule]]:
        if intent_type:
            return {intent_type: self.rules.get(intent_type, [])}
        return self.rules

    def get_rules_by_intent(self, intent_type: str) -> List[Rule]:
        return self.rules.get(intent_type, [])

    def match(self, text: str, intent_types: List[str] = None) -> List[Tuple[Rule, int]]:
        matches = []
        types_to_check = intent_types if intent_types else list(self.rules.keys())

        for intent_type in types_to_check:
            if intent_type not in self.rules:
                continue
            for rule in self.rules[intent_type]:
                if rule.match(text):
                    matches.append((rule, rule.priority))

        matches.sort(key=lambda x: x[1], reverse=True)
        return matches

    def export_rules(self, intent_type: str = None) -> dict:
        if intent_type:
            return {intent_type: [r.to_dict() for r in self.rules.get(intent_type, [])]}
        return {k: [r.to_dict() for r in v] for k, v in self.rules.items()}

    def import_rules(self, rules_data: dict) -> bool:
        try:
            for intent_type, rules_list in rules_data.items():
                self.rules[intent_type] = []
                for rule_dict in rules_list:
                    rule = Rule(
                        rule_id=rule_dict["rule_id"],
                        intent_type=rule_dict["intent_type"],
                        patterns=rule_dict["patterns"],
                        priority=rule_dict.get("priority", RulePriority.MEDIUM.value),
                        description=rule_dict.get("description", ""),
                        examples=rule_dict.get("examples", []),
                        version=rule_dict.get("version", "1.0.0")
                    )
                    self.rules[intent_type].append(rule)
            return True
        except Exception:
            return False

    def get_statistics(self) -> dict:
        stats = {}
        for intent_type, rules in self.rules.items():
            stats[intent_type] = {
                "rule_count": len(rules),
                "total_matches": sum(r.match_count for r in rules),
                "total_successes": sum(r.success_count for r in rules),
                "rules": [r.to_dict() for r in rules]
            }
        return stats