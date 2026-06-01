import os
import numpy as np
from pinecone import Pinecone
from models.knowledge_doc import KnowledgeDoc
from utils.llm_client import generate_response
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
from utils.context_manager import ContextManager
from config import get_hf_token, get_pinecone_api_key, get_pinecone_environment, get_pinecone_index_name

os.environ["HF_TOKEN"] = get_hf_token()
# 全局配置
INDEX_NAME = get_pinecone_index_name()
EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
PINECONE_API_KEY = get_pinecone_api_key()
PINECONE_ENVIRONMENT = get_pinecone_environment()

# 1️⃣ 初始化 embedding 模型（与 test_pinecone 用到的模型保持一致）
_embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

# 2️⃣ 初始化 Pinecone 客户端与索引
# Serverless 索引需要指定 environment 参数
_pinecone_client = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
_index = _pinecone_client.Index(INDEX_NAME)

def _embed_text(text: str) -> list:
    """
    使用统一的 embedding 模型将文本编码为向量，并返回 Python list 形式的向量。
    """
    embedding = _embedding_model.encode(text)  # 通常返回 numpy array
    if hasattr(embedding, "tolist"):
        embedding = embedding.tolist()
    return embedding

def generate_answer_with_knowledge(user_input: str, db, history_text: str = "", session_id: int = None) -> str:
    """
    综合 RAG + 上下文生成回答：
    1️⃣ 获取用户输入向量
    2️⃣ 检索 Pinecone 知识库
    3️⃣ 拼接上下文
    4️⃣ 调用大模型生成最终回答
    """
    # print('上下文：')
    # print(history_text)

    try:
        # 1️⃣ 编码问题（确保输出维度与 Pinecone 索引维度一致，这里是 384）
        query_vector = _embed_text(user_input)
        # print("查询向量长度:", len(query_vector))
        if len(query_vector) != 384:
            print("[Warning] 查询向量维度可能与索引维度不一致，请确认 Pinecone 索引的维度为 384。")

        # 2️⃣ Pinecone 查询
        response = _index.query(
            vector=query_vector,
            top_k=5,  # 查找前5个最相似的文档
            include_metadata=True
        )
        # print('pinecone响应', response)

        # 3️⃣ 从 Pinecone 结果中提取 IDs，并查询本地知识库
        matches = response.get('matches', [])
        idxs = [match['id'] for match in matches]
        # print("检索到的文档 ID:", idxs)

        if not idxs:
            print("没有检索到相关知识（matches 为空）。")
            knowledge_text = ""
            # 兜底：可以在这里返回一个默认回答，或继续走无知识的生成逻辑
        else:
            docs = db.query(KnowledgeDoc).filter(KnowledgeDoc.vector_id.in_(idxs)).all()
            # print("数据库查询结果:", docs)

            knowledge_text = "\n".join([f"- {d.title}: {d.description}" for d in docs])
        # print('rag结果:\n', knowledge_text if knowledge_text else "(无可用知识)")

        # 4️⃣ 获取结构化上下文信息
        structured_context = ""
        if session_id:
            from models.chat_session import ChatSession
            session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
            if session:
                session_data = {
                    'conversation_topic': session.conversation_topic,
                    'user_intent': session.user_intent,
                    'conversation_progress': session.conversation_progress
                }
                structured_context = ContextManager.build_structured_context(session_data)

        # 5️⃣ 构造最终提示词 Prompt
        prompt = f"""
## 角色定义
你是一名**电商平台智能客服助手**，专业、友善、高效。你的职责是帮助用户解决购物相关问题。

## 行为准则
- 只回答与电商购物相关的问题（商品信息、订单物流、售后服务等）
- 不知道或信息不足时，坦诚告知用户，不要编造答案
- 绝不在回答中添加"(思考中...)"、"(内心独白)"、"（此处应有表情）"等元评论
- 只输出正式回答内容，不输出任何括号内的自我描述

## 回答格式要求
- 使用简洁的陈述句直接回答用户问题
- 禁止在回答正文中使用圆括号()或方括号[]进行额外说明或心理描写

## 当前会话上下文
{structured_context}

## 对话历史
{history_text}

## 相关知识参考
{knowledge_text if knowledge_text else "（无相关知识，请基于常识回答）"}

## 用户问题
{user_input}

## 回答
"""
        # 6️⃣ 调用 LLM 生成最终回答
        return generate_response(prompt)

    except Exception as e:
        print(f"[RAG Engine Error] {e}")
        return "抱歉，我暂时无法获取到相关信息。"

# 可选：如果你愿意，提供一个简单的测试入口
if __name__ == "__main__":
    # 这个部分仅用于本地快速测试，实际部署中调用 generate_answer_with_knowledge 即可
    class DummyDB:
        def query(self, model):
            return []

    db = DummyDB()
    print(generate_answer_with_knowledge("你好，你是谁？商品什么时候发货？", db, history_text=""))

