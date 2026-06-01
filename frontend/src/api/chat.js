import axios from "axios";

const API_BASE = "http://127.0.0.1:8000"; // 后端地址

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 30000, // 30秒超时
  headers: {
    'Content-Type': 'application/json'
  }
});

export async function sendQuestion(question, history = []) {
  try {
    // 构建请求URL
    const url = `${API_BASE}/chat/send_message`;
    
    // 准备请求数据
    const requestData = {
      user_id: 1,
      user_input: question,
      session_id: 1
    };
    
    console.log("发送请求到:", url);
    console.log("发送请求数据:", requestData);

    // 发送请求（使用请求体）
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData)
    });
    
    console.log("响应状态:", res.status);
    console.log("响应状态文本:", res.statusText);
    
    // 解析响应数据
    const data = await res.json();
    console.log("响应数据:", data);
    
    // 检查响应状态
    if (!res.ok) {
      throw new Error(`请求失败: ${res.status} ${res.statusText}`);
    }

    // 后端返回的消息结构
    const messages = Array.isArray(data) ? data : [];

    // 获取最新的回答（通常是 assistant 角色的最后一条消息）
    const answer = messages
      .filter(msg => msg.role === "assistant") // 筛选出 assistant 的消息
      .pop(); // 获取最后一条消息

    return { answer: answer ? answer.content : "没有得到有效回答" };
  } catch (err) {
    console.error("API请求失败:", err);
    
    // 更详细的错误处理
    let errorMessage = "请求失败，请稍后重试";
    if (err instanceof Response) {
      errorMessage = `请求失败: ${err.status} ${err.statusText}`;
    } else if (err.message) {
      errorMessage = err.message;
    }
    
    throw new Error(errorMessage);
  }
}
