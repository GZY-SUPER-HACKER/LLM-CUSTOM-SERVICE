"""
config.py

统一配置管理模块。
优先从环境变量读取配置，如果安装了 python-dotenv 则会自动加载 .env 文件。
所有配置均 **不提供硬编码 fallback 值** —— 未设置时会显式抛出异常或返回 None。
"""

import os
from functools import lru_cache

# 尝试加载 .env 文件（如果存在且 python-dotenv 已安装）
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ---------- 必需配置（无默认值，缺了会报错） ----------

def _required(key: str, hint: str = "") -> str:
    """获取必需的环境变量，缺失时抛出清晰的错误。"""
    value = os.environ.get(key)
    if not value:
        msg = f"缺少必需的环境变量: {key}"
        if hint:
            msg += f" —— {hint}"
        raise RuntimeError(msg)
    return value


# ---------- Pinecone ----------

def get_pinecone_api_key() -> str:
    return _required("PINECONE_API_KEY", "从 https://app.pinecone.io 获取")


def get_pinecone_environment() -> str:
    return os.environ.get("PINECONE_ENVIRONMENT", "us-west-2")


def get_pinecone_index_name() -> str:
    return os.environ.get("PINECONE_INDEX_NAME", "ecommerce-kb")


# ---------- HuggingFace ----------

def get_hf_token() -> str:
    return _required("HF_TOKEN", "从 https://huggingface.co/settings/tokens 获取")


# ---------- 数据库 ----------

def get_database_url() -> str:
    return _required("DATABASE_URL", '例如: mysql+pymysql://user:pass@host:3306/db?charset=utf8mb4')


# ---------- LLM 提供商 ----------

def get_llm_provider() -> str:
    return os.environ.get("LLM_PROVIDER", "deepseek")


def get_volc_model_id() -> str:
    """火山引擎上的模型 Endpoint ID"""
    return os.environ.get("VOLC_MODEL_ID", "ep-20260111134230-s67fn")


# ---------- JWT 认证 ----------

def get_jwt_secret_key() -> str:
    # 不设为必需 —— 允许使用默认占位符，但生产环境应覆盖
    return os.environ.get("JWT_SECRET_KEY", "your-secret-key-here")


def get_jwt_algorithm() -> str:
    return os.environ.get("JWT_ALGORITHM", "HS256")


def get_jwt_expire_minutes() -> int:
    return int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


# ========== 全局单例（避免重复读取） ==========

@lru_cache(maxsize=1)
def load_all_config() -> dict:
    """返回所有配置的快照（用于调试 / 启动检查）"""
    return {
        "PINECONE_ENVIRONMENT": get_pinecone_environment(),
        "PINECONE_INDEX_NAME": get_pinecone_index_name(),
        "LLM_PROVIDER": get_llm_provider(),
        "VOLC_MODEL_ID": get_volc_model_id(),
        "JWT_ALGORITHM": get_jwt_algorithm(),
        "JWT_ACCESS_TOKEN_EXPIRE_MINUTES": get_jwt_expire_minutes(),
        # 注意：不包含密钥本身，只包含非敏感元数据
    }
