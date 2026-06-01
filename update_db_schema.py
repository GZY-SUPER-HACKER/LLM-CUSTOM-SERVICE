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
    cursor = conn.cursor()
    
    # 添加缺失的字段
    alter_commands = [
        "ALTER TABLE manual_interventions ADD COLUMN emotion_type VARCHAR(50) NULL",
        "ALTER TABLE manual_interventions ADD COLUMN emotion_intensity FLOAT NULL",
        "ALTER TABLE manual_interventions ADD COLUMN emotion_level VARCHAR(20) NULL",
        "ALTER TABLE manual_interventions ADD COLUMN is_emotionally_agitated BOOLEAN NULL",
        "ALTER TABLE manual_interventions ADD COLUMN emotion_confidence FLOAT NULL",
        "ALTER TABLE manual_interventions ADD COLUMN tone_intensity FLOAT NULL",
        "ALTER TABLE manual_interventions ADD COLUMN negative_emotion_degree FLOAT NULL",
        "ALTER TABLE manual_interventions ADD COLUMN urgency_level FLOAT NULL",
        "ALTER TABLE manual_interventions ADD COLUMN loss_of_control_risk FLOAT NULL",
        "ALTER TABLE manual_interventions ADD COLUMN transfer_reason TEXT NULL",
        "ALTER TABLE manual_interventions ADD COLUMN conversation_topic VARCHAR(100) NULL",
        "ALTER TABLE manual_interventions ADD COLUMN user_intent VARCHAR(50) NULL",
        "ALTER TABLE manual_interventions ADD COLUMN conversation_progress TEXT NULL"
    ]
    
    for command in alter_commands:
        try:
            cursor.execute(command)
            print(f"执行成功: {command}")
        except Exception as e:
            print(f"执行失败: {command}")
            print(f"错误: {e}")
    
    # 提交更改
    conn.commit()
    
    # 验证表结构
    cursor.execute("DESCRIBE manual_interventions")
    print("\n更新后的manual_interventions表结构：")
    for row in cursor.fetchall():
        print(row)
    
    cursor.close()
    conn.close()
    print("\n表结构更新完成！")
    
except Exception as e:
    print("数据库操作失败：", e)