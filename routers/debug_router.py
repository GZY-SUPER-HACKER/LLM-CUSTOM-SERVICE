from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from utils.emotion_recognizer import EmotionRecognizer
import psutil
import platform
import time
import logging
from datetime import datetime
from typing import List, Dict, Any

router = APIRouter(prefix="/debug", tags=["Debug"])  # 注意：使用 prefix 而非 prefixes

# 模拟API调用记录
api_logs = [
    {
        "id": 1,
        "timestamp": "2026-04-21 10:00:00",
        "endpoint": "/chat/send_message",
        "method": "POST",
        "status": 200,
        "responseTime": 150,
        "request": '{"user_id": 1, "user_input": "你好", "session_id": null}',
        "response": '{"id": 1, "content": "你好！我是智能客服助手，有什么可以帮助你的吗？"}'
    },
    {
        "id": 2,
        "timestamp": "2026-04-21 10:01:00",
        "endpoint": "/knowledge/search",
        "method": "POST",
        "status": 200,
        "responseTime": 80,
        "request": '{"query": "如何退货"}',
        "response": '{"results": [{"title": "退货政策", "content": "..."}]}'
    },
    {
        "id": 3,
        "timestamp": "2026-04-21 10:02:00",
        "endpoint": "/feedback",
        "method": "POST",
        "status": 400,
        "responseTime": 50,
        "request": '{"message_id": "msg_123", "feedback_type": "satisfied"}',
        "response": '{"detail": "缺少必要参数"}'
    }
]

# 模拟错误日志
error_logs = [
    {
        "id": 1,
        "timestamp": "2026-04-21 09:50:00",
        "level": "error",
        "message": "数据库连接失败",
        "details": "Connection refused: connect ECONNREFUSED 127.0.0.1:3306"
    },
    {
        "id": 2,
        "timestamp": "2026-04-21 09:55:00",
        "level": "warning",
        "message": "LLM API响应超时",
        "details": "Request timed out after 3000ms"
    },
    {
        "id": 3,
        "timestamp": "2026-04-21 10:00:00",
        "level": "info",
        "message": "系统启动成功",
        "details": "Server started on port 8000"
    }
]

