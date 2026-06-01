import os
import pandas as pd
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from config import get_hf_token, get_pinecone_api_key, get_pinecone_index_name

HF_TOKEN = get_hf_token()
PINECONE_API_KEY = get_pinecone_api_key()
INDEX_NAME = get_pinecone_index_name()
EXCEL_PATH = os.environ.get("EXCEL_PATH", r"D:\browserdownloads\LLM-DATASET.xlsx")

os.environ["HF_TOKEN"] = HF_TOKEN

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

df = pd.read_excel(EXCEL_PATH)

QUESTION_COL = "【中文】客户对话内容"
ANSWER_COL = "【中文】客服对话内容"
ID_COL = "id"

if ID_COL not in df.columns:
    raise ValueError(f"Excel 缺少 {ID_COL} 列")

BATCH_SIZE = 100
vectors = []
count = 0

for _, row in tqdm(df.iterrows(), total=len(df)):
    raw_id = row.get(ID_COL)
    if pd.isna(raw_id):
        continue

    try:
        record_id = str(int(raw_id)).strip()
    except Exception:
        record_id = str(raw_id).strip()

    if not record_id:
        continue

    question = str(row[QUESTION_COL]).strip()
    answer = str(row[ANSWER_COL]).strip()

    if not question or not answer:
        continue

    embed_text = f"用户问题：{question}\n客服回答：{answer}"
    embedding = model.encode(embed_text).tolist()

    vectors.append({
        "id": f"kb_{record_id}",
        "values": embedding,
        "metadata": {
            "question": question,
            "answer": answer,
            "domain": "ecommerce",
            "source": "LLM-DATASET",
            "language": "zh"
        }
    })

    if len(vectors) >= BATCH_SIZE:
        index.upsert(vectors=vectors)
        count += len(vectors)
        vectors = []

if vectors:
    index.upsert(vectors=vectors)
    count += len(vectors)

print(f"✅ 成功写入 Pinecone 向量数：{count}")
