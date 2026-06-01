#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
seed_knowledge_docs.py

把 Excel 数据写入 knowledge_docs 表（MySQL），确保 idx 映射到 vector_id（Pinecone ID）。
依赖：
  - pandas
  - openpyxl
  - sqlalchemy
  - pymysql
使用方式：
  - 在 PyCharm 的 Run 配置里设置环境变量：
      DATABASE_URL = mysql+pymysql://<user>:<password>@<host>:<port>/<db>?charset=utf8mb4
      EXCEL_PATH = <你的 excel 路径，例如 D:/.../LLM-DATASET.xlsx>
  - 运行脚本即可完成导入/更新。
"""

import os
import sys
import logging
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.knowledge_doc import KnowledgeDoc
from config import get_database_url

# 日志配置
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# 读取环境变量
EXCEL_PATH = os.environ.get("EXCEL_PATH", "D:/browserdownloads/LLM-DATASET.xlsx")  # 你可以改成你的实际路径
DATABASE_URL = get_database_url()

def main():
    # 校验 Excel 文件
    if not os.path.exists(EXCEL_PATH):
        logging.error(f"Excel 文件不存在，请检查 EXCEL_PATH 环境变量，路径为: {EXCEL_PATH}")
        sys.exit(1)

    # 读取 Excel，默认读取第一个工作表
    try:
        df = pd.read_excel(EXCEL_PATH, engine="openpyxl")
    except Exception as e:
        logging.exception("读取 Excel 失败：%s", e)
        sys.exit(1)

    # 常用字段映射
    USER_COL = "【中文】客户对话内容"
    ANSWER_COL = "【中文】客服对话内容"

    # 需要一个 idx 字段来匹配 Pinecone 向量 ID，优先使用 'id'，若没有再用 '对话id'
    idx_col_candidates = ["id"]
    idx_col = None
    for c in idx_col_candidates:
        if c in df.columns:
            idx_col = c
            break
    if idx_col is None:
        logging.error(f"Excel 缺少可用的 idx 列，请确保包含 {idx_col_candidates} 中的一列作为索引.")
        sys.exit(1)

    if USER_COL not in df.columns or ANSWER_COL not in df.columns:
        logging.error("请确认 Excel 包含以下列：%s、%s", USER_COL, ANSWER_COL)
        sys.exit(1)

    # 设置数据库引擎与会话
    engine = create_engine(DATABASE_URL, echo=False, future=True)
    SessionLocal = sessionmaker(bind=engine, future=True)

    # 逐行导入
    inserted = 0
    updated = 0
    with SessionLocal() as session:
        try:
            for _, row in df.iterrows():
                # 获取 idx（转成字符串，便于拼接）
                raw_id = row.get(idx_col)
                if pd.isna(raw_id):
                    continue
                try:
                    idx = str(int(raw_id)).strip()
                except Exception:
                    idx = str(raw_id).strip()

                if not idx:
                    continue

                pine_id = f"kb_{idx}"

                # 获取文本字段
                user_text = str(row.get(USER_COL, "")).strip()
                answer_text = str(row.get(ANSWER_COL, "")).strip()

                title = user_text[:200] if user_text else ""
                description = answer_text

                if not title and not description:
                    continue

                # 尝试查找现有记录（通过 vector_id）
                existing = session.query(KnowledgeDoc).filter_by(vector_id=pine_id).first()

                if existing:
                    # 更新现有记录（可根据需要扩展字段）
                    existing.title = title if title else existing.title
                    existing.description = description if description else existing.description
                    updated += 1
                else:
                    # 新增记录
                    doc = KnowledgeDoc(
                        domain="ecommerce",
                        vector_id=pine_id,
                        title=title,
                        description=description,
                        source="ExcelImport"
                    )
                    session.add(doc)
                    inserted += 1

            session.commit()
            logging.info("导入完成：新增 %d 条，更新 %d 条。", inserted, updated)
        except Exception as e:
            session.rollback()
            logging.exception("执行中发生错误：%s", e)
            sys.exit(1)

if __name__ == "__main__":
    main()
