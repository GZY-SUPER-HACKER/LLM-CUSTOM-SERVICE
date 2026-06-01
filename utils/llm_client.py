import os
from utils.providers.volc_deepseek_client import chat_with_deepseek

# 可选：将 provider 配置写入环境变量，例如 "deepseek" / "openai" / "qwen"
PROVIDER = os.getenv("LLM_PROVIDER", "deepseek")

def generate_response(user_input: str) -> str:
    """
    通用统一接口：根据 PROVIDER 自动调用不同 LLM
    """
    if PROVIDER == "deepseek":
        return chat_with_deepseek(user_input)

    # # 为后续兼容其他模型留接口
    # elif PROVIDER == "openai":
    #     from utils.providers.openai_client import chat_with_openai
    #     return chat_with_openai(user_input)
    #
    # elif PROVIDER == "qwen":
    #     from utils.providers.qwen_client import chat_with_qwen
    #     return chat_with_qwen(user_input)

    else:
        raise ValueError(f"未知的模型提供商: {PROVIDER}")
