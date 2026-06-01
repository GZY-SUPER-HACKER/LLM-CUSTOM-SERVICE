<template>
  <div class="users-view">
    <div class="users-header">
      <div class="search-box">
        <input type="text" v-model="searchQuery" placeholder="搜索用户..." />
        <button class="btn-search">搜索</button>
      </div>
    </div>
    
    <div v-if="loading" class="loading-container">
      <p>加载中...</p>
    </div>
    <div v-else-if="error" class="error-container">
      <p>{{ error }}</p>
      <button class="btn-retry" @click="fetchUsers">重试</button>
    </div>
    <div v-else>
      <div class="users-table">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>用户名</th>
              <th>邮箱</th>
              <th>创建时间</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in filteredUsers" :key="user.id">
              <td>{{ user.id }}</td>
              <td>{{ user.username }}</td>
              <td>{{ user.email }}</td>
              <td>{{ formatDate(user.created_at) }}</td>
              <td :class="`status-${user.status}`">{{ user.status }}</td>
              <td>
                <button class="btn-delete" @click="deleteUser(user.id)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="users.length === 0" class="no-data">
          <p>暂无用户数据</p>
        </div>
      </div>
      
      <div class="pagination">
        <button class="btn-page" :disabled="currentPage === 1" @click="currentPage--">上一页</button>
        <span class="page-info">第 {{ currentPage }} 页，共 {{ totalPages }} 页</span>
        <button class="btn-page" :disabled="currentPage === totalPages" @click="currentPage++">下一页</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { userApi } from '../../api/admin'

const users = ref([])
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(true)
const error = ref(null)

const filteredUsers = computed(() => {
  let result = users.value
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(user => 
      user.username.toLowerCase().includes(query) || 
      user.email.toLowerCase().includes(query)
    )
  }
  return result
})

const totalPages = computed(() => {
  return Math.ceil(filteredUsers.value.length / pageSize.value)
})

const fetchUsers = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await userApi.getUsers()
    users.value = response.data
  } catch (err) {
    console.error('获取用户数据失败:', err)
    error.value = '获取用户数据失败：' + (err.response?.data?.detail || '请检查您的权限和网络连接')
    // 失败时不使用模拟数据，显示真实的错误信息
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString()
}

const editUser = (user) => {
  console.log('编辑用户:', user)
  // 这里将实现编辑用户的逻辑
}

const deleteUser = async (userId) => {
  if (confirm('确定要删除这个用户吗？')) {
    try {
      await userApi.deleteUser(userId)
      // 重新获取用户列表
      await fetchUsers()
    } catch (error) {
      console.error('删除用户失败:', error)
      alert('删除用户失败，请重试')
    }
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.users-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.users-header {
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
  background: #fff;
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

.btn-add {
  background-color: #27ae60;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-add:hover {
  background-color: #219a52;
}

.users-table {
  background-color: white;
  border: 1px solid #e3eaff;
  border-radius: 14px;
  box-shadow: 0 8px 22px rgba(29, 53, 87, 0.08);
  overflow: hidden;
}

.users-table table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th,
.users-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.users-table th {
  background-color: #f2f6ff;
  font-weight: bold;
  font-size: 14px;
  color: #33456f;
}

.users-table td {
  font-size: 14px;
}

.status-active {
  color: #27ae60;
  font-weight: bold;
}

.status-inactive {
  color: #e74c3c;
  font-weight: bold;
}

.btn-edit {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  margin-right: 5px;
}

.btn-edit:hover {
  background-color: #2980b9;
}

.btn-delete {
  background: linear-gradient(135deg, #e06666 0%, #d94a4a 100%);
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 12px;
}

.btn-delete:hover {
  background-color: #c0392b;
}

.no-data {
  padding: 40px;
  text-align: center;
  color: #999;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-top: 20px;
}

.btn-page {
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-page:hover:not(:disabled) {
  background-color: #e9ecef;
}

.btn-page:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #666;
}

@media (max-width: 768px) {
  .users-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .search-box input {
    width: 100%;
  }
  
  .users-table {
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