<template>
  <div class="dashboard">
    <div v-if="loading" class="loading-container">
      <p>加载中...</p>
    </div>
    <div v-else-if="error" class="error-container">
      <p>{{ error }}</p>
      <button class="btn-retry" @click="fetchDashboardData">重试</button>
    </div>
    <div v-else>
      <div class="dashboard-cards">
        <div class="dashboard-card">
          <h3>总用户数</h3>
          <p class="card-value">{{ userCount }}</p>
          <div class="card-footer">
            <span class="trend up">+12%</span>
            <span>较上月</span>
          </div>
        </div>
        <div class="dashboard-card">
          <h3>总对话数</h3>
          <p class="card-value">{{ sessionCount }}</p>
          <div class="card-footer">
            <span class="trend up">+8%</span>
            <span>较上月</span>
          </div>
        </div>
        <div class="dashboard-card">
          <h3>总消息数</h3>
          <p class="card-value">{{ messageCount }}</p>
          <div class="card-footer">
            <span class="trend up">+15%</span>
            <span>较上月</span>
          </div>
        </div>
        <div class="dashboard-card">
          <h3>反馈数</h3>
          <p class="card-value">{{ feedbackCount }}</p>
          <div class="card-footer">
            <span class="trend down">-2%</span>
            <span>较上月</span>
          </div>
        </div>
      </div>

      <div class="analysis-panel">
        <div class="analysis-header">
          <div>
            <h3>AI综合运营分析</h3>
            <p class="analysis-tip">基于对话历史、用户意图、反馈内容与转人工记录进行分点分析</p>
          </div>
          <div class="analysis-actions">
            <button class="btn-analyze" :disabled="analysisLoading" @click="runSummaryAnalysis">
              {{ analysisLoading ? '分析中...' : '一键分析' }}
            </button>
            <button class="btn-clear-analysis" :disabled="analysisLoading || !analysisSummary" @click="clearSummaryAnalysis">
              清除结果
            </button>
          </div>
        </div>
        <div class="analysis-content" v-if="analysisSummary">
          <p>{{ analysisSummary }}</p>
        </div>
        <div class="analysis-content empty" v-else>
          <p>点击“一键分析”后，系统将生成客服运行成果总结。</p>
        </div>
      </div>
      
      <div class="dashboard-charts">
        <div class="chart-container">
          <div class="chart-header">
            <h3>对话趋势</h3>
            <div class="chart-actions">
              <button v-if="!isPreviewMode" class="btn-secondary" @click="enablePreview">预览示例</button>
              <button v-else class="btn-secondary" @click="disablePreview">取消预览</button>
            </div>
          </div>
          <div class="chart-canvas">
            <canvas ref="trendCanvas"></canvas>
          </div>
        </div>
        <div class="chart-container">
          <div class="chart-header">
            <h3>用户分布</h3>
            <div class="chart-actions">
              <button v-if="!isPreviewMode" class="btn-secondary" @click="enablePreview">预览示例</button>
              <button v-else class="btn-secondary" @click="disablePreview">取消预览</button>
            </div>
          </div>
          <div class="chart-canvas">
            <canvas ref="userDistCanvas"></canvas>
          </div>
        </div>
      </div>
      
      <div class="dashboard-stats">
        <h3>最近活动</h3>
        <div class="activity-table">
          <table>
            <thead>
              <tr>
                <th>时间</th>
                <th>用户</th>
                <th>活动</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="activity in recentActivities" :key="activity.id">
                <td>{{ activity.time }}</td>
                <td>{{ activity.user }}</td>
                <td>{{ activity.action }}</td>
                <td :class="`status-${activity.status}`">{{ activity.status }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import Chart from 'chart.js/auto'
import { userApi, sessionApi, messageApi, feedbackApi, analysisApi } from '../../api/admin'

const userCount = ref(0)
const sessionCount = ref(0)
const messageCount = ref(0)
const feedbackCount = ref(0)
const recentActivities = ref([])
const loading = ref(true)
const error = ref(null)
const isPreviewMode = ref(false)
const analysisLoading = ref(false)
const analysisSummary = ref('')
const analysisStorageKey = 'admin_dashboard_analysis_summary'

let lastRealUsers = []
let lastRealSessions = []

const trendCanvas = ref(null)
const userDistCanvas = ref(null)
let trendChart = null
let userDistChart = null

const safeDate = (value) => {
  if (!value) return null
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return null
  return d
}

const fmt = (value) => {
  const d = safeDate(value)
  return d ? d.toLocaleString() : 'N/A'
}

const buildConversationTrend = (sessions, days = 14) => {
  const now = new Date()
  const start = new Date(now)
  start.setDate(now.getDate() - (days - 1))
  start.setHours(0, 0, 0, 0)

  const labels = []
  const counts = new Array(days).fill(0)
  for (let i = 0; i < days; i++) {
    const d = new Date(start)
    d.setDate(start.getDate() + i)
    labels.push(`${d.getMonth() + 1}/${d.getDate()}`)
  }

  for (const s of sessions) {
    const d = safeDate(s.created_at)
    if (!d) continue
    const day = new Date(d)
    day.setHours(0, 0, 0, 0)
    const idx = Math.floor((day - start) / (24 * 60 * 60 * 1000))
    if (idx >= 0 && idx < days) counts[idx] += 1
  }

  return { labels, counts }
}

const buildUserDistribution = (users) => {
  const map = new Map()
  for (const u of users) {
    const role = u.role || 'user'
    map.set(role, (map.get(role) || 0) + 1)
  }
  const labels = Array.from(map.keys())
  const counts = labels.map(l => map.get(l))
  return { labels, counts }
}

const randomInt = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min

const buildRandomConversationTrend = (days = 14) => {
  const now = new Date()
  const start = new Date(now)
  start.setDate(now.getDate() - (days - 1))
  start.setHours(0, 0, 0, 0)
  const labels = []
  const counts = []
  for (let i = 0; i < days; i++) {
    const d = new Date(start)
    d.setDate(start.getDate() + i)
    labels.push(`${d.getMonth() + 1}/${d.getDate()}`)
    counts.push(randomInt(5, 80))
  }
  return { labels, counts }
}

const buildRandomUserDistribution = () => {
  const labels = ['user', 'support', 'admin']
  const counts = [randomInt(20, 200), randomInt(1, 15), randomInt(1, 5)]
  return { labels, counts }
}

const renderCharts = ({ users, sessions }) => {
  if (trendChart) trendChart.destroy()
  if (userDistChart) userDistChart.destroy()
  if (!trendCanvas.value || !userDistCanvas.value) return

  const trend = isPreviewMode.value ? buildRandomConversationTrend(14) : buildConversationTrend(sessions, 14)
  trendChart = new Chart(trendCanvas.value.getContext('2d'), {
    type: 'line',
    data: {
      labels: trend.labels,
      datasets: [
        {
          label: '会话数',
          data: trend.counts,
          borderColor: '#3498db',
          backgroundColor: 'rgba(52, 152, 219, 0.15)',
          tension: 0.25,
          fill: true
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true, ticks: { precision: 0 } } }
    }
  })

  const dist = isPreviewMode.value ? buildRandomUserDistribution() : buildUserDistribution(users)
  userDistChart = new Chart(userDistCanvas.value.getContext('2d'), {
    type: 'doughnut',
    data: {
      labels: dist.labels,
      datasets: [
        {
          data: dist.counts,
          backgroundColor: ['#3498db', '#27ae60', '#f39c12', '#9b59b6', '#95a5a6']
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } }
    }
  })
}

const enablePreview = () => {
  isPreviewMode.value = true
  renderCharts({ users: lastRealUsers, sessions: lastRealSessions })
}

const disablePreview = () => {
  isPreviewMode.value = false
  renderCharts({ users: lastRealUsers, sessions: lastRealSessions })
}

const runSummaryAnalysis = async () => {
  analysisLoading.value = true
  try {
    const response = await analysisApi.getSummary()
    analysisSummary.value = response.data?.summary || '分析完成，但未获取到有效总结内容。'
    localStorage.setItem(analysisStorageKey, analysisSummary.value)
  } catch (err) {
    console.error('AI综合分析失败:', err)
    analysisSummary.value = '分析失败，请稍后重试。'
  } finally {
    analysisLoading.value = false
  }
}

const clearSummaryAnalysis = () => {
  analysisSummary.value = ''
  localStorage.removeItem(analysisStorageKey)
}

// 真实API调用获取数据
const fetchDashboardData = async () => {
  loading.value = true
  error.value = null
  try {
    const [users, sessions, messages, feedbacks] = await Promise.all([
      userApi.getUsers(),
      sessionApi.getSessions(),
      messageApi.getMessages(),
      feedbackApi.listFeedbacks({ limit: 200 })
    ])
    
    // 计算统计数据
    userCount.value = users.data.length
    sessionCount.value = sessions.data.length
    messageCount.value = messages.data.length
    feedbackCount.value = feedbacks.data.length

    lastRealUsers = users.data
    lastRealSessions = sessions.data
    
    // 构建最近活动数据
    recentActivities.value = [
      ...sessions.data
        .slice()
        .sort((a, b) => (safeDate(b.created_at) || 0) - (safeDate(a.created_at) || 0))
        .slice(0, 3)
        .map(session => ({
        id: session.id,
        time: fmt(session.created_at),
        user: `用户${session.user_id}`,
        action: '发起对话',
        status: 'success'
      })),
      ...feedbacks.data
        .slice()
        .sort((a, b) => (safeDate(b.timestamp) || 0) - (safeDate(a.timestamp) || 0))
        .slice(0, 2)
        .map(f => ({
          id: `feedback-${f.id}`,
          time: fmt(f.timestamp),
          user: `${f.user_id}`,
          action: `提交反馈(${f.feedback_type})`,
          status: 'info'
        }))
    ].slice(0, 5)

    // 关键：先让页面从 loading 切换到内容区，canvas 才会挂载
    loading.value = false
    await nextTick()
    renderCharts({ users: lastRealUsers, sessions: lastRealSessions })
    return
  } catch (err) {
    console.error('获取仪表盘数据失败:', err)
    error.value = '获取数据失败，请刷新页面重试'
    userCount.value = 0
    sessionCount.value = 0
    messageCount.value = 0
    feedbackCount.value = 0
    recentActivities.value = []
    loading.value = false
  }
}

onMounted(() => {
  analysisSummary.value = localStorage.getItem(analysisStorageKey) || ''
  fetchDashboardData()
})

onBeforeUnmount(() => {
  if (trendChart) trendChart.destroy()
  if (userDistChart) userDistChart.destroy()
})
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.dashboard-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.dashboard-card {
  background: linear-gradient(180deg, #ffffff 0%, #f7f9ff 100%);
  border: 1px solid #e8edff;
  border-radius: 14px;
  padding: 22px;
  box-shadow: 0 8px 24px rgba(29, 53, 87, 0.08);
}

.dashboard-card h3 {
  font-size: 14px;
  color: #666;
  margin: 0 0 10px 0;
}

.card-value {
  font-size: 30px;
  font-weight: bold;
  margin: 0 0 12px 0;
  color: #1f2d5a;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #999;
}

.trend.up {
  color: #27ae60;
  font-weight: bold;
}

.trend.down {
  color: #e74c3c;
  font-weight: bold;
}

.dashboard-charts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.chart-container {
  background-color: #ffffff;
  border: 1px solid #e8edff;
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 8px 22px rgba(29, 53, 87, 0.08);
}

.chart-container h3 {
  font-size: 16px;
  color: #333;
  margin: 0 0 15px 0;
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.chart-actions {
  display: flex;
  gap: 8px;
}

.btn-secondary {
  background-color: #7486ff;
  color: white;
  border: none;
  padding: 6px 10px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 12px;
}

.btn-secondary:hover {
  background-color: #5f70e4;
}

.chart-canvas {
  height: 240px;
}

.dashboard-stats {
  background-color: #ffffff;
  border: 1px solid #e8edff;
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 8px 22px rgba(29, 53, 87, 0.08);
}

.analysis-panel {
  background: linear-gradient(135deg, #f7f8ff 0%, #f0f8ff 100%);
  border: 1px solid #dfe8ff;
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 8px 22px rgba(31, 45, 90, 0.08);
}

.analysis-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.analysis-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.analysis-header h3 {
  margin: 0 0 4px 0;
  font-size: 18px;
  color: #20305a;
}

.analysis-tip {
  margin: 0;
  color: #61739a;
  font-size: 13px;
}

.btn-analyze {
  border: none;
  border-radius: 10px;
  padding: 10px 16px;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(135deg, #4d73ff 0%, #6a8bff 100%);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 8px 16px rgba(77, 115, 255, 0.24);
}

.btn-analyze:hover:not(:disabled) {
  transform: translateY(-1px);
}

.btn-analyze:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.btn-clear-analysis {
  border: 1px solid #cad6ff;
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 13px;
  font-weight: 600;
  color: #4c5c86;
  background: #f5f7ff;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-clear-analysis:hover:not(:disabled) {
  background: #ecf1ff;
}

.btn-clear-analysis:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.analysis-content {
  margin-top: 14px;
  background: #fff;
  border-radius: 10px;
  border: 1px solid #e5ebff;
  padding: 14px 16px;
}

.analysis-content p {
  margin: 0;
  line-height: 1.8;
  color: #2e3d64;
  white-space: pre-line;
}

.analysis-content.empty p {
  color: #7a88a8;
}

.dashboard-stats h3 {
  font-size: 16px;
  color: #333;
  margin: 0 0 15px 0;
}

.activity-table table {
  width: 100%;
  border-collapse: collapse;
}

.activity-table th,
.activity-table td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.activity-table th {
  background-color: #e9ecef;
  font-weight: bold;
  font-size: 14px;
}

.activity-table td {
  font-size: 14px;
}

.status-success {
  color: #27ae60;
  font-weight: bold;
}

.status-info {
  color: #3498db;
  font-weight: bold;
}

.status-warning {
  color: #f39c12;
  font-weight: bold;
}

@media (max-width: 768px) {
  .dashboard-charts {
    grid-template-columns: 1fr;
  }

  .analysis-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .analysis-actions {
    width: 100%;
    justify-content: flex-start;
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