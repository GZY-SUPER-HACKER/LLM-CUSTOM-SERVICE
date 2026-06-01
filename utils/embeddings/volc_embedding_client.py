from volcenginesdkarkruntime import Ark
import os

client = Ark()
EMBED_MODEL = "ep-20260111160402-fxzwt"

def get_text_embedding(text: str) -> list[float]:
    try:
        result = client.multimodal_embeddings.create(
            model=EMBED_MODEL,
            input=[
                {
                    "type": "text",
                    "text": text
                }
            ]
        )

        # 检查 result.data 的实际结构
        # print(result)  # 打印出返回的结构以便调试

        # 根据返回结果的实际结构修改访问方式
        if isinstance(result.data, list) and len(result.data) > 0:
            return result.data[0].embedding  # 假设是一个对象，可以通过属性访问
        else:
            return [0.0] * 384  # 默认返回空向量（根据向量维度调整）

    except Exception as e:
        print(f"[Embedding Error] {e}, request_id: {getattr(e, 'request_id', 'unknown')}")
        return [0.0] * 384  # 备用空向量
