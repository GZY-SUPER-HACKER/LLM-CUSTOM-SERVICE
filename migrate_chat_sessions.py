# -*- coding: utf-8 -*-
"""
数据库迁移脚本 - 为chat_sessions表添加缺失的列
"""
import os
import pymysql

# 优先从环境变量读取数据库连接信息
DATABASE_CONFIG = {
    "host": os.environ.get("DB_HOST", "127.0.0.1"),
    "port": int(os.environ.get("DB_PORT", "3306")),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "your_db_password"),  # 通过环境变量 DB_PASSWORD 设置
    "database": os.environ.get("DB_NAME", "llm_chatbot"),
    "charset": "utf8mb4"
}

def migrate_chat_sessions():
    """为chat_sessions表添加缺失的列"""
    connection = pymysql.connect(**DATABASE_CONFIG)

    try:
        with connection.cursor() as cursor:
            # 检查并添加 conversation_topic 列
            cursor.execute("""
                SELECT COUNT(*)
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = 'chat_sessions' AND column_name = 'conversation_topic'
            """, (DATABASE_CONFIG["database"],))
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    ALTER TABLE chat_sessions
                    ADD COLUMN conversation_topic VARCHAR(255) NULL AFTER created_at
                """)
                print("[OK] 列 conversation_topic 已添加")
            else:
                print("[SKIP] 列 conversation_topic 已存在")

            # 检查并添加 user_intent 列
            cursor.execute("""
                SELECT COUNT(*)
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = 'chat_sessions' AND column_name = 'user_intent'
            """, (DATABASE_CONFIG["database"],))
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    ALTER TABLE chat_sessions
                    ADD COLUMN user_intent VARCHAR(100) NULL AFTER conversation_topic
                """)
                print("[OK] 列 user_intent 已添加")
            else:
                print("[SKIP] 列 user_intent 已存在")

            # 检查并添加 conversation_progress 列
            cursor.execute("""
                SELECT COUNT(*)
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = 'chat_sessions' AND column_name = 'conversation_progress'
            """, (DATABASE_CONFIG["database"],))
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    ALTER TABLE chat_sessions
                    ADD COLUMN conversation_progress TEXT NULL AFTER user_intent
                """)
                print("[OK] 列 conversation_progress 已添加")
            else:
                print("[SKIP] 列 conversation_progress 已存在")

        connection.commit()
        print("\n[SUCCESS] 数据库迁移完成！")

    except Exception as e:
        print(f"[ERROR] 迁移失败: {e}")
        connection.rollback()
    finally:
        connection.close()

if __name__ == "__main__":
    print("=" * 50)
    print("开始数据库迁移...")
    print("=" * 50)
    migrate_chat_sessions()
    print("=" * 50)