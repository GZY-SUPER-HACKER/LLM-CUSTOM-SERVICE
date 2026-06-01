<template>
  <div class="conversations-view">
    <div class="conversations-header">
      <div class="search-box">
        <input type="text" v-model="searchQuery" placeholder="搜索对话..." />
        <button class="btn-search">搜索</button>
      </div>
    </div>
    
    <div v-if="loading" class="loading-container">
      <p>加载中...</p>
    </div>
    <div v-else-if="error" class="error-container">
      <p>{{ error }}</p>
      <button class="btn-retry" @click="fetchSessions">重试</button>
    </div>
    <div v-else>
      <div class="conversations-list">
        <div class="conversation-item" 
             v-for="session in filteredSessions" 
             :key="session.id"
             @click="selectSession(session)">
          <div class="conversation-row">
            <div class="conversation-info">
              <h4>会话 #{{ session.id }}</h4>
              <p class="conversation-user">用户: {{ session.user_id }}</p>
              <p class="conversation-time">开始时间: {{ formatDate(session.created_at) }}</p>
              <p class="conversation-meta"><strong>主题:</strong> {{ session.conversation_topic || 'N/A' }}</p>
              <p class="conversation-meta"><strong>意图:</strong> {{ session.user_intent || 'N/A' }}</p>
              <p class="conversation-meta"><strong>进程:</strong> {{ session.conversation_progress || 'N/A' }}</p>
            </div>
            <div class="conversation-actions">
              <button class="btn-view" @click.stop="selectSession(session)">查看</button>
              <button class="btn-danger" @click.stop="deleteSession(session)">删除</button>
            </div>
          </div>

          <!-- 详情：展开在当前会话条目下方 -->
          <div v-if="selectedSession && selectedSession.id === session.id" class="conversation-detail-inline" @click.stop>
            <div class="detail-actions">
              <button class="btn-close" @click="closeDetail">收起</button>
            </div>
            <div class="session-struct">
              <div class="struct-row"><span class="struct-k">主题</span><span class="struct-v">{{ selectedSession.conversation_topic || 'N/A' }}</span></div>
              <div class="struct-row"><span class="struct-k">意图</span><span class="struct-v">{{ selectedSession.user_intent || 'N/A' }}</span></div>
              <div class="struct-row"><span class="struct-k">进程</span><span class="struct-v">{{ selectedSession.conversation_progress || 'N/A' }}</span></div>
            </div>
            <div class="manual-records">
              <h4 class="manual-title">转人工记录</h4>
              <div v-if="manualRecords.length === 0" class="manual-empty">暂无转人工记录</div>
              <div v-else class="manual-list">
                <div v-for="r in manualRecords" :key="r.id" class="manual-item">
                  <div class="manual-meta">
                    <span class="manual-time">{{ formatDate(r.created_at) }}</span>
                    <span class="manual-tag">转人工</span>
                  </div>
                  <div class="manual-body">
                    <div class="manual-row"><span class="m-k">原因</span><span class="m-v">{{ r.transfer_reason || 'N/A' }}</span></div>
                    <div class="manual-row"><span class="m-k">备注</span><span class="m-v">{{ r.note || 'N/A' }}</span></div>
                    <div class="manual-row"><span class="m-k">情绪</span><span class="m-v">{{ r.emotion_type || 'N/A' }} / {{ r.emotion_level || 'N/A' }}</span></div>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="detailLoading" class="detail-loading">
              <p>加载消息中...</p>
            </div>
            <div v-else class="messages-list">
              <div class="message-item" 
                   v-for="message in selectedSession.messages" 
                   :key="message.id"
                   :class="{
                     'user-message': message.role === 'user',
                     'bot-message': message.role === 'assistant',
                     'support-message': message.role === 'support',
                     'system-message': message.role === 'system'
                   }">
                <div class="message-header">
                  <span class="message-role">
                    {{ message.role === 'user'
                      ? '用户'
                      : (message.role === 'assistant'
                        ? 'AI'
                        : (message.role === 'support'
                          ? '人工客服'
                          : '系统')) }}
                  </span>
                  <span class="message-time">{{ formatDate(message.created_at) }}</span>
                </div>
                <div class="message-content">
                  {{ message.content }}
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-if="sessions.length === 0" class="no-data">
          <p>暂无对话数据</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { sessionApi, manualApi } from '../../api/admin'

const sessions = ref([])
const selectedSession = ref(null)
const searchQuery = ref('')
const loading = ref(true)
const error = ref(null)
const detailLoading = ref(false)
const manualRecords = ref([])

const filteredSessions = computed(() => {
  let result = sessions.value
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(session => 
      session.id.toString().includes(query) || 
      session.user_id.toString().includes(query)
    )
  }
  return result
})

const fetchSessions = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await sessionApi.getSessions()
    sessions.value = response.data
  } catch (err) {
    console.error('获取对话数据失败:', err)
    error.value = '获取对话数据失败，请刷新页面重试'
    sessions.value = []
  } finally {
    loading.value = false
  }
}

