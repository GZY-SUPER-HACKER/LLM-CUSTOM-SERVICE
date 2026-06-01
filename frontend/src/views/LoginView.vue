<template>
  <div class="login-container">
    <div class="login-form">
      <h2>用户登录</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">用户名</label>
          <input 
            type="text" 
            id="username" 
            v-model="loginForm.username" 
            required 
            placeholder="请输入用户名"
          />
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input 
            type="password" 
            id="password" 
            v-model="loginForm.password" 
            required 
            placeholder="请输入密码"
          />
        </div>
        <div class="form-actions">
          <button type="submit" class="btn-primary" :disabled="loading">
            {{ loading ? '登录中...' : '登录' }}
          </button>
          <router-link to="/register" class="btn-secondary">注册</router-link>
        </div>
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../api/auth'

const router = useRouter()
const loginForm = ref({
  username: '',
  password: ''
})
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await login(loginForm.value)
    // 存储令牌和用户信息
    localStorage.setItem('token', response.access_token)
    localStorage.setItem('user', JSON.stringify({
      id: response.user_id,
      username: response.username,
      role: response.role
    }))
    // 根据用户角色跳转到不同页面
    if (response.role === 'admin') {
      // 管理员跳转到后台管理页面
      router.push('/admin')
    } else {
      // 普通用户跳转到客服界面（首页）
      router.push('/')
    }
  } catch (err) {
    error.value = err.response?.data?.detail || '登录失败，请检查用户名和密码'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.login-form {
  background-color: white;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.login-form h2 {
  margin-bottom: 30px;
  text-align: center;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #666;
  font-weight: bold;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 30px;
}

.btn-primary {
  flex: 1;
  background-color: #3498db;
  color: white;
  border: none;
  padding: 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
}

.btn-primary:hover {
  background-color: #2980b9;
}

.btn-primary:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.btn-secondary {
  flex: 1;
  background-color: #95a5a6;
  color: white;
  border: none;
  padding: 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  text-align: center;
  text-decoration: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-secondary:hover {
  background-color: #7f8c8d;
}

.error-message {
  margin-top: 20px;
  padding: 10px;
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
  text-align: center;
}

@media (max-width: 768px) {
  .login-form {
    padding: 20px;
    margin: 20px;
  }
  
  .form-actions {
    flex-direction: column;
  }
}
</style>