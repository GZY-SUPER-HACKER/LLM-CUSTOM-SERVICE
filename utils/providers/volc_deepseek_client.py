from volcenginesdkarkruntime import Ark
from config import get_volc_model_id

# 模型配置（从环境变量 VOLC_MODEL_ID 读取）
MODEL_ID = get_volc_model_id()

# 如果环境变量中配置了 VOLC_ACCESSKEY / VOLC_SECRETKEY 会自动读取
# 否则可以手动传入：
# client = Ark(ak="your_ak", sk="your_sk")
client = Ark()

def chat_with_deepseek(user_input: str) -> str:
    """
    使用火山引擎 DeepSeek 模型生成回复
    """
    try:
        completion = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "user", "content": user_input},
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"[DeepSeek Error] {e}")
        return "抱歉，我暂时无法回答这个问题。"
