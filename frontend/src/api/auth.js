import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 登录
export const login = async (credentials) => {
  const response = await api.post('/auth/login', {
    username: credentials.username,
    password: credentials.password
  }, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    transformRequest: [(data) => {
      let formData = ''
      for (const key in data) {
        formData += `${encodeURIComponent(key)}=${encodeURIComponent(data[key])}&`
      }
      return formData.slice(0, -1)
    }]
  })
  return response.data
}

// 注册
export const register = async (userData) => {
  const response = await api.post('/auth/register', userData)
  return response.data
}

// 获取当前用户信息
export const getCurrentUser = async () => {
  const token = localStorage.getItem('token')
  if (!token) {
    throw new Error('No token found')
  }
  const response = await api.get('/auth/me', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })
  return response.data
}

// 刷新令牌
export const refreshToken = async () => {
  const token = localStorage.getItem('token')
  if (!token) {
    throw new Error('No token found')
  }
  const response = await api.post('/auth/refresh', {}, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })
  return response.data
}

// 登出
export const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
}

// 检查是否已登录
export const isLoggedIn = () => {
  return localStorage.getItem('token') !== null
}

// 获取用户信息
export const getUser = () => {
  const userStr = localStorage.getItem('user')
  return userStr ? JSON.parse(userStr) : null
}

// 获取令牌
export const getToken = () => {
  return localStorage.getItem('token')
}

export default {
  login,
  register,
  getCurrentUser,
  refreshToken,
  logout,
  isLoggedIn,
  getUser,
  getToken
}