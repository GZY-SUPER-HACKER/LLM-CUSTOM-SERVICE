<template>
  <div :class="['message', `message-${message.role}`]" data-testid="message">
    <div class="message-wrapper">
      <div class="message-avatar">
        {{ message.role === 'user' ? '👤' : (props.isHumanAgentMode ? '👨‍💼' : '🤖') }}
      </div>
      <div class="message-content">
        <div class="message-header">
          <span class="message-sender">
            {{ message.role === 'user' ? currentUsername : (props.isHumanAgentMode ? (props.currentAgent?.name || '客服') : 'AI') }}
          </span>
          <span class="message-time">{{ getCurrentTime() }}</span>
        </div>
        <div class="message-text">{{ message.content }}</div>
        <!-- 仅在 AI 消息上显示操作按钮 -->
        <div v-if="message.role === 'ai'" class="message-actions">
          <button 
            class="action-button feedback-button" 
            :class="{ 'feedback-submitted': feedbackSubmitted }"
            @click="submitFeedback('satisfied')"
            :disabled="feedbackSubmitted"
            title="满意"
          >
            👍
          </button>
          <button 
            class="action-button feedback-button" 
            :class="{ 'feedback-submitted': feedbackSubmitted }"
            @click="submitFeedback('unsatisfied')"
            :disabled="feedbackSubmitted"
            title="不满意"
          >
            👎
          </button>
          <button 
            class="action-button regenerate-button" 
            @click="$emit('regenerate')"
            title="重新生成"
          >
            🔄
          </button>
          <button 
            class="action-button copy-button" 
            @click="$emit('copy', message.content)"
            title="复制"
          >
            📋
          </button>
        </div>
      </div>
    </div>
    <!-- 反馈成功提示 -->
    <div v-if="showFeedbackToast" class="feedback-toast">
      感谢您的反馈
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';

const props = defineProps({
  message: {
    type: Object,
    required: true
  },
  index: {
    type: Number,
    required: true
  },
  isHumanAgentMode: {
    type: Boolean,
    default: false
  },
  currentAgent: {
    type: Object,
    default: null
  }
});

// 定义事件
const emit = defineEmits(['regenerate', 'copy', 'feedback']);

// 反馈状态
const feedbackSubmitted = ref(false);
const showFeedbackToast = ref(false);

const currentUsername = computed(() => {
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  return user.username || '你';
});

// 获取当前时间
function getCurrentTime() {
  const now = new Date();
  const hours = now.getHours().toString().padStart(2, '0');
  const minutes = now.getMinutes().toString().padStart(2, '0');
  return `${hours}:${minutes}`;
}

// 提交反馈
async function submitFeedback(feedbackType) {
  if (feedbackSubmitted.value) {
    return;
  }
  
  try {
    // 收集反馈数据
    const feedbackData = {
      messageId: props.message.id || `msg_${Date.now()}`,
      userId: getCurrentUserId(),
      sessionId: getCurrentSessionId(),
      feedbackType: feedbackType,
      timestamp: new Date().toISOString(),
      status: 'submitted'
    };
    
    // 发送反馈到服务器
    await sendFeedbackToServer(feedbackData);
    
    // 更新状态
    feedbackSubmitted.value = true;
    
    // 显示成功提示
    showFeedbackToast.value = true;
    setTimeout(() => {
      showFeedbackToast.value = false;
    }, 3000);
    
    // 通知父组件
    emit('feedback', feedbackData);
    
  } catch (error) {
    console.error('反馈提交失败:', error);
    // 显示错误提示
    showFeedbackToast.value = true;
    setTimeout(() => {
      showFeedbackToast.value = false;
    }, 5000);
  }
}

// 获取当前用户ID
function getCurrentUserId() {
  // 从localStorage或cookie中获取用户ID
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
  return userInfo.id || localStorage.getItem('userId') || 'anonymous';
}

// 获取当前会话ID
function getCurrentSessionId() {
  // 从localStorage或cookie中获取会话ID
  return localStorage.getItem('sessionId') || `session_${Date.now()}`;
}

// 发送反馈到服务器
async function sendFeedbackToServer(feedbackData) {
  try {
    const payload = {
      message_id: String(feedbackData.messageId),
      user_id: String(feedbackData.userId),
      session_id: String(feedbackData.sessionId),
      feedback_type: feedbackData.feedbackType,
      status: feedbackData.status || 'submitted'
    };

    // 发送反馈到后端API
    const response = await fetch('http://127.0.0.1:8000/feedback/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload)
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || '反馈提交失败');
    }
    
    return await response.json();
  } catch (error) {
    console.error('反馈API调用失败:', error);
    throw error;
  }
}
</script>

<style scoped>
.message {
  margin-bottom: var(--spacing-md);
  animation: messageFadeIn 0.3s ease-in-out;
}

@keyframes messageFadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-wrapper {
  display: flex;
  gap: var(--spacing-sm);
  max-width: 95%;
  align-items: flex-start;
}

/* 自适应宽度 - 对话内容容器 */
.message-content {
  display: inline-block;
  max-width: 100%;
  min-width: 0;
  width: fit-content;
}

.message-user {
  justify-content: flex-end;
}

.message-ai {
  justify-content: flex-start;
}

