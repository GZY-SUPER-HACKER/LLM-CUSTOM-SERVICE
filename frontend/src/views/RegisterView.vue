<template>
  <div class="register-container">
    <div class="register-form">
      <h2>用户注册</h2>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="username">用户名</label>
          <input 
            type="text" 
            id="username" 
            v-model="registerForm.username" 
            required 
            placeholder="请输入用户名"
          />
        </div>
        <div class="form-group">
          <label for="email">邮箱</label>
          <input 
            type="email" 
            id="email" 
            v-model="registerForm.email" 
            required 
            placeholder="请输入邮箱"
          />
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input 
            type="password" 
            id="password" 
            v-model="registerForm.password" 
            required 
            placeholder="请输入密码"
          />
        </div>
        <div class="form-actions">
          <button type="submit" class="btn-primary" :disabled="loading">
            {{ loading ? '注册中...' : '注册' }}
          </button>
          <router-link to="/login" class="btn-secondary">登录</router-link>
        </div>
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        <div v-if="success" class="success-message">
          {{ success }}
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { register } from '../api/auth'

const router = useRouter()
const registerForm = ref({
  username: '',
  email: '',
  password: '',
  role: 'user'
})
const loading = ref(false)
const error = ref('')
const success = ref('')

const handleRegister = async () => {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    await register(registerForm.value)
    success.value = '注册成功，请登录'
    // 3秒后跳转到登录页面
    setTimeout(() => {
      router.push('/login')
    }, 3000)
  } catch (err) {
    error.value = err.response?.data?.detail || '注册失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.register-form {
  background-color: white;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.register-form h2 {
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
  background-color: #27ae60;
  color: white;
  border: none;
  padding: 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
}

.btn-primary:hover {
  background-color: #219a52;
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

.success-message {
  margin-top: 20px;
  padding: 10px;
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
  border-radius: 4px;
  text-align: center;
}

@media (max-width: 768px) {
  .register-form {
    padding: 20px;
    margin: 20px;
  }
  
  .form-actions {
    flex-direction: column;
  }
}
</style>