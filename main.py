# -*- coding: utf-8 -*-
from fastapi import FastAPI
from database import Base, engine
from routers import (
    user_router, chat_session_router, knowledge_router,
    manual_router, system_log_router,chat_message_router,
    chat_router, feedback_router, debug_router, auth_router, admin_router
)
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173",   # Vue/Vite 默认开发端口
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5175",
    "http://localhost:5176",
    "http://127.0.0.1:5176",
]


from models import user, chat_session, chat_message, knowledge_doc, manual_intervention, system_log, text_feedback, knowledge_change_log
# 创建所有数据库表 - 只创建不存在的表，不删除已有数据
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(chat_session_router.router)
app.include_router(chat_message_router.router)
app.include_router(knowledge_router.router)
app.include_router(manual_router.router)
app.include_router(system_log_router.router)
app.include_router(chat_router.router)
app.include_router(feedback_router.router)
app.include_router(debug_router.router)
app.include_router(admin_router.router)

@app.on_event("startup")
def ensure_startup_log():
    """
    确保系统日志页不会永远为空：当库里没有任何日志时写入一条启动日志。
    """
    try:
        from database import SessionLocal
        from models.system_log import SystemLog

        db = SessionLocal()
        try:
            has_any = db.query(SystemLog.id).first() is not None
            if not has_any:
                db.add(SystemLog(level="INFO", message="System started"))
                db.commit()
        finally:
            db.close()
    except Exception:
        # 启动日志不应影响服务启动
        pass

@app.get("/")
def home():
    return {"message": "FastAPI + MySQL is running successfully 🚀"}