<template>
  <div class="logs-view">
    <div class="logs-header">
      <div class="search-box">
        <input type="text" v-model="searchQuery" placeholder="搜索日志..." />
        <button class="btn-search">搜索</button>
      </div>
      <div class="filter-box">
        <select v-model="levelFilter">
          <option value="all">全部级别</option>
          <option value="info">信息</option>
          <option value="warning">警告</option>
          <option value="error">错误</option>
        </select>
      </div>
    </div>
    
    <div v-if="loading" class="loading-container">
      <p>加载中...</p>
    </div>
    <div v-else-if="error" class="error-container">
      <p>{{ error }}</p>
      <button class="btn-retry" @click="fetchLogs">重试</button>
    </div>
    <div v-else>
      <div class="logs-table">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>时间</th>
              <th>级别</th>
              <th>模块</th>
              <th>消息</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in filteredLogs" :key="log.id">
              <td>{{ log.id }}</td>
              <td>{{ formatDate(log.created_at) }}</td>
              <td :class="`level-${log.level}`">{{ log.level }}</td>
              <td>{{ log.module || 'system' }}</td>
              <td>{{ log.message }}</td>
            </tr>
          </tbody>
        </table>
        <div v-if="logs.length === 0" class="no-data">
          <p>暂无日志数据</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { logApi } from '../../api/admin'

const logs = ref([])
const searchQuery = ref('')
const levelFilter = ref('all')
const loading = ref(true)
const error = ref(null)

const filteredLogs = computed(() => {
  let result = logs.value
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(log => 
      (log.message || '').toLowerCase().includes(query) || 
      (log.module || '').toLowerCase().includes(query)
    )
  }
  if (levelFilter.value !== 'all') {
    result = result.filter(log => (log.level || '').toLowerCase() === levelFilter.value)
  }
  return result
})

const fetchLogs = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await logApi.getLogs()
    logs.value = (response.data || []).map(l => ({
      ...l,
      level: (l.level || '').toLowerCase()
    }))
  } catch (err) {
    console.error('获取日志数据失败:', err)
    error.value = '获取日志数据失败，请刷新页面重试'
    logs.value = []
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  if (Number.isNaN(date.getTime())) return 'N/A'
  return date.toLocaleString()
}

onMounted(() => {
  fetchLogs()
})
</script>

<style scoped>
.logs-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.logs-header {
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
  padding: 10px 12px;
  border: 1px solid #d8e2ff;
  border-radius: 10px;
}

.logs-table {
  background-color: white;
  border: 1px solid #e3eaff;
  border-radius: 14px;
  box-shadow: 0 8px 22px rgba(29, 53, 87, 0.08);
  overflow: hidden;
}

.logs-table table {
  width: 100%;
  border-collapse: collapse;
}

.logs-table th,
.logs-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.logs-table th {
  background-color: #f2f6ff;
  font-weight: bold;
  font-size: 14px;
  color: #33456f;
}

.logs-table td {
  font-size: 14px;
}

.level-info {
  color: #3498db;
  font-weight: bold;
}

.level-warning {
  color: #f39c12;
  font-weight: bold;
}

.level-error {
  color: #e74c3c;
  font-weight: bold;
}

.no-data {
  padding: 40px;
  text-align: center;
  color: #999;
}

@media (max-width: 768px) {
  .logs-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .search-box input {
    width: 100%;
  }
  
  .logs-table {
    overflow-x: auto;
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