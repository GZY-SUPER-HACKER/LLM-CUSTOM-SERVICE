<template>
  <div class="admin-container">
    <div class="admin-sidebar">
      <h2>后台管理</h2>
      <ul class="admin-menu">
        <li @click="activeTab = 'dashboard'" :class="{ active: activeTab === 'dashboard' }">
          <span class="menu-icon">📊</span>
          <span>报表分析</span>
        </li>
        <li @click="activeTab = 'users'" :class="{ active: activeTab === 'users' }">
          <span class="menu-icon">👥</span>
          <span>用户管理</span>
        </li>
        <li @click="activeTab = 'conversations'" :class="{ active: activeTab === 'conversations' }">
          <span class="menu-icon">💬</span>
          <span>对话历史</span>
        </li>
        <li @click="activeTab = 'feedback'" :class="{ active: activeTab === 'feedback' }">
          <span class="menu-icon">⭐</span>
          <span>反馈管理</span>
        </li>
        <li @click="activeTab = 'logs'" :class="{ active: activeTab === 'logs' }">
          <span class="menu-icon">📋</span>
          <span>系统日志</span>
        </li>
        <li @click="activeTab = 'knowledge'" :class="{ active: activeTab === 'knowledge' }">
          <span class="menu-icon">🧠</span>
          <span>知识库管理</span>
        </li>
      </ul>

    </div>
    <div class="admin-content">
      <div class="admin-header">
        <h1>{{ getPageTitle() }}</h1>

      </div>
      <div class="admin-body">
        <component :is="activeComponent" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import DashboardView from './admin/DashboardView.vue'
import UsersView from './admin/UsersView.vue'
import ConversationsView from './admin/ConversationsView.vue'
import FeedbackView from './admin/FeedbackView.vue'
import LogsView from './admin/LogsView.vue'
import KnowledgeBaseView from './admin/KnowledgeBaseView.vue'

const router = useRouter()
const activeTab = ref('dashboard')

const activeComponent = computed(() => {
  switch (activeTab.value) {
    case 'dashboard': return DashboardView
    case 'users': return UsersView
    case 'conversations': return ConversationsView
    case 'feedback': return FeedbackView
    case 'logs': return LogsView
    case 'knowledge': return KnowledgeBaseView
    default: return DashboardView
  }
})

const getPageTitle = () => {
  switch (activeTab.value) {
    case 'dashboard': return '报表分析'
    case 'users': return '用户管理'
    case 'conversations': return '对话历史记录'
    case 'feedback': return '反馈管理'
    case 'logs': return '系统日志'
    case 'knowledge': return '知识库管理'
    default: return '后台管理'
  }
}

onMounted(() => {
  // 不需要获取用户信息，因为管理员页面不需要使用登录内容
})
</script>

<style scoped>
.admin-container {
  display: flex;
  height: 100vh;
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: linear-gradient(135deg, #eef3ff 0%, #f6f9ff 100%);
}

.admin-sidebar {
  width: 260px;
  background: linear-gradient(180deg, #1b2a4a 0%, #1f3561 100%);
  color: white;
  padding: 24px 18px;
  display: flex;
  flex-direction: column;
  height: 100vh;
  box-shadow: 8px 0 28px rgba(18, 29, 52, 0.2);
}

.admin-sidebar h2 {
  margin-bottom: 28px;
  text-align: center;
  font-size: 20px;
  letter-spacing: 0.5px;
}

.admin-menu {
  list-style: none;
  padding: 0;
}

.admin-menu li {
  display: flex;
  align-items: center;
  padding: 12px 14px;
  margin-bottom: 10px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.admin-menu li:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.admin-menu li.active {
  background: linear-gradient(135deg, #4f73ff 0%, #6a8cff 100%);
  box-shadow: 0 10px 18px rgba(79, 115, 255, 0.3);
}

.menu-icon {
  margin-right: 10px;
  font-size: 18px;
}

.user-info {
  margin-top: auto;
  padding: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.user-details {
  margin-bottom: 10px;
}

.user-name {
  display: block;
  font-weight: bold;
  margin-bottom: 5px;
}

.user-role {
  display: block;
  font-size: 12px;
  opacity: 0.8;
}

.btn-logout {
  width: 100%;
  background-color: #e74c3c;
  color: white;
  border: none;
  padding: 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-logout:hover {
  background-color: #c0392b;
}

.admin-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 10px 2px 16px;
  border-bottom: 1px solid #dfe6ff;
}

.admin-header h1 {
  font-size: 28px;
  color: #1f2d5a;
  margin: 0;
  letter-spacing: 0.3px;
}

.admin-actions {
  display: flex;
  gap: 10px;
}

.btn-primary {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary:hover {
  background-color: #2980b9;
}

.btn-secondary {
  background-color: #95a5a6;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-secondary:hover {
  background-color: #7f8c8d;
}

.admin-body {
  background-color: #f7f9ff;
  border: 1px solid #e3eaff;
  border-radius: 16px;
  padding: 22px;
  box-shadow: 0 10px 26px rgba(27, 42, 74, 0.08);
}
</style>