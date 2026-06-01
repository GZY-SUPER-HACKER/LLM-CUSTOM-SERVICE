<template>
  <div class="feedback-view">
    <div class="feedback-header">
      <div class="search-box">
        <input type="text" v-model="searchQuery" placeholder="搜索反馈..." />
        <button class="btn-search">搜索</button>
      </div>
    </div>
    
    <div v-if="loading" class="loading-container">
      <p>加载中...</p>
    </div>
    <div v-else-if="error" class="error-container">
      <p>{{ error }}</p>
      <button class="btn-retry" @click="fetchFeedback">重试</button>
    </div>
    <div v-else>
      <div class="feedback-table">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>来源</th>
              <th>消息ID</th>
              <th>用户ID</th>
              <th>会话ID</th>
              <th>反馈类型</th>
              <th>反馈内容</th>
              <th>提交时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="feedback in filteredFeedback" :key="feedback.id">
              <td>{{ feedback.id }}</td>
              <td :class="`source-${feedback.feedback_source}`">{{ feedback.feedback_source === 'manual_text' ? '文字反馈' : '对话反馈' }}</td>
              <td>{{ feedback.message_id }}</td>
              <td>{{ feedback.user_id }}</td>
              <td>{{ feedback.session_id }}</td>
              <td>{{ feedback.feedback_type }}</td>
              <td>{{ feedback.content || '-' }}</td>
              <td>{{ formatDate(feedback.timestamp) }}</td>
              <td>
                <div class="row-actions">
                  <button class="btn-view" @click="viewFeedback(feedback.id)">查看</button>
                  <button class="btn-danger" @click="deleteOne(feedback.id)">删除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="feedback.length === 0" class="no-data">
          <p>暂无反馈数据</p>
        </div>
      </div>
      
      <div v-if="selectedFeedback" class="feedback-detail">
        <div class="detail-header">
          <h3>反馈详情 #{{ selectedFeedback.id }}</h3>
          <button class="btn-close" @click="closeDetail">关闭</button>
        </div>
        <div class="detail-content">
          <div class="detail-item">
            <label>消息ID:</label>
            <span>{{ selectedFeedback.message_id }}</span>
          </div>
          <div class="detail-item">
            <label>用户ID:</label>
            <span>{{ selectedFeedback.user_id }}</span>
          </div>
          <div class="detail-item">
            <label>会话ID:</label>
            <span>{{ selectedFeedback.session_id }}</span>
          </div>
          <div class="detail-item">
            <label>反馈类型:</label>
            <span>{{ selectedFeedback.feedback_type }}</span>
          </div>
          <div class="detail-item">
            <label>反馈来源:</label>
            <span>{{ selectedFeedback.feedback_source === 'manual_text' ? '文字反馈' : '对话反馈' }}</span>
          </div>
          <div class="detail-item">
            <label>反馈内容:</label>
            <span>{{ selectedFeedback.content || '-' }}</span>
          </div>
          <div class="detail-item">
            <label>提交时间:</label>
            <span>{{ formatDate(selectedFeedback.timestamp) }}</span>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { feedbackApi } from '../../api/admin'

const feedback = ref([])
const selectedFeedback = ref(null)
const searchQuery = ref('')
const loading = ref(true)
const error = ref(null)

const filteredFeedback = computed(() => {
  let result = feedback.value
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(item => 
      item.id.toString().includes(query) || 
      item.message_id.toString().includes(query) || 
      item.user_id.toString().includes(query) ||
      (item.content || '').toLowerCase().includes(query)
    )
  }
  return result
})

