import os
import pymysql

try:
    conn = pymysql.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", "your_db_password"),  # 通过环境变量 DB_PASSWORD 设置
        database=os.environ.get("DB_NAME", "llm_chatbot"),
        port=int(os.environ.get("DB_PORT", "3306"))
    )
    print("数据库连接成功！")
    # 检查manual_interventions表结构
    cursor = conn.cursor()
    cursor.execute("DESCRIBE manual_interventions")
    print("\nmanual_interventions表结构：")
    for row in cursor.fetchall():
        print(row)
    cursor.close()
    conn.close()
except Exception as e:
    print("数据库连接失败：", e)
