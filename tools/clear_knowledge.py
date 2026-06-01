#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
clear_knowledge.py

删除 MySQL 数据库中的 knowledge_docs 表数据和 Pinecone 数据库中的向量数据。
依赖：
  - sqlalchemy
  - pymysql
  - pinecone-client
使用方式：
  - 直接运行脚本即可完成清理。
"""

import os
import sys
import logging

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_database_url, get_pinecone_api_key, get_pinecone_index_name

# 日志配置
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def clear_mysql_data():
    """删除 MySQL 数据库中的 knowledge_docs 表数据"""
    try:
        from sqlalchemy import create_engine
        from models.knowledge_doc import KnowledgeDoc
        
        DATABASE_URL = get_database_url()
        
        engine = create_engine(DATABASE_URL, echo=False, future=True)
        
        # 删除所有数据
        with engine.connect() as conn:
            conn.execute(KnowledgeDoc.__table__.delete())
            conn.commit()
            logging.info("MySQL: knowledge_docs 表数据已全部删除")
            return True
    except Exception as e:
        logging.exception("删除 MySQL 数据失败：%s", e)
        return False

def clear_pinecone_data():
    """删除 Pinecone 数据库中的所有向量数据"""
    try:
        from pinecone import Pinecone
        
        # 从环境变量读取 Pinecone 配置
        api_key = get_pinecone_api_key()
        index_name = get_pinecone_index_name()
        
        # 初始化 Pinecone（使用新 API）
        pc = Pinecone(api_key=api_key)
        
        # 检查索引是否存在
        if index_name not in pc.list_indexes().names():
            logging.warning(f"Pinecone 索引 {index_name} 不存在")
            return True
        
        # 获取索引
        index = pc.Index(index_name)
        
        # 删除所有向量（使用 delete 操作）
        index.delete(delete_all=True)
        logging.info(f"Pinecone: 索引 {index_name} 中的所有向量已删除")
        return True
    except Exception as e:
        logging.exception("删除 Pinecone 数据失败：%s", e)
        return False

def main():
    logging.info("开始清理知识数据...")
    
    # 清理 MySQL 数据
    mysql_success = clear_mysql_data()
    
    # 清理 Pinecone 数据（即使失败也继续）
    pinecone_success = clear_pinecone_data()
    
    if mysql_success:
        logging.info("MySQL 数据清理完成！")
        if pinecone_success:
            logging.info("Pinecone 数据清理完成！")
            logging.info("所有数据清理完成！")
        else:
            logging.warning("Pinecone 数据清理失败，请手动清理或检查 API 密钥")
            logging.info("MySQL 数据已成功清理，可以重新导入知识条目")
        sys.exit(0)
    else:
        logging.error("MySQL 数据清理失败，请检查日志")
        sys.exit(1)

if __name__ == "__main__":
    main()