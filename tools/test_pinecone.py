import os
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from config import get_hf_token, get_pinecone_api_key, get_pinecone_environment

os.environ["HF_TOKEN"] = get_hf_token()
# 1. 加载模型
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# 2. 创建 Pinecone 实例并初始化
pc = Pinecone(api_key=get_pinecone_api_key())

# 3. 连接到 Pinecone Index（创建或者加载已有的）
index_name = "ecommerce-kb"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,  # 根据你存储的向量维度选择
        metric='cosine',
        spec=ServerlessSpec(cloud='aws', region='us-west-2')  # 根据需要选择区域
)

index = pc.Index(index_name)

# 4. 示例查询
query = "如何申请退款？"
embedding = model.encode(query).tolist()

# 5. 查询 Pinecone，获取最相似的前 5 个结果
response = index.query(
    vector=embedding,
    top_k=5,
    include_metadata=True
)

# 6. 打印查询结果
for match in response['matches']:
    print(f"Score: {match['score']}, Question: {match['metadata']['question']}, Answer: {match['metadata']['answer']}")
