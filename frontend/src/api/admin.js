import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 不需要添加认证令牌，因为管理员页面不需要权限验证
/*
api.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)
*/

// 不需要处理令牌过期，因为管理员页面不需要权限验证
/*
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      // 令牌过期，重定向到登录页面
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
*/

// 用户相关 API
export const userApi = {
  getUsers: () => api.get('/users'),
  getUser: (userId) => api.get(`/users/${userId}`),
  createUser: (userData) => api.post('/users', userData),
  updateUser: (userId, userData) => api.put(`/users/${userId}`, userData),
  deleteUser: (userId) => api.delete(`/users/${userId}`)
}

// 对话会话相关 API
export const sessionApi = {
  getSessions: () => api.get('/chat_sessions'),
  getSession: (sessionId) => api.get(`/chat_sessions/${sessionId}`),
  getSessionMessages: (sessionId) => api.get(`/chat_messages/session/${sessionId}`),
  deleteSession: (sessionId) => api.delete(`/chat_sessions/${sessionId}`)
}

// 对话消息相关 API
export const messageApi = {
  getMessages: () => api.get('/chat_messages')
}

// 反馈相关 API
export const feedbackApi = {
  getFeedback: (messageId) => api.get(`/feedback/message/${messageId}`),
  listFeedbacks: (params = {}) => api.get('/feedback', { params }),
  listTextFeedbacks: (params = {}) => api.get('/feedback/text', { params }),
  updateFeedbackStatus: (feedbackId, status) => api.put(`/feedback/${feedbackId}/status`, { status }),
  deleteFeedback: (feedbackId) => api.delete(`/feedback/${feedbackId}`),
  deleteTextFeedback: (feedbackId) => api.delete(`/feedback/text/${feedbackId}`)
}

// 系统日志相关 API
export const logApi = {
  getLogs: () => api.get('/system_logs')
}

// 转人工记录相关 API
export const manualApi = {
  getManualBySession: (sessionId) => api.get(`/manual_interventions/session/${sessionId}`),
  getManualRecords: () => api.get('/manual_interventions')
}

export const analysisApi = {
  getSummary: () => api.get('/admin/analysis-summary')
}

export const knowledgeApi = {
  listDocs: (params = {}) => api.get('/knowledge_docs', { params }),
  createDoc: (data) => api.post('/knowledge_docs/', data),
  updateDoc: (docId, data) => api.put(`/knowledge_docs/${docId}`, data),
  deleteDoc: (docId) => api.delete(`/knowledge_docs/${docId}`),
  importChunked: (data) => api.post('/knowledge_docs/import/chunked', data),
  importFilesChunked: (formData) => api.post('/knowledge_docs/import/files', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  listChangeLogs: (params = {}) => api.get('/knowledge_docs/change_logs', { params }),
  listBatchChangeLogs: () => api.get('/knowledge_docs/change_logs/batches'),
  undoBatchImport: (batchId) => api.post(`/knowledge_docs/batches/${batchId}/undo`)
}

export default {
  userApi,
  sessionApi,
  messageApi,
  feedbackApi,
  logApi,
  manualApi,
  analysisApi,
  knowledgeApi
}