/* AI消息的气泡宽度优化 */
.message-ai .message-content {
  max-width: calc(100% - 40px);
}

/* 用户消息的气泡宽度优化 */
.message-user .message-content {
  max-width: calc(100% - 40px);
}

/* 消息头部 - 头像和名称水平排列 */
.message-header {
  display: flex;
  align-items: center;
  margin-bottom: var(--spacing-xs);
  font-size: 10px;
  padding: 0 var(--spacing-xs);
  gap: var(--spacing-xs);
}

/* 确保用户消息的头像显示在左侧 */
.message-user .message-wrapper {
  flex-direction: row;
}

/* 确保消息头部元素的正确排列 */
.message-header {
  justify-content: flex-start;
}

.message-header .message-time {
  margin-left: auto;
}

/* 头像优化 */
.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: var(--border-light);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-lg);
  flex-shrink: 0;
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-fast);
}

.message-user .message-avatar {
  background-color: var(--primary-light);
  box-shadow: 0 2px 4px rgba(79, 70, 229, 0.2);
}

.message-ai .message-avatar {
  background-color: var(--border-light);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

/* 消息头部优化 */
.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xs);
  font-size: 10px;
  padding: 0 var(--spacing-xs);
}

.message-sender {
  font-weight: 600;
  color: var(--text-primary);
  font-family: var(--font-sans);
  letter-spacing: 0.02em;
}

.message-user .message-sender {
  color: var(--primary);
}

.message-time {
  color: var(--text-muted);
  font-family: var(--font-mono);
  font-weight: 400;
}

/* 对话框优化 - 自适应宽度 */
.message-text {
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-xl);
  line-height: 1.4;
  font-size: var(--text-sm);
  word-wrap: break-word;
  position: relative;
  max-width: 100%;
  min-width: 0;
  display: inline-block;
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-fast);
  width: fit-content;
  min-width: 0;
}

/* 用户消息样式 */
.message-user .message-text {
  background-color: var(--primary);
  color: var(--text-light);
  border-bottom-right-radius: var(--radius-md);
  box-shadow: 0 2px 8px rgba(79, 70, 229, 0.15);
}

.message-user .message-text:hover {
  background-color: var(--primary-hover);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
  transform: translateY(-1px);
}

/* AI消息样式 */
.message-ai .message-text {
  background-color: var(--surface);
  color: var(--text-primary);
  border: 1px solid var(--border);
  border-bottom-left-radius: var(--radius-md);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.message-ai .message-text:hover {
  background-color: var(--surface-hover);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .message-wrapper {
    max-width: 95%;
  }
  
  .message-avatar {
    width: 32px;
    height: 32px;
    font-size: var(--text-base);
  }
  
  .message-text {
    padding: var(--spacing-sm) var(--spacing-md);
    font-size: var(--text-sm);
    min-width: 0;
  }
  
  .message-header {
    font-size: 10px;
  }
  
  .message-ai .message-content {
    max-width: calc(100% - 40px);
  }
  
  .message-user .message-content {
    max-width: calc(100% - 40px);
  }
}

@media (max-width: 480px) {
  .message-wrapper {
    max-width: 98%;
  }
  
  .message-text {
    padding: var(--spacing-sm);
    font-size: 13px;
  }
  
  .message-ai .message-content {
    max-width: calc(100% - 30px);
  }
  
  .message-user .message-content {
    max-width: calc(100% - 30px);
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .message-ai .message-text {
    background-color: var(--text-primary);
    color: var(--surface);
    border-color: var(--border-dark);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  }
  
  .message-ai .message-text:hover {
    background-color: #1f2937;
  }
  
  .message-avatar {
    background-color: var(--border-dark);
  }
  
  .message-user .message-avatar {
    background-color: var(--primary-dark);
  }
}

/* 长消息处理 */
.message-text.long-message {
  max-width: 100%;
  line-height: 1.6;
}

/* 消息操作按钮 */
.message-actions {
  display: flex;
  gap: var(--spacing-xs);
  margin-top: var(--spacing-xs);
  justify-content: flex-end;
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.message-ai:hover .message-actions {
  opacity: 1;
}

.action-button {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: var(--radius-full);
  background-color: var(--surface-hover);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
  font-size: var(--text-sm);
}

.action-button:hover {
  background-color: var(--primary-light);
  color: var(--primary);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.action-button:active {
  transform: translateY(0);
  box-shadow: none;
}

/* 动画效果增强 */
.message-avatar {
  animation: avatarPulse 2s ease-in-out infinite;
}

/* 反馈按钮样式 */
.feedback-button {
  transition: all var(--transition-fast);
}

.feedback-button:hover:not(:disabled) {
  background-color: var(--primary-light);
  color: var(--primary);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.feedback-button:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: none;
}

.feedback-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.feedback-button.feedback-submitted {
  background-color: var(--success);
  color: var(--text-light);
  border: none;
}

/* 反馈成功提示框 */
.feedback-toast {
  position: fixed;
  bottom: 100px;
  left: 50%;
  transform: translateX(-50%);
  background-color: var(--success);
  color: var(--text-light);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  z-index: 1000;
  animation: toastSlideUp 0.3s ease-out;
  font-size: var(--text-sm);
  font-weight: 500;
}

@keyframes toastSlideUp {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

@keyframes avatarPulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}
</style>