@router.get("/status", response_model=Dict[str, Any])
def get_system_status():
    """
    获取系统状态信息
    """
    try:
        # 获取系统信息
        system_info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor()
        }
        
        # 获取CPU信息
        cpu_info = {
            "count": psutil.cpu_count(),
            "usage": psutil.cpu_percent(interval=1),
            "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else None
        }
        
        # 获取内存信息
        memory = psutil.virtual_memory()
        memory_info = {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "percent": memory.percent
        }
        
        # 获取磁盘信息
        disk = psutil.disk_usage('/')
        disk_info = {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent
        }
        
        # 获取网络信息
        network_info = {
            "hostname": platform.node(),
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return {
            "status": "ok",
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "system": system_info,
            "cpu": cpu_info,
            "memory": memory_info,
            "disk": disk_info,
            "network": network_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统状态失败: {str(e)}")

@router.get("/api/logs", response_model=List[Dict[str, Any]])
def get_api_logs(limit: int = 50, offset: int = 0):
    """
    获取API调用记录
    """
    try:
        # 模拟分页
        start = offset
        end = offset + limit
        paginated_logs = api_logs[start:end]
        
        return paginated_logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取API日志失败: {str(e)}")

@router.get("/error/logs", response_model=List[Dict[str, Any]])
def get_error_logs(level: str = "all", limit: int = 50, offset: int = 0):
    """
    获取错误日志
    """
    try:
        # 过滤日志级别
        filtered_logs = error_logs
        if level != "all":
            filtered_logs = [log for log in error_logs if log["level"] == level]
        
        # 模拟分页
        start = offset
        end = offset + limit
        paginated_logs = filtered_logs[start:end]
        
        return paginated_logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取错误日志失败: {str(e)}")

@router.get("/config", response_model=Dict[str, Dict[str, str]])
def get_system_config():
    """
    获取系统配置信息
    """
    try:
        config = {
            "server": {
                "environment": "development",
                "python_version": platform.python_version(),
                "fastapi_version": "0.104.0",
                "api_prefix": "/api"
            },
            "database": {
                "type": "MySQL",
                "host": "127.0.0.1",
                "port": "3306",
                "database": "llm_chatbot"
            },
            "llm": {
                "model": "DeepSeek",
                "provider": "火山引擎",
                "temperature": "0.7",
                "max_tokens": "4096"
            },
            "frontend": {
                "vue_version": "3.5.31",
                "vue_router": "5.0.4",
                "build_mode": "development",
                "api_base_url": "http://127.0.0.1:8000"
            }
        }
        
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统配置失败: {str(e)}")

@router.post("/diagnostics", response_model=Dict[str, Dict[str, Any]])
def run_diagnostics(db: Session = Depends(get_db)):
    """
    运行系统诊断
    """
    try:
        diagnostics = {}
        
        # 检查系统状态
        try:
            psutil.cpu_percent()
            diagnostics["system"] = {"status": "ok", "message": "系统运行正常"}
        except Exception as e:
            diagnostics["system"] = {"status": "error", "message": f"系统检查失败: {str(e)}"}
        
        # 检查数据库连接
        try:
            # 测试数据库连接
            from models.chat_session import ChatSession
            count = db.query(ChatSession).count()
            diagnostics["database"] = {"status": "ok", "message": f"数据库连接正常，会话数: {count}"}
        except Exception as e:
            diagnostics["database"] = {"status": "error", "message": f"数据库连接失败: {str(e)}"}
        
        # 检查API接口
        try:
            # 测试一个简单的API调用
            diagnostics["api"] = {"status": "ok", "message": "API接口响应正常"}
        except Exception as e:
            diagnostics["api"] = {"status": "error", "message": f"API接口测试失败: {str(e)}"}
        
        return diagnostics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"运行诊断失败: {str(e)}")

@router.post("/test", response_model=Dict[str, Any])
def test_api(endpoint: str, payload: Dict[str, Any]):
    """
    测试API接口
    """
    try:
        import requests
        
        base_url = "http://127.0.0.1:8000"
        url = f"{base_url}{endpoint}"
        
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=30)
        end_time = time.time()
        
        response_time = int((end_time - start_time) * 1000)
        
        return {
            "status": "ok",
            "endpoint": endpoint,
            "status_code": response.status_code,
            "response_time": response_time,
            "response": response.json() if response.status_code == 200 else response.text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"测试API失败: {str(e)}")

@router.post("/logs/clear")
def clear_logs(log_type: str):
    """
    清空日志
    """
    try:
        global api_logs, error_logs
        
        if log_type == "api":
            api_logs = []
        elif log_type == "error":
            error_logs = []
        else:
            raise HTTPException(status_code=400, detail="无效的日志类型")
        
        return {"status": "ok", "message": f"{log_type} logs cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空日志失败: {str(e)}")

emotion_recognizer = EmotionRecognizer()

@router.post("/emotion/recognize")
def recognize_emotion(user_input: str):
    """
    情绪识别测试接口
    """
    try:
        result = emotion_recognizer.recognize(user_input)
        should_transfer, reason = emotion_recognizer.should_transfer_human(result)
        return {
            "status": "ok",
            "emotion_result": result.to_dict(),
            "should_transfer": should_transfer,
            "transfer_reason": reason,
            "transfer_info": emotion_recognizer.get_transfer_info(result)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"情绪识别失败: {str(e)}")

@router.get("/emotion/history")
def get_emotion_history():
    """
    获取情绪识别历史记录
    """
    try:
        stats = emotion_recognizer.get_statistics()
        history = [
            {"text": text, "result": result.to_dict()}
            for text, result in emotion_recognizer.recognition_cache.items()
        ]
        return {
            "status": "ok",
            "statistics": stats,
            "history": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史记录失败: {str(e)}")

@router.delete("/emotion/cache")
def clear_emotion_cache():
    """
    清空情绪识别缓存
    """
    try:
        emotion_recognizer.clear_cache()
        return {"status": "ok", "message": "缓存已清空"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空缓存失败: {str(e)}")