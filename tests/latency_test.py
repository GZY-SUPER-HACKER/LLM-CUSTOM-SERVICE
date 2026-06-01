# -*- coding: utf-8 -*-
"""
系统响应时间测试脚本
测量从前端请求到后端返回的完整链路延迟，并分析各阶段耗时。
"""
import time
import sys
import json

# 1. 直接测试完整端点（端到端）
print("=" * 60)
print("测试1: 完整端到端请求 (POST /chat/send_message)")
print("=" * 60)

import urllib.request

data = json.dumps({
    "user_id": 1,
    "user_input": "你好，请问你们主要卖什么产品？",
    "session_id": None
}).encode("utf-8")

req = urllib.request.Request(
    "http://127.0.0.1:8000/chat/send_message",
    data=data,
    headers={"Content-Type": "application/json"}
)

t0 = time.time()
try:
    resp = urllib.request.urlopen(req, timeout=180)
    t1 = time.time()
    body = resp.read().decode("utf-8")
    t2 = time.time()
    msgs = json.loads(body)
    print(f"  总响应时间 (端到端): {t2 - t0:.3f}s")
    print(f"  首字节时间:           {t1 - t0:.3f}s")
    print(f"  响应体下载时间:       {t2 - t1:.3f}s")
    last = [m for m in msgs if m["role"] == "assistant"]
    if last:
        print(f"  AI回复内容 ({len(last[-1]['content'])}字): {last[-1]['content'][:80]}")
except Exception as e:
    t2 = time.time()
    print(f"  请求失败 ({t2-t0:.1f}s): {e}")

# 2. 分阶段测试
print()
print("=" * 60)
print("测试2: 各组件延迟分解")
print("=" * 60)

from sentence_transformers import SentenceTransformer
import numpy as np
import os
from config import get_hf_token
os.environ["HF_TOKEN"] = get_hf_token()

# 2a. Embedding 模型
print("\n[2a] SentenceTransformer Embedding")
t0 = time.time()
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
t_load = time.time() - t0
print(f"  模型加载: {t_load:.2f}s")

texts = [
    "请问你们的退货政策是怎样的？",
    "这个商品什么时候能发货？",
    "我想查询一下我的订单状态"
]
for txt in texts:
    t0 = time.time()
    for _ in range(5):
        emb = model.encode(txt)
    avg = (time.time() - t0) / 5
    print(f"  编码 \"{txt[:20]}...\": {avg*1000:.1f}ms (5次平均)")

# 2b. Pinecone 向量检索
print("\n[2b] Pinecone 向量检索")
from pinecone import Pinecone
from config import get_pinecone_api_key, get_pinecone_environment
t0 = time.time()
pc = Pinecone(
    api_key=get_pinecone_api_key(),
    environment=get_pinecone_environment()
)
idx = pc.Index("ecommerce-kb")
t_pc_init = time.time() - t0
print(f"  初始化: {t_pc_init*1000:.1f}ms")

vec = model.encode("请问你们的退货政策是怎样的？").tolist()
t0 = time.time()
for _ in range(5):
    r = idx.query(vector=vec, top_k=5, include_metadata=True)
t_pc_query = (time.time() - t0) / 5
print(f"  单次查询: {t_pc_query*1000:.1f}ms (5次平均)")
print(f"  命中数量: {len(r.get('matches', []))}")

# 2c. DeepSeek LLM API
print("\n[2c] DeepSeek LLM API 调用")
from utils.providers.volc_deepseek_client import chat_with_deepseek
t0 = time.time()
result = chat_with_deepseek("你好，请用一句话介绍退货政策")
t_llm = time.time() - t0
print(f"  单次调用: {t_llm:.3f}s")
print(f"  返回内容: {result[:80]}")

# 2d. ContextManager (分类+情绪)
print("\n[2d] ContextManager 转人工判断")
from utils.rag_engine import generate_answer_with_knowledge
from utils.context_manager import ContextManager

t0 = time.time()
for _ in range(5):
    s, r = ContextManager.should_transfer_human("你好，请问有什么帮助？")
t_check = (time.time() - t0) / 5
print(f"  should_transfer_human: {t_check*1000:.1f}ms (5次平均)")

# 情绪强的文本
t0 = time.time()
s, r = ContextManager.should_transfer_human("你们这是什么垃圾服务！我要投诉！")
t_angry = time.time() - t0
print(f"  负面情绪文本: {t_angry*1000:.1f}ms")

# 2e. 数据库操作
print("\n[2e] 数据库操作 (SQLite)")
from database import SessionLocal
from models.chat_session import ChatSession
from models.chat_message import ChatMessage
from models.knowledge_doc import KnowledgeDoc

db = SessionLocal()

t0 = time.time()
for _ in range(5):
    last5 = db.query(ChatMessage).order_by(ChatMessage.id.desc()).limit(5).all()
t_db_read = (time.time() - t0) / 5
print(f"  读取最近5条消息: {t_db_read*1000:.1f}ms (5次平均)")

t0 = time.time()
for _ in range(3):
    msg = ChatMessage(session_id=1, role="user", content="test msg")
    db.add(msg)
    db.commit()
    db.delete(msg)
    db.commit()
t_db_write = (time.time() - t0) / 3
print(f"  写入+提交: {t_db_write*1000:.1f}ms (3次平均)")

t0 = time.time()
for _ in range(5):
    docs = db.query(KnowledgeDoc).filter(KnowledgeDoc.vector_id.in_(["d1", "d2"])).all()
t_db_kb = (time.time() - t0) / 5
print(f"  知识库向量ID查询: {t_db_kb*1000:.1f}ms (5次平均)")

session = db.query(ChatSession).filter(ChatSession.id == 1).first()
t0 = time.time()
for _ in range(3):
    session.conversation_topic = "test"
    session.user_intent = "test"
    session.conversation_progress = "test"
    db.commit()
t_db_update = (time.time() - t0) / 3
print(f"  会话上下文更新+提交: {t_db_update*1000:.1f}ms (3次平均)")

db.close()

# 3. 总结
print()
print("=" * 60)
print("延迟构成汇总 (以一次典型请求为例)")
print("=" * 60)

components = [
    ("A. 请求网络传输 (估算)", 1.0),
    ("B. 会话检查/创建 (DB)", 30.0),
    ("C. 用户消息落库 (DB)", 15.0),
    ("D. 转人工判断", t_check * 1000),
    ("E. Embedding 编码", 50.0),
    ("F. Pinecone 向量检索", t_pc_query * 1000),
    ("G. 知识库DB查询", t_db_kb * 1000),
    ("H. 上下文获取+构造", 20.0),
    ("I. DeepSeek LLM 调用", t_llm * 1000),
    ("J. AI回复落库 (DB)", 15.0),
    ("K. 上下文更新 (DB)", t_db_update * 1000),
    ("L. 全量消息查询返回 (DB)", t_db_read * 1000),
    ("M. 响应网络传输 (估算)", 1.0),
]

total = 0
for name, val in components:
    print(f"  {name}: {val:.1f}ms")
    total += val

print(f"  {'-' * 40}")
print(f"  理论合计: {total:.1f}ms = {total/1000:.2f}s")
print(f"  实测端到端: 请参考测试1结果")
print()

# 瓶颈分析
print("瓶颈分析:")
components_sorted = sorted(components, key=lambda x: x[1], reverse=True)
for i, (name, val) in enumerate(components_sorted[:3]):
    pct = val / total * 100
    print(f"  #{i+1} {name}: {val:.0f}ms ({pct:.0f}%)")
