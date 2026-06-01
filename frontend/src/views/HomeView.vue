<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import ChatWindow from '../components/ChatWindow.vue'
import { isLoggedIn, getUser, logout } from '../api/auth'

const router = useRouter()
const loggedIn = computed(() => isLoggedIn())
const username = computed(() => getUser()?.username || '')

const handleLogout = () => {
  logout()
  router.push('/login')
}
</script>

<template>
  <main class="home">
    <section class="hero">
      <div class="hero-card">
        <div class="badge">LLM Custom Service</div>
        <h1 class="title">智能客服系统</h1>
        <p class="subtitle">
          支持多轮对话、转人工、反馈记录与后台报表分析。点击右下角气泡开始对话。
        </p>
        <div class="hero-actions">
          <router-link v-if="!loggedIn" to="/login" class="btn-primary">登录</router-link>
          <template v-else>
            <span class="btn-primary btn-user">用户：{{ username }}</span>
            <button class="btn-secondary btn-logout" @click="handleLogout">退出登录</button>
          </template>
          <router-link to="/admin" class="btn-secondary">后台管理</router-link>
        </div>
      </div>
    </section>

    <ChatWindow />
  </main>
</template>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.hero {
  width: 100%;
  display: flex;
  justify-content: center;
}

.hero-card {
  width: min(980px, 100%);
  border-radius: 18px;
  padding: clamp(18px, 3vw, 28px);
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(226, 232, 240, 0.9);
  box-shadow: 0 16px 45px rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(10px);
}

.badge {
  display: inline-flex;
  align-items: center;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.02em;
  color: #1d4ed8;
  background: rgba(59, 130, 246, 0.12);
  border: 1px solid rgba(59, 130, 246, 0.18);
}

.title {
  margin-top: 12px;
  font-size: clamp(28px, 4vw, 40px);
  letter-spacing: -0.02em;
  color: var(--text-primary);
}

.subtitle {
  margin-top: 10px;
  font-size: clamp(14px, 1.6vw, 16px);
  color: var(--text-secondary);
  max-width: 52rem;
}

.hero-actions {
  margin-top: 16px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.btn-user {
  display: inline-flex;
  align-items: center;
}

.btn-logout {
  border: none;
  cursor: pointer;
}
</style>