const selectSession = async (session) => {
  detailLoading.value = true
  try {
    const [messagesRes, manualRes] = await Promise.all([
      sessionApi.getSessionMessages(session.id),
      manualApi.getManualBySession(session.id).catch(() => ({ data: [] }))
    ])
    selectedSession.value = {
      ...session,
      messages: messagesRes.data
    }
    manualRecords.value = manualRes.data || []
  } catch (err) {
    console.error('获取对话消息失败:', err)
    selectedSession.value = { ...session, messages: [] }
    manualRecords.value = []
  } finally {
    detailLoading.value = false
  }
}

const closeDetail = () => {
  selectedSession.value = null
  manualRecords.value = []
}

const deleteSession = async (session) => {
  if (!confirm(`确定删除会话 #${session.id} 吗？（会话消息也会一并删除）`)) return
  try {
    await sessionApi.deleteSession(session.id)
    if (selectedSession.value?.id === session.id) closeDetail()
    await fetchSessions()
  } catch (e) {
    console.error('删除会话失败:', e)
    alert('删除会话失败，请重试')
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  if (Number.isNaN(date.getTime())) return 'N/A'
  return date.toLocaleString()
}

onMounted(() => {
  fetchSessions()
})
</script>

<style scoped>
.conversations-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.conversations-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-box {
  display: flex;
  gap: 10px;
}

.search-box input {
  padding: 10px 12px;
  border: 1px solid #d8e2ff;
  border-radius: 10px;
  width: 300px;
}

.btn-search {
  background: linear-gradient(135deg, #4f73ff 0%, #6a8cff 100%);
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 10px;
  cursor: pointer;
}

.btn-search:hover {
  background: linear-gradient(135deg, #4368ef 0%, #5d7de8 100%);
}

.filter-box select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.conversations-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.conversation-item {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: stretch;
  background-color: white;
  border: 1px solid #e3eaff;
  border-radius: 14px;
  padding: 15px;
  box-shadow: 0 8px 22px rgba(29, 53, 87, 0.08);
  cursor: pointer;
  transition: all 0.3s ease;
}

.conversation-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.conversation-item:hover {
  box-shadow: 0 12px 24px rgba(29, 53, 87, 0.14);
}

.conversation-info h4 {
  margin: 0 0 5px 0;
  font-size: 16px;
  color: #333;
}

.conversation-user,
.conversation-time,
.conversation-status {
  margin: 3px 0;
  font-size: 14px;
  color: #666;
}

.status-active {
  color: #27ae60;
  font-weight: bold;
}

.status-ended {
  color: #95a5a6;
  font-weight: bold;
}

.btn-view {
  background-color: #4f73ff;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.btn-view:hover {
  background-color: #2980b9;
}

.btn-danger {
  background-color: #dd5c5c;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.btn-danger:hover {
  background-color: #c0392b;
}

.detail-actions {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 10px;
}

.no-data {
  padding: 40px;
  text-align: center;
  color: #999;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.conversation-detail-inline {
  margin-top: 12px;
  padding-top: 14px;
  border-top: 1px solid #e6edff;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ddd;
}

.detail-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.btn-close {
  background-color: #95a5a6;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-close:hover {
  background-color: #7f8c8d;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.message-item {
  max-width: 80%;
  padding: 10px 15px;
  border-radius: 10px;
}

.user-message {
  align-self: flex-start;
  background-color: #e3f2fd;
}

.bot-message {
  align-self: flex-end;
  background-color: #f1f1f1;
}

.support-message {
  align-self: flex-end;
  background-color: #e8f5e9;
}

.system-message {
  align-self: center;
  max-width: 95%;
  background-color: #fff3cd;
  color: #856404;
}

.session-struct {
  display: grid;
  grid-template-columns: 1fr;
  gap: 6px;
  padding: 10px 12px;
  border: 1px solid #eee;
  background: #fafafa;
  border-radius: 8px;
  margin-bottom: 12px;
}

.struct-row {
  display: flex;
  gap: 10px;
}

.struct-k {
  width: 70px;
  color: #666;
  font-weight: 600;
}

.struct-v {
  color: #333;
  flex: 1;
  word-break: break-word;
}

.manual-records {
  margin: 12px 0 10px;
  padding: 12px;
  border: 1px solid #eee;
  border-radius: 8px;
  background: #fff;
}

.manual-title {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #333;
}

.manual-empty {
  color: #999;
  font-size: 13px;
}

.manual-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.manual-item {
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  padding: 10px 12px;
  background: #fafafa;
}

.manual-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 12px;
  color: #666;
}

.manual-tag {
  background: #f39c12;
  color: #fff;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
}

.manual-row {
  display: flex;
  gap: 10px;
  font-size: 13px;
  margin: 4px 0;
}

.m-k {
  width: 48px;
  color: #666;
  font-weight: 600;
}

.m-v {
  flex: 1;
  color: #333;
  word-break: break-word;
}

.message-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  font-size: 12px;
  color: #666;
}

.message-role {
  font-weight: bold;
}

.message-content {
  font-size: 14px;
  line-height: 1.4;
}

@media (max-width: 768px) {
  .conversations-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .search-box input {
    width: 100%;
  }
  
  .message-item {
    max-width: 90%;
  }
}

.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 300px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
  text-align: center;
}

.error-container p {
  color: #e74c3c;
  margin-bottom: 20px;
}

.btn-retry {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-retry:hover {
  background-color: #2980b9;
}

.detail-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  background-color: #f8f9fa;
  border-radius: 8px;
  margin-top: 20px;
}
</style>