const fetchFeedback = async () => {
  loading.value = true
  error.value = null
  try {
    const [chatRes, textRes] = await Promise.all([
      feedbackApi.listFeedbacks({ limit: 200 }),
      feedbackApi.listTextFeedbacks({ limit: 200 })
    ])

    const chatItems = (chatRes.data || []).map(item => ({
      ...item,
      feedback_source: 'chat_reaction',
      content: ''
    }))
    const textItems = (textRes.data || []).map(item => ({
      id: `text-${item.id}`,
      rawId: item.id,
      message_id: '-',
      user_id: item.user_id,
      session_id: item.session_id || '-',
      feedback_type: 'text',
      timestamp: item.timestamp,
      status: item.status,
      feedback_source: 'manual_text',
      content: item.content
    }))

    feedback.value = [...chatItems, ...textItems].sort(
      (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    )
  } catch (err) {
    console.error('获取反馈数据失败:', err)
    error.value = '获取反馈数据失败，请刷新页面重试'
    feedback.value = []
  } finally {
    loading.value = false
  }
}

const processFeedback = async (feedbackId) => {
  try {
    await feedbackApi.updateFeedbackStatus(feedbackId, 'processed')
    // 重新获取反馈列表
    await fetchFeedback()
  } catch (error) {
    console.error('处理反馈失败:', error)
    alert('处理反馈失败，请重试')
  }
}

const viewFeedback = (feedbackId) => {
  // 这里将从API获取反馈详情
  selectedFeedback.value = feedback.value.find(item => item.id === feedbackId)
}

const deleteOne = async (feedbackId) => {
  if (!confirm(`确定删除反馈 #${feedbackId} 吗？`)) return
  try {
    const target = feedback.value.find(f => f.id === feedbackId)
    if (target?.feedback_source === 'manual_text') {
      await feedbackApi.deleteTextFeedback(target.rawId)
    } else {
      await feedbackApi.deleteFeedback(feedbackId)
    }
    if (selectedFeedback.value?.id === feedbackId) selectedFeedback.value = null
    await fetchFeedback()
  } catch (e) {
    console.error('删除反馈失败:', e)
    alert('删除反馈失败，请重试')
  }
}

const closeDetail = () => {
  selectedFeedback.value = null
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  if (Number.isNaN(date.getTime())) return 'N/A'
  return date.toLocaleString()
}

onMounted(() => {
  fetchFeedback()
})
</script>

<style scoped>
.feedback-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.feedback-header {
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
  background-color: #2980b9;
}

.filter-box select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.feedback-table {
  background-color: white;
  border: 1px solid #e3eaff;
  border-radius: 14px;
  box-shadow: 0 8px 22px rgba(29, 53, 87, 0.08);
  overflow: hidden;
}

.feedback-table table {
  width: 100%;
  border-collapse: collapse;
}

.feedback-table th,
.feedback-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.feedback-table th {
  background-color: #f2f6ff;
  font-weight: bold;
  font-size: 14px;
  color: #33456f;
}

.feedback-table td {
  font-size: 14px;
}

.source-chat_reaction {
  color: #4f73ff;
  font-weight: 600;
}

.source-manual_text {
  color: #0f766e;
  font-weight: 600;
}

.status-pending {
  color: #f39c12;
  font-weight: bold;
}

.status-processed {
  color: #27ae60;
  font-weight: bold;
}

.btn-process {
  background-color: #27ae60;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  margin-right: 5px;
}

.btn-process:hover {
  background-color: #219a52;
}

.btn-view {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.btn-view:hover {
  background-color: #2980b9;
}

.btn-danger {
  background-color: #e74c3c;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  margin-left: 6px;
}

.btn-danger:hover {
  background-color: #c0392b;
}

.row-actions {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.row-actions .btn-view,
.row-actions .btn-danger {
  margin: 0;
}

.no-data {
  padding: 40px;
  text-align: center;
  color: #999;
}

.feedback-detail {
  background-color: white;
  border: 1px solid #e3eaff;
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 8px 22px rgba(29, 53, 87, 0.08);
  margin-top: 20px;
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

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.detail-item {
  display: flex;
  gap: 10px;
}

.detail-item label {
  width: 120px;
  font-weight: bold;
  color: #333;
}

.detail-actions {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ddd;
}

@media (max-width: 768px) {
  .feedback-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .search-box input {
    width: 100%;
  }
  
  .feedback-table {
    overflow-x: auto;
  }
  
  .detail-item {
    flex-direction: column;
    gap: 5px;
  }
  
  .detail-item label {
    width: 100%;
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
</style>