<template>
  <div class="debug-container">
    <h1 class="debug-title">系统调试中心</h1>
    
    <!-- 导航标签 -->
    <div class="debug-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        :class="['debug-tab', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        {{ tab.name }}
      </button>
    </div>
    
    <!-- 内容区域 -->
    <div class="debug-content">
      <!-- 系统状态 -->
      <div v-if="activeTab === 'status'" class="debug-panel">
        <h2>系统状态</h2>
        <div class="status-grid">
          <div class="status-card" :class="{ 'status-ok': systemStatus.status === 'ok' }">
            <h3>系统状态</h3>
            <p>{{ systemStatus.status === 'ok' ? '正常运行' : '异常' }}</p>
            <p class="status-time">{{ systemStatus.timestamp }}</p>
          </div>
          
          <div class="status-card" :class="{ 'status-ok': dbStatus.status === 'connected' }">
            <h3>数据库连接</h3>
            <p>{{ dbStatus.status === 'connected' ? '已连接' : '未连接' }}</p>
            <p class="status-detail">{{ dbStatus.details }}</p>
          </div>
          
          <div class="status-card" :class="{ 'status-ok': llmStatus.status === 'available' }">
            <h3>LLM服务</h3>
            <p>{{ llmStatus.status === 'available' ? '可用' : '不可用' }}</p>
            <p class="status-detail">{{ llmStatus.model }}</p>
          </div>
          
          <div class="status-card" :class="{ 'status-ok': redisStatus.status === 'connected' }">
            <h3>Redis缓存</h3>
            <p>{{ redisStatus.status === 'connected' ? '已连接' : '未连接' }}</p>
            <p class="status-detail">{{ redisStatus.details }}</p>
          </div>
        </div>
        
        <!-- 性能指标 -->
        <div class="performance-section">
          <h3>性能指标</h3>
          <div class="performance-grid">
            <div class="performance-card">
              <h4>CPU使用率</h4>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: performance.cpu + '%' }"></div>
              </div>
              <p>{{ performance.cpu }}%</p>
            </div>
            
            <div class="performance-card">
              <h4>内存使用率</h4>
              <div class="progress-bar">
                <div class="progress-fill memory" :style="{ width: performance.memory + '%' }"></div>
              </div>
              <p>{{ performance.memory }}%</p>
            </div>
            
            <div class="performance-card">
              <h4>磁盘使用率</h4>
              <div class="progress-bar">
                <div class="progress-fill disk" :style="{ width: performance.disk + '%' }"></div>
              </div>
              <p>{{ performance.disk }}%</p>
            </div>
            
            <div class="performance-card">
              <h4>网络延迟</h4>
              <p>{{ performance.network }}ms</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 接口调用记录 -->
      <div v-if="activeTab === 'api'" class="debug-panel">
        <h2>接口调用记录</h2>
        <div class="api-filter">
          <select v-model="apiFilter">
            <option value="all">全部接口</option>
            <option value="chat">聊天接口</option>
            <option value="knowledge">知识接口</option>
            <option value="feedback">反馈接口</option>
          </select>
          <button @click="clearApiLogs">清空记录</button>
          <button @click="refreshApiLogs" class="refresh-btn">刷新</button>
        </div>
        
        <div class="api-logs">
          <table class="api-table">
            <thead>
              <tr>
                <th>时间</th>
                <th>接口</th>
                <th>方法</th>
                <th>状态码</th>
                <th>响应时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="log in filteredApiLogs" :key="log.id" :class="{ 'error': log.status >= 400 }">
                <td>{{ log.timestamp }}</td>
                <td>{{ log.endpoint }}</td>
                <td>{{ log.method }}</td>
                <td :class="{ 'status-ok': log.status < 400, 'status-error': log.status >= 400 }">
                  {{ log.status }}
                </td>
                <td>{{ log.responseTime }}ms</td>
                <td>
                  <button @click="viewApiDetail(log)" class="detail-btn">详情</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- 接口详情模态框 -->
        <div v-if="showApiDetail" class="modal">
          <div class="modal-content">
            <h3>接口详情</h3>
            <div class="api-detail">
              <p><strong>时间:</strong> {{ selectedApiLog.timestamp }}</p>
              <p><strong>接口:</strong> {{ selectedApiLog.endpoint }}</p>
              <p><strong>方法:</strong> {{ selectedApiLog.method }}</p>
              <p><strong>状态码:</strong> {{ selectedApiLog.status }}</p>
              <p><strong>响应时间:</strong> {{ selectedApiLog.responseTime }}ms</p>
              <p><strong>请求:</strong></p>
              <pre>{{ selectedApiLog.request }}</pre>
              <p><strong>响应:</strong></p>
              <pre>{{ selectedApiLog.response }}</pre>
            </div>
            <button @click="showApiDetail = false" class="close-btn">关闭</button>
          </div>
        </div>
      </div>
      
      <!-- 错误日志 -->
      <div v-if="activeTab === 'logs'" class="debug-panel">
        <h2>错误日志</h2>
        <div class="log-filter">
          <select v-model="logLevel">
            <option value="all">全部级别</option>
            <option value="error">错误</option>
            <option value="warning">警告</option>
            <option value="info">信息</option>
          </select>
          <button @click="clearLogs">清空日志</button>
          <button @click="refreshLogs" class="refresh-btn">刷新</button>
        </div>
        
        <div class="log-list">
          <div v-for="log in filteredLogs" :key="log.id" :class="['log-item', log.level]">
            <div class="log-header">
              <span class="log-time">{{ log.timestamp }}</span>
              <span class="log-level" :class="log.level">{{ log.level.toUpperCase() }}</span>
            </div>
            <div class="log-content">
              <p>{{ log.message }}</p>
              <p v-if="log.details" class="log-details">{{ log.details }}</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 环境配置 -->
      <div v-if="activeTab === 'config'" class="debug-panel">
        <h2>环境配置</h2>
        <div class="config-grid">
          <div class="config-card">
            <h3>服务器配置</h3>
            <ul class="config-list">
              <li v-for="(value, key) in serverConfig" :key="key">
                <strong>{{ key }}:</strong> {{ value }}
              </li>
            </ul>
          </div>
          
          <div class="config-card">
            <h3>数据库配置</h3>
            <ul class="config-list">
              <li v-for="(value, key) in dbConfig" :key="key">
                <strong>{{ key }}:</strong> {{ value }}
              </li>
            </ul>
          </div>
          
          <div class="config-card">
            <h3>LLM配置</h3>
            <ul class="config-list">
              <li v-for="(value, key) in llmConfig" :key="key">
                <strong>{{ key }}:</strong> {{ value }}
              </li>
            </ul>
          </div>
          
          <div class="config-card">
            <h3>前端配置</h3>
            <ul class="config-list">
              <li v-for="(value, key) in frontendConfig" :key="key">
                <strong>{{ key }}:</strong> {{ value }}
              </li>
            </ul>
          </div>
        </div>
      </div>
      
      <!-- 测试工具 -->
      <div v-if="activeTab === 'tools'" class="debug-panel">
        <h2>测试工具</h2>
        
        <div class="test-section">
          <h3>接口测试</h3>
          <div class="test-form">
            <select v-model="testEndpoint">
              <option value="/chat/send_message">聊天接口</option>
              <option value="/knowledge/search">知识搜索</option>
              <option value="/feedback">反馈接口</option>
            </select>
            <textarea v-model="testPayload" placeholder="输入请求参数..."></textarea>
            <button @click="testApi" class="test-btn">测试接口</button>
          </div>
          
          <div v-if="testResult" class="test-result">
            <h4>测试结果</h4>
            <pre>{{ testResult }}</pre>
          </div>
        </div>
        
        <div class="test-section">
          <h3>系统诊断</h3>
          <button @click="runDiagnostics" class="diagnostic-btn">运行诊断</button>
          <div v-if="diagnosticResult" class="diagnostic-result">
            <h4>诊断结果</h4>
            <div v-for="(result, key) in diagnosticResult" :key="key" class="diagnostic-item">
              <span class="diagnostic-name">{{ key }}:</span>
              <span :class="{ 'status-ok': result.status === 'ok', 'status-error': result.status === 'error' }">
                {{ result.status }}
              </span>
              <span v-if="result.message" class="diagnostic-message">{{ result.message }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 对话分析 -->
      <div v-if="activeTab === 'analysis'" class="debug-panel">
        <h2>对话消息情绪与意图分析</h2>
        <p class="panel-description">展示每条对话消息的情绪识别和意图识别结果</p>

        <div class="analysis-header">
          <div class="analysis-info">
            <span class="info-label">会话ID:</span>
            <span class="info-value">{{ analysisSessionId }}</span>
          </div>
          <div class="analysis-actions">
            <button @click="refreshAnalysis" class="refresh-btn">刷新分析</button>
            <select v-model="selectedSessionForAnalysis" @change="loadSessionMessages">
              <option value="">选择会话</option>
              <option v-for="session in availableSessions" :key="session.id" :value="session.id">
                会话 #{{ session.id }} - {{ session.title }}
              </option>
            </select>
          </div>
        </div>

        <div class="analysis-messages">
          <div v-if="analysisMessages.length === 0" class="empty-state">
            <p>暂无对话数据，请选择会话或刷新</p>
          </div>
          <div v-else v-for="(msg, index) in analysisMessages" :key="index" class="analysis-message-item">
            <div class="message-header">
              <span class="message-role" :class="msg.role">
                {{ msg.role === 'user' ? '用户' : 'AI助手' }}
              </span>
              <span class="message-time">{{ msg.timestamp }}</span>
            </div>
            <div class="message-body">
              <div class="message-content-section">
                <h4>消息内容</h4>
                <p class="message-text">{{ msg.content }}</p>
              </div>

              <div class="analysis-results">
                <div class="analysis-section emotion-section">
                  <h4>
                    <span class="section-icon">🎭</span>
                    情绪识别结果
                  </h4>
                  <div class="analysis-grid">
                    <div class="analysis-item">
                      <span class="item-label">情绪类型:</span>
                      <span class="item-value emotion-type" :class="'emotion-' + msg.emotionResult?.emotion_type">
                        {{ getEmotionTypeText(msg.emotionResult?.emotion_type) }}
                      </span>
                    </div>
                    <div class="analysis-item">
                      <span class="item-label">情绪强度:</span>
                      <span class="item-value">
                        {{ msg.emotionResult?.intensity_level || '轻微' }}
                        <span class="intensity-score">({{ (msg.emotionResult?.intensity * 100).toFixed(0) }}%)</span>
                      </span>
                    </div>
                    <div class="analysis-item">
                      <span class="item-label">置信度:</span>
                      <span class="item-value confidence">{{ (msg.emotionResult?.confidence * 100).toFixed(0) }}%</span>
                    </div>
                  </div>
                  <div v-if="msg.emotionResult?.suggestion" class="suggestion-box">
                    <span class="suggestion-label">建议:</span>
                    <span class="suggestion-text">{{ msg.emotionResult.suggestion }}</span>
                  </div>
                </div>

                <div class="analysis-section intent-section">
                  <h4>
                    <span class="section-icon">🎯</span>
                    意图识别结果
                  </h4>
                  <div class="analysis-grid">
                    <div class="analysis-item">
                      <span class="item-label">意图类别:</span>
                      <span class="item-value intent-type">{{ getIntentTypeText(msg.intentResult?.intent_type) }}</span>
                    </div>
                    <div class="analysis-item">
                      <span class="item-label">置信度:</span>
                      <span class="item-value confidence">{{ (msg.intentResult?.confidence * 100).toFixed(0) }}%</span>
                    </div>
                    <div class="analysis-item">
                      <span class="item-label">识别方式:</span>
                      <span class="item-value method">{{ msg.intentResult?.method === 'rule_based' ? '规则匹配' : 'LLM分析' }}</span>
                    </div>
                  </div>
                  <div v-if="msg.intentResult?.confidence_level" class="confidence-level">
                    <span class="level-label">确定程度:</span>
                    <span class="level-badge" :class="'level-' + msg.intentResult?.confidence_level?.toLowerCase().replace(/\s/g, '-')">
                      {{ msg.intentResult.confidence_level }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 上下文管理 -->
      <div v-if="activeTab === 'context'" class="debug-panel">
        <h2>上下文结构化信息管理</h2>
        <p class="panel-description">展示和管理会话上下文中的结构化信息</p>

        <div class="context-header">
          <div class="context-info">
            <span class="info-label">当前会话:</span>
            <span class="info-value">#{{ contextSessionId }}</span>
          </div>
          <button @click="refreshContext" class="refresh-btn">刷新上下文</button>
        </div>

        <div class="structured-info-section">
          <h3>结构化信息概览</h3>
          <div class="info-cards">
            <div v-for="(info, index) in structuredInfo" :key="index" class="info-card">
              <div class="card-header">
                <span class="card-index">#{{ index + 1 }}</span>
                <span class="card-type-badge" :class="'type-' + info.type?.toLowerCase()">
                  {{ getInfoTypeText(info.type) }}
                </span>
              </div>
              <div class="card-body">
                <div class="card-field">
                  <span class="field-label">信息类型</span>
                  <span class="field-value">{{ info.type || '未分类' }}</span>
                </div>
                <div class="card-field">
                  <span class="field-label">生成时间戳</span>
                  <span class="field-value timestamp">{{ formatTimestamp(info.timestamp) }}</span>
                </div>
                <div class="card-field content-field">
                  <span class="field-label">具体内容</span>
                  <div class="field-content">{{ info.content }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="context-details-section">
          <h3>完整上下文数据</h3>
          <div class="context-data">
            <pre>{{ JSON.stringify(contextData, null, 2) }}</pre>
          </div>
        </div>
      </div>

      <!-- 情绪调试 -->
      <div v-if="activeTab === 'emotion'" class="debug-panel emotion-debug-panel">
        <h2>情绪识别实时调试</h2>
        <p class="panel-description">输入文本进行情绪识别测试，实时查看识别结果和转人工判断</p>

        <!-- 测试输入区域 -->
        <div class="emotion-test-section">
          <div class="test-input-wrapper">
            <textarea
              v-model="emotionTestInput"
              class="emotion-input"
              placeholder="请输入要测试的文本..."
              rows="4"
            ></textarea>
            <div class="test-input-actions">
              <button @click="testEmotion" :disabled="isAnalyzingEmotion" class="analyze-btn">
                {{ isAnalyzingEmotion ? '分析中...' : '分析情绪' }}
              </button>
              <button @click="emotionTestInput = ''; emotionTestResult = null" class="clear-btn">
                清空
              </button>
            </div>
          </div>

          <!-- 预设测试语料 -->
          <div class="preset-test-cases">
            <span class="preset-label">快速测试:</span>
            <button @click="emotionTestInput = '我非常满意你们的服务！'" class="preset-btn">正面</button>
            <button @click="emotionTestInput = '这个东西太差了，我要投诉！'" class="preset-btn">愤怒</button>
            <button @click="emotionTestInput = '我真的不知道该怎么办了...'" class="preset-btn">焦虑</button>
            <button @click="emotionTestInput = '等了好久都没人理我！'" class="preset-btn">沮丧</button>
            <button @click="emotionTestInput = '这个政策太不合理了！'" class="preset-btn">不满</button>
          </div>
        </div>

        <!-- 实时结果展示 -->
        <div v-if="emotionTestResult" class="emotion-result-section">
          <div v-if="emotionTestResult.status === 'error'" class="error-result">
            <h4>错误</h4>
            <p>{{ emotionTestResult.message }}</p>
            <pre>{{ emotionTestResult.detail }}</pre>
          </div>

          <div v-else class="result-card">
            <!-- 情绪类型和强度 -->
            <div class="result-header">
              <div class="emotion-badge" :style="{ backgroundColor: getEmotionColor(emotionTestResult.emotion_result?.emotion_type) }">
                <span class="emotion-icon">{{ getEmotionIcon(emotionTestResult.emotion_result?.emotion_type) }}</span>
                <span class="emotion-name">{{ getEmotionTypeText(emotionTestResult.emotion_result?.emotion_type) }}</span>
              </div>
              <div class="intensity-display">
                <span class="intensity-label">强度:</span>
                <div class="intensity-bar-wrapper">
                  <div class="intensity-bar">
                    <div
                      class="intensity-fill"
                      :class="getIntensityClass(emotionTestResult.emotion_result?.intensity)"
                      :style="{ width: (emotionTestResult.emotion_result?.intensity * 100) + '%' }"
                    ></div>
                  </div>
                  <span class="intensity-value">{{ (emotionTestResult.emotion_result?.intensity * 100).toFixed(0) }}%</span>
                </div>
              </div>
            </div>

            <!-- 多维度分析 -->
            <div class="multi-dim-section">
              <h4>多维度分析</h4>
              <div class="dim-grid">
                <div class="dim-item">
                  <span class="dim-label">语气激烈程度</span>
                  <div class="dim-bar-wrapper">
                    <div class="dim-bar">
                      <div
                        class="dim-fill tone"
                        :style="{ width: (emotionTestResult.emotion_result?.multi_dimensional_analysis?.tone_intensity * 100) + '%' }"
                      ></div>
                    </div>
                    <span class="dim-value">{{ (emotionTestResult.emotion_result?.multi_dimensional_analysis?.tone_intensity * 100).toFixed(0) }}%</span>
                  </div>
                </div>
                <div class="dim-item">
                  <span class="dim-label">负面情绪程度</span>
                  <div class="dim-bar-wrapper">
                    <div class="dim-bar">
                      <div
                        class="dim-fill negative"
                        :style="{ width: (emotionTestResult.emotion_result?.multi_dimensional_analysis?.negative_emotion_degree * 100) + '%' }"
                      ></div>
                    </div>
                    <span class="dim-value">{{ (emotionTestResult.emotion_result?.multi_dimensional_analysis?.negative_emotion_degree * 100).toFixed(0) }}%</span>
                  </div>
                </div>
                <div class="dim-item">
                  <span class="dim-label">诉求紧急程度</span>
                  <div class="dim-bar-wrapper">
                    <div class="dim-bar">
                      <div
                        class="dim-fill urgency"
                        :style="{ width: (emotionTestResult.emotion_result?.multi_dimensional_analysis?.urgency_level * 100) + '%' }"
                      ></div>
                    </div>
                    <span class="dim-value">{{ (emotionTestResult.emotion_result?.multi_dimensional_analysis?.urgency_level * 100).toFixed(0) }}%</span>
                  </div>
                </div>
                <div class="dim-item">
                  <span class="dim-label">失控风险</span>
                  <div class="dim-bar-wrapper">
                    <div class="dim-bar">
                      <div
                        class="dim-fill risk"
                        :style="{ width: (emotionTestResult.emotion_result?.multi_dimensional_analysis?.loss_of_control_risk * 100) + '%' }"
                      ></div>
                    </div>
                    <span class="dim-value">{{ (emotionTestResult.emotion_result?.multi_dimensional_analysis?.loss_of_control_risk * 100).toFixed(0) }}%</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 转人工判断 -->
            <div class="transfer-section" :class="{ 'transfer-yes': emotionTestResult.should_transfer, 'transfer-no': !emotionTestResult.should_transfer }">
              <div class="transfer-badge">
                <span class="transfer-icon">{{ emotionTestResult.should_transfer ? '⚠️' : '✅' }}</span>
                <span class="transfer-text">
                  {{ emotionTestResult.should_transfer ? '建议转人工' : '正常处理' }}
                </span>
              </div>
              <p class="transfer-reason">{{ emotionTestResult.transfer_reason }}</p>
            </div>

            <!-- 其他信息 -->
            <div class="result-details">
              <div class="detail-item">
                <span class="detail-label">识别方式:</span>
                <span class="detail-value">{{ emotionTestResult.emotion_result?.method === 'llm_based' ? 'LLM分析' : '关键词匹配' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">置信度:</span>
                <span class="detail-value">{{ (emotionTestResult.emotion_result?.confidence * 100).toFixed(0) }}%</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">情绪激动:</span>
                <span class="detail-value" :class="{ 'agitated': emotionTestResult.emotion_result?.is_emotionally_agitated }">
                  {{ emotionTestResult.emotion_result?.is_emotionally_agitated ? '是' : '否' }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 历史记录 -->
        <div class="emotion-history-section">
          <div class="history-header">
            <h3>识别历史</h3>
            <div class="history-actions">
              <button @click="loadEmotionHistory" class="refresh-btn">刷新</button>
              <button @click="clearEmotionCache" class="clear-history-btn">清空</button>
            </div>
          </div>

          <div class="stats-overview">
            <div class="stat-card">
              <span class="stat-value">{{ emotionStats.cache_size }}</span>
              <span class="stat-label">缓存数量</span>
            </div>
            <div v-for="(stats, emotion) in emotionStats.emotion_distribution" :key="emotion" class="stat-card emotion-stat">
              <span class="stat-value" :style="{ color: getEmotionColor(emotion) }">{{ stats.count }}</span>
              <span class="stat-label">{{ getEmotionTypeText(emotion) }}</span>
            </div>
          </div>

          <div class="history-list">
            <div v-if="emotionHistory.length === 0" class="empty-history">
              暂无历史记录
            </div>
            <div v-else v-for="(item, index) in emotionHistory" :key="index" class="history-item">
              <div class="history-text">{{ item.text }}</div>
              <div class="history-result">
                <span class="history-emotion" :style="{ backgroundColor: getEmotionColor(item.result.emotion_type) }">
                  {{ getEmotionTypeText(item.result.emotion_type) }}
                </span>
                <span class="history-intensity">{{ (item.result.intensity * 100).toFixed(0) }}%</span>
                <span v-if="item.result.is_emotionally_agitated" class="history-agitated">⚠️</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

// 状态管理
const activeTab = ref('status')
const apiFilter = ref('all')
const logLevel = ref('all')
const showApiDetail = ref(false)
const selectedApiLog = ref(null)
const testEndpoint = ref('/chat/send_message')
const testPayload = ref('{"user_id": 1, "user_input": "你好", "session_id": null}')
const testResult = ref(null)
const diagnosticResult = ref(null)

// 对话分析相关状态
const analysisSessionId = ref('1')
const selectedSessionForAnalysis = ref('')
const analysisMessages = ref([])
const availableSessions = ref([
  { id: 1, title: '产品咨询' },
  { id: 2, title: '售后服务' },
  { id: 3, title: '投诉建议' }
])

// 上下文管理相关状态
const contextSessionId = ref('1')
const structuredInfo = ref([
  {
    type: 'conversation_topic',
    timestamp: new Date().toLocaleString(),
    content: '用户咨询产品退货流程及相关政策'
  },
  {
    type: 'user_intent',
    timestamp: new Date().toLocaleString(),
    content: 'after_sales - 售后服务类咨询，涉及退货政策和流程'
  },
  {
    type: 'conversation_progress',
    timestamp: new Date().toLocaleString(),
    content: '对话进行中，用户询问退货流程，AI已提供详细说明'
  }
])
const contextData = ref({
  session_id: 1,
  user_id: 1,
  conversation_topic: '产品退货咨询',
  user_intent: 'after_sales',
  user_emotion: 'neutral',
  confidence: 0.85,
  conversation_progress: '用户询问退货流程，AI已提供详细说明',
  context_management: {
    topic: '产品退货咨询',
    intent: 'after_sales',
    emotion: 'neutral',
    progress: '对话进行中'
  }
})

// 情绪调试相关状态
const emotionTestInput = ref('')
const emotionTestResult = ref(null)
const emotionHistory = ref([])
const emotionStats = ref({
  cache_size: 0,
  emotion_distribution: {}
})
const isAnalyzingEmotion = ref(false)
const emotionHistoryFilter = ref('all')

// 标签页配置
const tabs = [
  { id: 'status', name: '系统状态' },
  { id: 'api', name: '接口调用' },
  { id: 'logs', name: '错误日志' },
  { id: 'config', name: '环境配置' },
  { id: 'tools', name: '测试工具' },
  { id: 'analysis', name: '对话分析' },
  { id: 'context', name: '上下文管理' },
  { id: 'emotion', name: '情绪调试' }
]

// 系统状态数据
const systemStatus = ref({
  status: 'ok',
  timestamp: new Date().toLocaleString()
})

const dbStatus = ref({
  status: 'connected',
  details: 'MySQL 8.0.30'
})

const llmStatus = ref({
  status: 'available',
  model: 'DeepSeek'
})

const redisStatus = ref({
  status: 'connected',
  details: 'Redis 7.0+'
})

// 性能指标
const performance = ref({
  cpu: 25,
  memory: 45,
  disk: 60,
  network: 120
})

// API调用记录
const apiLogs = ref([
  {
    id: 1,
    timestamp: '2026-04-21 10:00:00',
    endpoint: '/chat/send_message',
    method: 'POST',
    status: 200,
    responseTime: 150,
    request: '{"user_id": 1, "user_input": "你好", "session_id": null}',
    response: '{"id": 1, "content": "你好！我是智能客服助手，有什么可以帮助你的吗？"}'
  },
  {
    id: 2,
    timestamp: '2026-04-21 10:01:00',
    endpoint: '/knowledge/search',
    method: 'POST',
    status: 200,
    responseTime: 80,
    request: '{"query": "如何退货"}',
    response: '{"results": [{"title": "退货政策", "content": "..."}]}'
  },
  {
    id: 3,
    timestamp: '2026-04-21 10:02:00',
    endpoint: '/feedback',
    method: 'POST',
    status: 400,
    responseTime: 50,
    request: '{"message_id": "msg_123", "feedback_type": "satisfied"}',
    response: '{"detail": "缺少必要参数"}'
  }
])

// 错误日志
const logs = ref([
  {
    id: 1,
    timestamp: '2026-04-21 09:50:00',
    level: 'error',
    message: '数据库连接失败',
    details: 'Connection refused: connect ECONNREFUSED 127.0.0.1:3306'
  },
  {
    id: 2,
    timestamp: '2026-04-21 09:55:00',
    level: 'warning',
    message: 'LLM API响应超时',
    details: 'Request timed out after 3000ms'
  },
  {
    id: 3,
    timestamp: '2026-04-21 10:00:00',
    level: 'info',
    message: '系统启动成功',
    details: 'Server started on port 8000'
  }
])

// 配置信息
const serverConfig = ref({
  '服务器地址': 'http://127.0.0.1:8000',
  '运行环境': 'development',
  'Python版本': '3.11.0',
  'FastAPI版本': '0.104.0'
})

const dbConfig = ref({
  '数据库类型': 'MySQL',
  '主机地址': '127.0.0.1',
  '端口': '3306',
  '数据库名': 'llm_chatbot'
})

const llmConfig = ref({
  '模型': 'DeepSeek',
  'API提供商': '火山引擎',
  '温度参数': '0.7',
  '最大token': '4096'
})

const frontendConfig = ref({
  'Vue版本': '3.5.31',
  'Vue Router': '5.0.4',
  '构建模式': 'development',
  'API基础URL': 'http://127.0.0.1:8000'
})

// 计算属性
const filteredApiLogs = computed(() => {
  if (apiFilter.value === 'all') {
    return apiLogs.value
  }
  return apiLogs.value.filter(log => log.endpoint.includes(apiFilter.value))
})

const filteredLogs = computed(() => {
  if (logLevel.value === 'all') {
    return logs.value
  }
  return logs.value.filter(log => log.level === logLevel.value)
})

// 方法
const viewApiDetail = (log) => {
  selectedApiLog.value = log
  showApiDetail.value = true
}

const clearApiLogs = () => {
  apiLogs.value = []
}

const refreshApiLogs = () => {
  // 模拟刷新数据
  apiLogs.value = [
    ...apiLogs.value,
    {
      id: Date.now(),
      timestamp: new Date().toLocaleString(),
      endpoint: '/chat/send_message',
      method: 'POST',
      status: 200,
      responseTime: Math.floor(Math.random() * 200) + 50,
      request: '{"user_id": 1, "user_input": "测试刷新", "session_id": null}',
      response: '{"id": ' + Date.now() + ', "content": "测试响应"}'
    }
  ]
}

const clearLogs = () => {
  logs.value = []
}

const refreshLogs = () => {
  // 模拟刷新数据
  logs.value = [
    ...logs.value,
    {
      id: Date.now(),
      timestamp: new Date().toLocaleString(),
      level: 'info',
      message: '日志刷新测试',
      details: '手动刷新日志'
    }
  ]
}

const testApi = async () => {
  try {
    const payload = JSON.parse(testPayload.value)
    const response = await axios.post(`http://127.0.0.1:8000${testEndpoint.value}`, payload)
    testResult.value = JSON.stringify(response.data, null, 2)
  } catch (error) {
    testResult.value = `错误: ${error.message}\n${JSON.stringify(error.response?.data, null, 2) || '无响应数据'}`
  }
}

const runDiagnostics = async () => {
  try {
    // 模拟诊断结果
    diagnosticResult.value = {
      '系统状态': { status: 'ok', message: '系统运行正常' },
      '数据库连接': { status: 'ok', message: '数据库连接正常' },
      'LLM服务': { status: 'ok', message: 'LLM服务可用' },
      'Redis缓存': { status: 'ok', message: 'Redis连接正常' },
      'API接口': { status: 'ok', message: '所有接口响应正常' }
    }
  } catch (error) {
    diagnosticResult.value = {
      '系统诊断': { status: 'error', message: '诊断失败: ' + error.message }
    }
  }
}

// 对话分析相关方法
const loadSessionMessages = async () => {
  if (!selectedSessionForAnalysis.value) {
    analysisMessages.value = [
      {
        id: 1,
        role: 'user',
        content: '你好，我想咨询一下你们的退货政策是怎样的？',
        timestamp: '2026-04-25 10:30:00',
        emotionResult: {
          emotion_type: 'neutral',
          intensity: 0.2,
          intensity_level: '轻微',
          confidence: 0.85,
          suggestion: '对话正常进行'
        },
        intentResult: {
          intent_type: 'after_sales',
          confidence: 0.88,
          confidence_level: '确定',
          method: 'rule_based'
        }
      },
      {
        id: 2,
        role: 'ai',
        content: '您好！感谢您的咨询。我们的退货政策如下：\n1. 商品在收到后7天内可以申请退货\n2. 商品需保持原包装完整\n3. 退货时请提供订单编号\n请问您还有什么其他问题吗？',
        timestamp: '2026-04-25 10:30:15',
        emotionResult: null,
        intentResult: null
      },
      {
        id: 3,
        role: 'user',
        content: '已经超过7天了，但商品有质量问题，这种情况下可以退货吗？',
        timestamp: '2026-04-25 10:31:00',
        emotionResult: {
          emotion_type: 'frustrated',
          intensity: 0.6,
          intensity_level: '中等',
          confidence: 0.82,
          suggestion: '用户情绪略显急躁，建议耐心解答'
        },
        intentResult: {
          intent_type: 'after_sales',
          confidence: 0.92,
          confidence_level: '非常确定',
          method: 'rule_based'
        }
      }
    ]
  }
}

const refreshAnalysis = () => {
  loadSessionMessages()
}

// 上下文管理相关方法
const refreshContext = () => {
  structuredInfo.value = structuredInfo.value.map(info => ({
      ...info,
      timestamp: new Date().toLocaleString()
    }))
}

// 情绪调试相关方法
const testEmotion = async () => {
  if (!emotionTestInput.value.trim()) {
    return
  }
  isAnalyzingEmotion.value = true
  try {
    const response = await axios.post('http://127.0.0.1:8000/debug/emotion/recognize', null, {
      params: { user_input: emotionTestInput.value }
    })
    emotionTestResult.value = response.data
  } catch (error) {
    emotionTestResult.value = {
      status: 'error',
      message: error.message,
      detail: error.response?.data || '无响应数据'
    }
  } finally {
    isAnalyzingEmotion.value = false
  }
}

const loadEmotionHistory = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/debug/emotion/history')
    emotionHistory.value = response.data.history || []
    emotionStats.value = response.data.statistics || { cache_size: 0, emotion_distribution: {} }
  } catch (error) {
    console.error('加载情绪历史失败:', error)
  }
}

const clearEmotionCache = async () => {
  try {
    await axios.delete('http://127.0.0.1:8000/debug/emotion/cache')
    emotionHistory.value = []
    emotionStats.value = { cache_size: 0, emotion_distribution: {} }
  } catch (error) {
    console.error('清空缓存失败:', error)
  }
}

const getEmotionColor = (emotionType) => {
  const colorMap = {
    'neutral': '#6b7280',
    'happy': '#10b981',
    'satisfied': '#059669',
    'angry': '#ef4444',
    'frustrated': '#f97316',
    'anxious': '#f59e0b',
    'sad': '#6366f1',
    'disappointed': '#8b5cf6',
    'surprised': '#ec4899',
    'confused': '#a855f7',
    'emotionally_agitated': '#dc2626'
  }
  return colorMap[emotionType] || '#6b7280'
}

const getIntensityClass = (intensity) => {
  if (intensity >= 0.8) return 'extreme'
  if (intensity >= 0.6) return 'strong'
  if (intensity >= 0.3) return 'moderate'
  return 'mild'
}

const getEmotionIcon = (emotionType) => {
  const iconMap = {
    'neutral': '😐',
    'happy': '😊',
    'satisfied': '😄',
    'angry': '😠',
    'frustrated': '😤',
    'anxious': '😰',
    'sad': '😢',
    'disappointed': '😞',
    'surprised': '😮',
    'confused': '😕',
    'emotionally_agitated': '🔥'
  }
  return iconMap[emotionType] || '😐'
}

// 辅助函数
const getEmotionTypeText = (emotionType) => {
  const emotionMap = {
    'neutral': '中性',
    'happy': '开心',
    'satisfied': '满意',
    'angry': '生气',
    'frustrated': '沮丧',
    'anxious': '焦虑',
    'sad': '悲伤',
    'disappointed': '失望',
    'surprised': '惊讶',
    'confused': '困惑'
  }
  return emotionMap[emotionType] || '未知'
}

const getIntentTypeText = (intentType) => {
  const intentMap = {
    'consultation': '咨询',
    'after_sales': '售后',
    'info_query': '信息查询',
    'transfer_human': '转人工',
    'complaint': '投诉',
    'technical_support': '技术支持',
    'product_suggestion': '产品建议',
    'chitchat': '闲聊',
    'other': '其他'
  }
  return intentMap[intentType] || '未知'
}

const getInfoTypeText = (type) => {
  const typeMap = {
    'conversation_topic': '对话主题',
    'user_intent': '用户意图',
    'user_emotion': '用户情绪',
    'conversation_progress': '对话进展',
    'context_summary': '上下文摘要'
  }
  return typeMap[type] || type || '未分类'
}

const formatTimestamp = (timestamp) => {
  if (!timestamp) return '未知'
  return timestamp
}

// 生命周期
onMounted(() => {
  // 模拟实时数据更新
  setInterval(() => {
    systemStatus.value.timestamp = new Date().toLocaleString()
    performance.value.cpu = Math.floor(Math.random() * 30) + 10
    performance.value.memory = Math.floor(Math.random() * 20) + 40
  }, 5000)

  // 初始化对话分析数据
  loadSessionMessages()
})
</script>

<style scoped>
.debug-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.debug-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 20px;
  color: #333;
}

.debug-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 10px;
}

.debug-tab {
  padding: 10px 20px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background: #f5f5f5;
  cursor: pointer;
  transition: all 0.3s ease;
}

.debug-tab:hover {
  background: #e0e0e0;
}

.debug-tab.active {
  background: #4f46e5;
  color: white;
  border-color: #4f46e5;
}

.debug-panel {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.debug-panel h2 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
  color: #333;
}

/* 系统状态 */
.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.status-card {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid #e0e0e0;
}

.status-card.status-ok {
  border-left-color: #10b981;
  background: #f0fdf4;
}

.status-card h3 {
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
}

.status-card p {
  font-size: 16px;
  font-weight: 500;
  margin: 0;
}

.status-time {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.status-detail {
  font-size: 12px;
  color: #666;
  margin-top: 5px;
}

/* 性能指标 */
.performance-section {
  margin-top: 30px;
}

.performance-section h3 {
  font-size: 16px;
  margin-bottom: 15px;
}

.performance-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.performance-card {
  background: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
}

.performance-card h4 {
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progress-fill {
  height: 100%;
  background: #3b82f6;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-fill.memory {
  background: #f59e0b;
}

.progress-fill.disk {
  background: #ef4444;
}

/* API调用记录 */
.api-filter {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  align-items: center;
}

.api-filter select {
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

.api-filter button {
  padding: 8px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background: #f5f5f5;
  cursor: pointer;
  transition: all 0.3s ease;
}

.api-filter button:hover {
  background: #e0e0e0;
}

.api-filter .refresh-btn {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.api-filter .refresh-btn:hover {
  background: #2563eb;
}

.api-table {
  width: 100%;
  border-collapse: collapse;
}

.api-table th,
.api-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

.api-table th {
  background: #f9f9f9;
  font-weight: 600;
  font-size: 14px;
  color: #333;
}

.api-table tr:hover {
  background: #f5f5f5;
}

.api-table tr.error {
  background: #fef2f2;
}

.status-ok {
  color: #10b981;
  font-weight: 500;
}

.status-error {
  color: #ef4444;
  font-weight: 500;
}

.detail-btn {
  padding: 4px 8px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.detail-btn:hover {
  background: #2563eb;
}

/* 模态框 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  max-width: 800px;
  max-height: 80vh;
  overflow-y: auto;
  width: 90%;
}

.modal-content h3 {
  margin-top: 0;
  margin-bottom: 20px;
}

.api-detail pre {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 10px 0;
  font-size: 12px;
}

.close-btn {
  margin-top: 20px;
  padding: 8px 16px;
  background: #6b7280;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.close-btn:hover {
  background: #4b5563;
}

/* 错误日志 */
.log-filter {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  align-items: center;
}

.log-filter select {
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

.log-filter button {
  padding: 8px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background: #f5f5f5;
  cursor: pointer;
  transition: all 0.3s ease;
}

.log-filter button:hover {
  background: #e0e0e0;
}

.log-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.log-item {
  background: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid #e0e0e0;
}

.log-item.error {
  border-left-color: #ef4444;
  background: #fef2f2;
}

.log-item.warning {
  border-left-color: #f59e0b;
  background: #fffbeb;
}

.log-item.info {
  border-left-color: #3b82f6;
  background: #eff6ff;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.log-time {
  font-size: 12px;
  color: #666;
}

.log-level {
  font-size: 12px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
}

.log-level.error {
  background: #fef2f2;
  color: #ef4444;
}

.log-level.warning {
  background: #fffbeb;
  color: #f59e0b;
}

.log-level.info {
  background: #eff6ff;
  color: #3b82f6;
}

.log-content p {
  margin: 0;
  font-size: 14px;
}

.log-details {
  margin-top: 5px;
  font-size: 12px;
  color: #666;
}

/* 环境配置 */
.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.config-card {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
}

.config-card h3 {
  font-size: 16px;
  margin-bottom: 15px;
  color: #333;
}

.config-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.config-list li {
  padding: 8px 0;
  border-bottom: 1px solid #e0e0e0;
  font-size: 14px;
}

.config-list li:last-child {
  border-bottom: none;
}

.config-list strong {
  display: inline-block;
  width: 100px;
  color: #666;
}

/* 测试工具 */
.test-section {
  margin-bottom: 30px;
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
}

.test-section h3 {
  font-size: 16px;
  margin-bottom: 15px;
}

.test-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.test-form select {
  padding: 10px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

.test-form textarea {
  padding: 10px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  height: 100px;
  resize: vertical;
}

.test-btn {
  padding: 10px 20px;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.test-btn:hover {
  background: #059669;
}

.test-result {
  background: white;
  padding: 15px;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.test-result pre {
  margin: 10px 0 0 0;
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
}

.diagnostic-btn {
  padding: 10px 20px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.diagnostic-btn:hover {
  background: #2563eb;
}

.diagnostic-result {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.diagnostic-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: white;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.diagnostic-name {
  font-weight: 500;
  min-width: 100px;
}

.diagnostic-message {
  margin-left: auto;
  font-size: 14px;
  color: #666;
}

/* 对话分析样式 */
.panel-description {
  color: #666;
  font-size: 14px;
  margin-bottom: 20px;
}

.analysis-header,
.context-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
}

.analysis-info,
.context-info {
  display: flex;
  gap: 10px;
  align-items: center;
}

.info-label {
  font-weight: 500;
  color: #666;
}

.info-value {
  font-weight: 600;
  color: #333;
}

.analysis-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.analysis-actions select {
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

.analysis-messages {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.empty-state {
  text-align: center;
  padding: 40px;
  background: #f9f9f9;
  border-radius: 8px;
  color: #666;
}

.analysis-message-item {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.analysis-message-item .message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  background: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
}

.analysis-message-item .message-role {
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 12px;
}

.analysis-message-item .message-role.user {
  background: #dbeafe;
  color: #1d4ed8;
}

.analysis-message-item .message-role.ai {
  background: #dcfce7;
  color: #15803d;
}

.analysis-message-item .message-time {
  font-size: 12px;
  color: #666;
}

.analysis-message-item .message-body {
  padding: 15px;
}

.message-content-section {
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e0e0e0;
}

.message-content-section h4,
.analysis-section h4 {
  font-size: 14px;
  margin: 0 0 10px 0;
  color: #333;
}

.message-text {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
}

.analysis-results {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.analysis-section {
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
}

.emotion-section {
  border-left: 4px solid #f59e0b;
}

.intent-section {
  border-left: 4px solid #3b82f6;
}

.analysis-section h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.section-icon {
  font-size: 16px;
}

.analysis-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.analysis-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.item-label {
  font-size: 13px;
  color: #666;
}

.item-value {
  font-size: 13px;
  font-weight: 500;
  color: #333;
}

.emotion-type {
  padding: 2px 8px;
  border-radius: 4px;
}

.emotion-type.emotion-neutral { background: #f3f4f6; }
.emotion-type.emotion-happy { background: #fef3c7; color: #92400e; }
.emotion-type.emotion-satisfied { background: #d1fae5; color: #065f46; }
.emotion-type.emotion-angry { background: #fee2e2; color: #991b1b; }
.emotion-type.emotion-frustrated { background: #fed7aa; color: #9a3412; }
.emotion-type.emotion-anxious { background: #fef9c3; color: #854d0e; }
.emotion-type.emotion-sad { background: #e0e7ff; color: #3730a3; }
.emotion-type.emotion-disappointed { background: #fce7f3; color: #9d174d; }
.emotion-type.emotion-surprised { background: #ccfbf1; color: #115e59; }
.emotion-type.emotion-confused { background: #f3e8ff; color: #6b21a8; }

.intent-type {
  padding: 2px 8px;
  border-radius: 4px;
  background: #eff6ff;
  color: #1d4ed8;
}

.confidence {
  color: #059669;
}

.intensity-score {
  color: #666;
  font-size: 12px;
}

.suggestion-box {
  margin-top: 10px;
  padding: 10px;
  background: white;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
  font-size: 13px;
}

.suggestion-label {
  font-weight: 500;
  color: #666;
}

.suggestion-text {
  color: #333;
}

.confidence-level {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
}

.level-label {
  font-size: 13px;
  color: #666;
}

.level-badge {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
}

.level-very-high {
  background: #d1fae5;
  color: #065f46;
}

.level-high {
  background: #fef3c7;
  color: #92400e;
}

.level-medium {
  background: #e0e7ff;
  color: #3730a3;
}

.level-low,
.level-very-low {
  background: #f3f4f6;
  color: #4b5563;
}

/* 上下文管理样式 */
.structured-info-section {
  margin-bottom: 30px;
}

.structured-info-section h3 {
  font-size: 16px;
  margin-bottom: 15px;
  color: #333;
}

.info-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.info-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.info-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  background: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
}

.card-index {
  font-weight: 600;
  color: #333;
}

.card-type-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.card-type-badge.type-conversation_topic {
  background: #dbeafe;
  color: #1d4ed8;
}

.card-type-badge.type-user_intent {
  background: #dcfce7;
  color: #15803d;
}

.card-type-badge.type-conversation_progress {
  background: #fef3c7;
  color: #92400e;
}

.card-type-badge.type-user_emotion {
  background: #fce7f3;
  color: #9d174d;
}

.card-type-badge.type-context_summary {
  background: #e0e7ff;
  color: #3730a3;
}

.info-card .card-body {
  padding: 15px;
}

.card-field {
  margin-bottom: 12px;
}

.card-field:last-child {
  margin-bottom: 0;
}

.field-label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.field-value {
  font-size: 14px;
  color: #333;
}

.field-value.timestamp {
  font-family: monospace;
  font-size: 13px;
}

.content-field .field-content {
  padding: 10px;
  background: #f9f9f9;
  border-radius: 4px;
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
}

.context-details-section {
  margin-top: 30px;
}

.context-details-section h3 {
  font-size: 16px;
  margin-bottom: 15px;
  color: #333;
}

.context-data {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 8px;
  overflow-x: auto;
}

.context-data pre {
  margin: 0;
  font-size: 12px;
  line-height: 1.5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .debug-container {
    padding: 10px;
  }
  
  .debug-tabs {
    flex-wrap: wrap;
  }
  
  .status-grid,
  .performance-grid,
  .config-grid {
    grid-template-columns: 1fr;
  }
  
  .api-filter,
  .log-filter {
    flex-direction: column;
    align-items: stretch;
  }
  
  .api-table {
    font-size: 12px;
  }
  
  .api-table th,
  .api-table td {
    padding: 8px;
  }
}

/* 情绪调试样式 */
.emotion-debug-panel {
  max-width: 1000px;
}

.emotion-test-section {
  margin-bottom: 30px;
}

.test-input-wrapper {
  margin-bottom: 15px;
}

.emotion-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  resize: vertical;
  font-family: inherit;
  box-sizing: border-box;
}

.emotion-input:focus {
  outline: none;
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.test-input-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.analyze-btn {
  padding: 10px 24px;
  background: #4f46e5;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.analyze-btn:hover:not(:disabled) {
  background: #4338ca;
}

.analyze-btn:disabled {
  background: #a5a5a5;
  cursor: not-allowed;
}

.clear-btn {
  padding: 10px 24px;
  background: #f5f5f5;
  color: #666;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.clear-btn:hover {
  background: #e0e0e0;
}

.preset-test-cases {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.preset-label {
  font-size: 14px;
  color: #666;
}

.preset-btn {
  padding: 6px 16px;
  background: #f0f9ff;
  color: #0369a1;
  border: 1px solid #0ea5e9;
  border-radius: 16px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.preset-btn:hover {
  background: #0ea5e9;
  color: white;
}

.emotion-result-section {
  margin-bottom: 30px;
}

.error-result {
  padding: 20px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
}

.error-result h4 {
  color: #dc2626;
  margin: 0 0 10px 0;
}

.error-result pre {
  margin: 10px 0 0 0;
  font-size: 12px;
  white-space: pre-wrap;
}

.result-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  overflow: hidden;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #f5f5f5 0%, #ffffff 100%);
  border-bottom: 1px solid #e0e0e0;
}

.emotion-badge {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  border-radius: 8px;
  color: white;
}

.emotion-icon {
  font-size: 24px;
}

.emotion-name {
  font-size: 18px;
  font-weight: 600;
}

.intensity-display {
  display: flex;
  align-items: center;
  gap: 12px;
}

.intensity-label {
  font-size: 14px;
  color: #666;
}

.intensity-bar-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
}

.intensity-bar {
  width: 150px;
  height: 12px;
  background: #e0e0e0;
  border-radius: 6px;
  overflow: hidden;
}

.intensity-fill {
  height: 100%;
  border-radius: 6px;
  transition: width 0.3s ease;
}

.intensity-fill.mild { background: #10b981; }
.intensity-fill.moderate { background: #f59e0b; }
.intensity-fill.strong { background: #f97316; }
.intensity-fill.extreme { background: #ef4444; }

.intensity-value {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  min-width: 45px;
}

.multi-dim-section {
  padding: 20px;
  background: #fafafa;
  border-bottom: 1px solid #e0e0e0;
}

.multi-dim-section h4 {
  margin: 0 0 15px 0;
  font-size: 14px;
  color: #333;
}

.dim-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.dim-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.dim-label {
  font-size: 13px;
  color: #666;
}

.dim-bar-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
}

.dim-bar {
  flex: 1;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.dim-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.dim-fill.tone { background: #8b5cf6; }
.dim-fill.negative { background: #ef4444; }
.dim-fill.urgency { background: #f59e0b; }
.dim-fill.risk { background: #dc2626; }

.dim-value {
  font-size: 12px;
  font-weight: 500;
  color: #333;
  min-width: 40px;
}

.transfer-section {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.transfer-section.transfer-yes {
  background: #fef2f2;
}

.transfer-section.transfer-no {
  background: #f0fdf4;
}

.transfer-badge {
  display: flex;
  align-items: center;
  gap: 10px;
}

.transfer-icon {
  font-size: 24px;
}

.transfer-text {
  font-size: 16px;
  font-weight: 600;
}

.transfer-yes .transfer-text {
  color: #dc2626;
}

.transfer-no .transfer-text {
  color: #059669;
}

.transfer-reason {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.result-details {
  padding: 15px 20px;
  background: #f9f9f9;
  display: flex;
  gap: 30px;
  flex-wrap: wrap;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.detail-label {
  font-size: 13px;
  color: #666;
}

.detail-value {
  font-size: 13px;
  font-weight: 500;
  color: #333;
}

.detail-value.agitated {
  color: #dc2626;
  font-weight: 600;
}

.emotion-history-section {
  margin-top: 30px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.history-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.history-actions {
  display: flex;
  gap: 10px;
}

.clear-history-btn {
  padding: 8px 16px;
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.clear-history-btn:hover {
  background: #dc2626;
  color: white;
}

.stats-overview {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 15px 25px;
  background: #f5f5f5;
  border-radius: 8px;
  min-width: 80px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #333;
}

.stat-label {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.empty-history {
  padding: 40px;
  text-align: center;
  color: #999;
  background: #f9f9f9;
  border-radius: 8px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.history-item:hover {
  border-color: #4f46e5;
  box-shadow: 0 2px 4px rgba(79, 70, 229, 0.1);
}

.history-text {
  flex: 1;
  font-size: 14px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-right: 15px;
}

.history-result {
  display: flex;
  align-items: center;
  gap: 10px;
}

.history-emotion {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  color: white;
  font-weight: 500;
}

.history-intensity {
  font-size: 13px;
  color: #666;
}

.history-agitated {
  font-size: 16px;
}
</style>