<template>
  <!-- 气泡模式：收起状态 -->
  <div 
    v-if="!isExpanded" 
    class="chat-bubble-container" 
    @click="handleBubbleClick"
    @mousedown="startBubbleDrag"
    @touchstart="startBubbleDrag"
    :style="{ left: bubblePosition.left + 'px', top: bubblePosition.top + 'px' }"
  >
    <div class="chat-bubble">
      <div class="bubble-icon">🤖</div>
      <div class="bubble-text">
        <span>智能客服助手</span>
        <span class="bubble-status">在线</span>
      </div>
    </div>
  </div>
  
  <!-- 展开状态：完整聊天界面 -->
  <div 
    v-else 
    class="chat-container expanded"
    @mousedown="startChatDrag"
    @touchstart="startChatDrag"
    :style="{
      left: chatPosition.left + 'px',
      top: chatPosition.top + 'px',
      width: chatSize.width + 'px',
      height: chatSize.height + 'px'
    }"
  >
    <!-- 头部 -->
    <div class="chat-header">
      <h1 class="chat-title">
        {{ isHumanAgentMode ? `人工客服 - ${currentAgent?.name || '客服'}` : '智能客服助手' }}
      </h1>
      <div class="chat-header-actions">
        <div class="chat-status">
          <span class="status-indicator online"></span>
          <span class="status-text">
            {{ isHumanAgentMode ? '人工在线' : '在线' }}
          </span>
        </div>
        <button class="new-session-button" @click="startNewSession" title="新建会话">
          📄
        </button>
        <button class="feedback-entry-button" @click="openFeedbackModal" title="提交反馈">
          反馈
        </button>
        <button class="close-button" @click="toggleExpand" title="收起">×</button>
      </div>
    </div>
    
    <!-- 调整大小手柄 -->
    <div class="resize-handles">
      <div class="resize-handle resize-top-left" @mousedown="startResize" @touchstart="startResize" data-direction="top-left"></div>
      <div class="resize-handle resize-top" @mousedown="startResize" @touchstart="startResize" data-direction="top"></div>
      <div class="resize-handle resize-top-right" @mousedown="startResize" @touchstart="startResize" data-direction="top-right"></div>
      <div class="resize-handle resize-left" @mousedown="startResize" @touchstart="startResize" data-direction="left"></div>
      <div class="resize-handle resize-right" @mousedown="startResize" @touchstart="startResize" data-direction="right"></div>
      <div class="resize-handle resize-bottom-left" @mousedown="startResize" @touchstart="startResize" data-direction="bottom-left"></div>
      <div class="resize-handle resize-bottom" @mousedown="startResize" @touchstart="startResize" data-direction="bottom"></div>
      <div class="resize-handle resize-bottom-right" @mousedown="startResize" @touchstart="startResize" data-direction="bottom-right"></div>
    </div>
    
    <!-- 消息区域 -->
    <div class="messages" ref="messagesContainer">
      <!-- 欢迎消息 -->
      <div v-if="messages.length === 0" class="welcome-message">
        <div class="welcome-icon">🤖</div>
        <h2>你好！我是智能客服助手</h2>
        <p>有什么可以帮助你的吗？</p>
      </div>
      
      <!-- 消息列表 -->
      <Message 
        v-for="(msg, index) in messages" 
        :key="index" 
        :message="msg" 
        :index="index"
        :isHumanAgentMode="isHumanAgentMode"
        :currentAgent="currentAgent"
        @regenerate="regenerateAnswer(index)"
        @copy="copyAnswer(msg.content)"
        @feedback="handleFeedback"
      />
      
      <!-- 情绪提示 -->
      <div v-if="showEmotionAlert" class="emotion-alert" :class="emotionAlertType">
        <span class="emotion-icon">{{ emotionAlertIcon }}</span>
        <span class="emotion-text">{{ emotionAlertText }}</span>
        <button class="emotion-close" @click="showEmotionAlert = false">×</button>
      </div>
      
      <!-- 转接状态 -->
      <div v-if="transferStatus && (transferStatus.status === 'pending' || transferStatus.status === 'inProgress' || transferStatus.status === 'failed')" class="transfer-status" :class="transferStatus.status">
        <div v-if="transferStatus.status === 'pending'" class="transfer-pending">
          <div class="loading-spinner"></div>
          <span>正在为您转接人工客服...</span>
        </div>
        <div v-else-if="transferStatus.status === 'inProgress'" class="transfer-in-progress">
          <div class="loading-spinner"></div>
          <div class="transfer-info">
            <p>正在转接中，请稍候...</p>
            <p class="wait-time">预计等待时间: {{ transferStatus.estimatedWaitTime }}分钟</p>
          </div>
        </div>
        <div v-else-if="transferStatus.status === 'failed'" class="transfer-failed">
          <span class="error-icon">❌</span>
          <div class="transfer-info">
            <p>转接失败</p>
            <p class="error-message">{{ transferStatus.error }}</p>
            <button class="retry-button" @click="retryTransfer">重试</button>
          </div>
        </div>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="isLoading" class="loading-message">
        <div class="loading-spinner"></div>
        <span>正在思考...</span>
        <button class="pause-button" @click="pauseGeneration" title="暂停生成">
          ⏸️
        </button>
      </div>
    </div>
    
    <!-- 输入区域 -->
    <div class="input-area">
      <input 
        v-model="question" 
        @keyup.enter="send" 
        placeholder="请输入问题..."
        :disabled="isLoading || isTransferring"
        class="message-input"
      />
      <div class="input-buttons">
        <button 
          @click="requestTransfer" 
          class="transfer-button"
          :disabled="isLoading || isTransferring || isHumanAgentMode"
          title="转人工客服"
        >
          转人工
        </button>
        <button 
          @click="send" 
          class="send-button primary"
          :disabled="isLoading || isTransferring || !question.trim()"
        >
          <span v-if="!isLoading">发送</span>
          <div v-else class="button-spinner"></div>
        </button>
      </div>
    </div>
    
    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      <span class="error-icon">⚠️</span>
      <span>{{ error }}</span>
      <button class="error-close" @click="error = null">×</button>
    </div>
    
    <!-- 复制成功提示 -->
    <div v-if="showCopySuccess" class="copy-success">
      <span>复制成功！</span>
    </div>
    
    <!-- 转人工弹出消息框 -->
    <div v-if="showTransferPopup" class="transfer-popup">
      <div class="loading-spinner"></div>
      <span>正在为您转接人工客服，请稍候...</span>
    </div>

    <div v-if="showFeedbackModal" class="feedback-modal-mask" @click.self="closeFeedbackModal">
      <div class="feedback-modal">
        <h3>提交文字反馈</h3>
        <textarea
          v-model="feedbackText"
          class="feedback-textarea"
          placeholder="请输入你对客服系统的建议或问题反馈..."
          maxlength="500"
        ></textarea>
        <div class="feedback-meta">{{ feedbackText.length }}/500</div>
        <div class="feedback-actions">
          <button class="feedback-cancel" @click="closeFeedbackModal" :disabled="feedbackSubmitting">取消</button>
          <button class="feedback-submit" @click="submitTextFeedback" :disabled="feedbackSubmitting || !feedbackText.trim()">
            {{ feedbackSubmitting ? '提交中...' : '提交反馈' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import Message from "./Message.vue";
import { sendQuestion } from "../api/chat.js";
import { emotionAnalyzer } from "../utils/emotionAnalyzer.js";
import { transferService } from "../services/transferService.js";
import { isLoggedIn, getUser } from "../api/auth";

const router = useRouter();

// 新增状态变量
const isExpanded = ref(false);
const showCopySuccess = ref(false);
const abortController = ref(null);
const isHumanAgentMode = ref(false); // 新增：人工客服模式状态
const currentAgent = ref(null); // 新增：当前人工客服信息

// 气泡位置状态
const bubblePosition = ref({ left: window.innerWidth - 300, top: window.innerHeight - 100 });
const isBubbleDragging = ref(false);
const bubbleDragStart = ref({ x: 0, y: 0 });
const bubbleDragged = ref(false);

// 聊天框位置和大小状态
const chatPosition = ref({ left: window.innerWidth - 300, top: window.innerHeight - 500 });
const chatSize = ref({ width: 280, height: 500 });
const isChatDragging = ref(false);
const chatDragStart = ref({ x: 0, y: 0 });

// 调整大小状态
const isResizing = ref(false);
const resizeStart = ref({ x: 0, y: 0, width: 0, height: 0, left: 0, top: 0 });
const resizeDirection = ref('');

const question = ref("");
const messages = ref([]);
const history = ref([]);
const isLoading = ref(false);
const error = ref(null);
const messagesContainer = ref(null);
const showEmotionAlert = ref(false);
const emotionAlertType = ref('');
const emotionAlertText = ref('');
const emotionAlertIcon = ref('');
const transferStatus = ref(null);
const isTransferring = ref(false);
const transferRequestId = ref(null);
const showTransferPopup = ref(false); // 转人工弹出消息框
const showFeedbackModal = ref(false);
const feedbackText = ref('');
const feedbackSubmitting = ref(false);

const API_BASE = "http://127.0.0.1:8000";

async function ensureSessionId() {
  if (sessionId.value) return sessionId.value;
  const user = getUser();
  const userId = user?.id;
  if (!userId) throw new Error('未登录，无法创建会话');
  const res = await fetch(`${API_BASE}/chat_sessions/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId })
  });
  if (!res.ok) throw new Error('创建会话失败');
  const data = await res.json();
  sessionId.value = data.id;
  localStorage.setItem('sessionId', String(data.id));
  return sessionId.value;
}

async function saveMessageToServer(role, content) {
  const sid = await ensureSessionId();
  const res = await fetch(`${API_BASE}/chat_messages/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sid, role, content })
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || '消息保存失败');
  }
  return await res.json();
}

// 计算属性：是否正在转接
const isTransferInProgress = computed(() => {
  return transferStatus.value && 
    (transferStatus.value.status === 'pending' || transferStatus.value.status === 'inProgress');
});

// 滚动到底部
function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
}

// 分析情绪并显示提示
function analyzeEmotion(text) {
  const emotionResult = emotionAnalyzer.analyze(text);
  
  if (emotionResult.needsTransfer) {
    if (emotionResult.transferRequested) {
      // 用户明确要求转人工
      requestTransfer();
    } else {
      // 情绪激动自动触发，直接调用转人工流程
      requestTransfer();
    }
  }
  
  return emotionResult;
}

// 切换展开/收起状态
function toggleExpand() {
  isExpanded.value = !isExpanded.value;
  if (isExpanded.value) {
    nextTick(() => {
      scrollToBottom();
    });
  }
}

// 开始拖动气泡
function startBubbleDrag(e) {
  e.preventDefault();
  isBubbleDragging.value = true;
  bubbleDragged.value = false;
  
  const clientX = e.clientX || e.touches[0].clientX;
  const clientY = e.clientY || e.touches[0].clientY;
  
  bubbleDragStart.value = {
    x: clientX - bubblePosition.value.left,
    y: clientY - bubblePosition.value.top
  };
  
  document.addEventListener('mousemove', onMouseMove);
  document.addEventListener('mouseup', onMouseUp);
  document.addEventListener('touchmove', onTouchMove);
  document.addEventListener('touchend', onTouchEnd);
}

// 处理气泡点击
function handleBubbleClick() {
  if (!bubbleDragged.value) {
    if (!isLoggedIn()) {
      router.push('/login');
      return;
    }
    toggleExpand();
    if (isExpanded.value) {
      // 计算聊天窗口位置，使其显示在气泡的位置
      // 调整位置，确保聊天窗口不会超出屏幕边界
      const bubbleRect = {
        left: bubblePosition.value.left,
        top: bubblePosition.value.top,
        width: 200, // 气泡的最大宽度
        height: 60  // 气泡的高度
      };
      
      // 计算聊天窗口的位置，使其位于气泡的上方或旁边
      let chatLeft = bubbleRect.left;
      let chatTop = bubbleRect.top - chatSize.value.height - 10;
      
      // 确保聊天窗口不会超出屏幕边界
      const screenWidth = window.innerWidth;
      const screenHeight = window.innerHeight;
      
      // 水平方向调整
      if (chatLeft + chatSize.value.width > screenWidth) {
        chatLeft = screenWidth - chatSize.value.width - 20;
      }
      if (chatLeft < 20) {
        chatLeft = 20;
      }
      
      // 垂直方向调整
      if (chatTop < 20) {
        chatTop = bubbleRect.top + bubbleRect.height + 10;
        // 如果下方也不够空间，则调整到屏幕底部
        if (chatTop + chatSize.value.height > screenHeight) {
          chatTop = screenHeight - chatSize.value.height - 20;
        }
      }
      
      // 更新聊天窗口位置
      chatPosition.value = {
        left: chatLeft,
        top: chatTop
      };
    }
  }
  bubbleDragged.value = false;
}

function openFeedbackModal() {
  showFeedbackModal.value = true;
}

function closeFeedbackModal() {
  if (feedbackSubmitting.value) return;
  showFeedbackModal.value = false;
  feedbackText.value = '';
}

async function submitTextFeedback() {
  if (!feedbackText.value.trim() || feedbackSubmitting.value) return;
  if (!isLoggedIn()) {
    router.push('/login');
    return;
  }
  feedbackSubmitting.value = true;
  try {
    const userInfo = getUser() || {};
    const res = await fetch(`${API_BASE}/feedback/text`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: String(userInfo.id || ''),
        session_id: sessionId.value ? String(sessionId.value) : null,
        content: feedbackText.value.trim()
      })
    });
    if (!res.ok) throw new Error('提交失败');
    feedbackSubmitting.value = false;
    closeFeedbackModal();
    messages.value.push({ role: "system", content: "反馈提交成功，感谢你的建议！" });
    scrollToBottom();
  } catch (e) {
    console.error('提交文本反馈失败:', e);
    error.value = "反馈提交失败，请稍后重试";
  } finally {
    if (feedbackSubmitting.value) feedbackSubmitting.value = false;
  }
}

// 开始拖动聊天框
function startChatDrag(e) {
  // 只有点击头部或空白区域才允许拖动，调整大小手柄区域不允许拖动
  if (!e.target.closest('.chat-header') && !e.target.classList.contains('chat-container')) {
    return;
  }
  
  // 检查是否点击了调整大小手柄
  if (e.target.classList.contains('resize-handle')) {
    return;
  }
  
  e.preventDefault();
  isChatDragging.value = true;
  
  const clientX = e.clientX || e.touches[0].clientX;
  const clientY = e.clientY || e.touches[0].clientY;
  
  chatDragStart.value = {
    x: clientX - chatPosition.value.left,
    y: clientY - chatPosition.value.top
  };
  
  document.addEventListener('mousemove', onMouseMove);
  document.addEventListener('mouseup', onMouseUp);
  document.addEventListener('touchmove', onTouchMove);
  document.addEventListener('touchend', onTouchEnd);
}

// 开始调整大小
function startResize(e) {
  e.preventDefault();
  isResizing.value = true;
  resizeDirection.value = e.target.dataset.direction;
  
  const clientX = e.clientX || e.touches[0].clientX;
  const clientY = e.clientY || e.touches[0].clientY;
  
  resizeStart.value = {
    x: clientX,
    y: clientY,
    width: chatSize.value.width,
    height: chatSize.value.height,
    left: chatPosition.value.left,
    top: chatPosition.value.top
  };
  
  document.addEventListener('mousemove', onMouseMove);
  document.addEventListener('mouseup', onMouseUp);
  document.addEventListener('touchmove', onTouchMove);
  document.addEventListener('touchend', onTouchEnd);
  
  // 设置光标样式
  document.body.style.cursor = getCursorStyle(resizeDirection.value);
}

// 鼠标移动事件
function onMouseMove(e) {
  if (isBubbleDragging.value) {
    const clientX = e.clientX;
    const clientY = e.clientY;
    
    // 检测是否有实际移动
    if (Math.abs(clientX - (bubblePosition.value.left + bubbleDragStart.value.x)) > 5 || 
        Math.abs(clientY - (bubblePosition.value.top + bubbleDragStart.value.y)) > 5) {
      bubbleDragged.value = true;
    }
    
    bubblePosition.value = {
      left: clientX - bubbleDragStart.value.x,
      top: clientY - bubbleDragStart.value.y
    };
  } else if (isChatDragging.value) {
    const clientX = e.clientX;
    const clientY = e.clientY;
    
    chatPosition.value = {
      left: clientX - chatDragStart.value.x,
      top: clientY - chatDragStart.value.y
    };
  } else if (isResizing.value) {
    const clientX = e.clientX;
    const clientY = e.clientY;
    
    const deltaX = clientX - resizeStart.value.x;
    const deltaY = clientY - resizeStart.value.y;
    
    // 尺寸限制
    const minWidth = 250;
    const minHeight = 300;
    const maxHeight = window.innerHeight - 100;
    
    switch (resizeDirection.value) {
      case 'top-left': {
        const newWidth = Math.max(minWidth, resizeStart.value.width - deltaX);
        const newHeight = Math.min(Math.max(minHeight, resizeStart.value.height - deltaY), maxHeight);
        chatSize.value = {
          width: newWidth,
          height: newHeight
        };
        const actualDeltaX = resizeStart.value.width - newWidth;
        const actualDeltaY = resizeStart.value.height - newHeight;
        chatPosition.value = {
          left: resizeStart.value.left + actualDeltaX,
          top: resizeStart.value.top + actualDeltaY
        };
        break;
      }
      case 'top': {
        const newHeight = Math.min(Math.max(minHeight, resizeStart.value.height - deltaY), maxHeight);
        chatSize.value = {
          width: resizeStart.value.width,
          height: newHeight
        };
        const actualDeltaY = resizeStart.value.height - newHeight;
        chatPosition.value = {
          left: resizeStart.value.left,
          top: resizeStart.value.top + actualDeltaY
        };
        break;
      }
      case 'top-right': {
        const newWidth = Math.max(minWidth, resizeStart.value.width + deltaX);
        const newHeight = Math.min(Math.max(minHeight, resizeStart.value.height - deltaY), maxHeight);
        chatSize.value = {
          width: newWidth,
          height: newHeight
        };
        const actualDeltaY = resizeStart.value.height - newHeight;
        chatPosition.value = {
          left: resizeStart.value.left,
          top: resizeStart.value.top + actualDeltaY
        };
        break;
      }
      case 'left': {
        const newWidth = Math.max(minWidth, resizeStart.value.width - deltaX);
        chatSize.value = {
          width: newWidth,
          height: resizeStart.value.height
        };
        const actualDeltaX = resizeStart.value.width - newWidth;
        chatPosition.value = {
          left: resizeStart.value.left + actualDeltaX,
          top: resizeStart.value.top
        };
        break;
      }
      case 'right':
        chatSize.value = {
          width: Math.max(minWidth, resizeStart.value.width + deltaX),
          height: resizeStart.value.height
        };
        break;
      case 'bottom-left': {
        const newWidth = Math.max(minWidth, resizeStart.value.width - deltaX);
        const newHeight = Math.min(Math.max(minHeight, resizeStart.value.height + deltaY), maxHeight);
        chatSize.value = {
          width: newWidth,
          height: newHeight
        };
        const actualDeltaX = resizeStart.value.width - newWidth;
        chatPosition.value = {
          left: resizeStart.value.left + actualDeltaX,
          top: resizeStart.value.top
        };
        break;
      }
      case 'bottom':
        chatSize.value = {
          width: resizeStart.value.width,
          height: Math.min(Math.max(minHeight, resizeStart.value.height + deltaY), maxHeight)
        };
        break;
      case 'bottom-right':
        chatSize.value = {
          width: Math.max(minWidth, resizeStart.value.width + deltaX),
          height: Math.min(Math.max(minHeight, resizeStart.value.height + deltaY), maxHeight)
        };
        break;
    }
  }
}

// 触摸移动事件
function onTouchMove(e) {
  onMouseMove(e.touches[0]);
}

// 鼠标释放事件
function onMouseUp() {
  endDrag();
}

// 触摸结束事件
function onTouchEnd() {
  endDrag();
}

// 结束拖动
function endDrag() {
  isBubbleDragging.value = false;
  isChatDragging.value = false;
  isResizing.value = false;
  
  document.removeEventListener('mousemove', onMouseMove);
  document.removeEventListener('mouseup', onMouseUp);
  document.removeEventListener('touchmove', onTouchMove);
  document.removeEventListener('touchend', onTouchEnd);
  
  // 恢复光标样式
  document.body.style.cursor = '';
}

// 获取光标样式
function getCursorStyle(direction) {
  switch (direction) {
    case 'top-left':
    case 'bottom-right':
      return 'nwse-resize';
    case 'top':
    case 'bottom':
      return 'ns-resize';
    case 'top-right':
    case 'bottom-left':
      return 'nesw-resize';
    case 'left':
    case 'right':
      return 'ew-resize';
    default:
      return '';
  }
}

// 暂停生成
function pauseGeneration() {
  if (abortController.value) {
    abortController.value.abort();
    abortController.value = null;
    isLoading.value = false;
    // 回滚到生成开始前的状态
    if (messages.value.length > 0) {
      const lastMessage = messages.value[messages.value.length - 1];
      if (lastMessage.role === 'ai') {
        messages.value.pop();
      }
    }
    error.value = "生成已暂停";
  }
}

// 重新生成回答
async function regenerateAnswer(index) {
  const msg = messages.value[index];
  if (msg.role !== 'ai') return;
  
  // 找到对应的用户问题
  let userQuestion = '';
  for (let i = index - 1; i >= 0; i--) {
    if (messages.value[i].role === 'user') {
      userQuestion = messages.value[i].content;
      break;
    }
  }
  
  if (!userQuestion) return;
  
  // 移除当前AI回答
  messages.value.splice(index, 1);
  
  // 重新发送请求
  await sendWithQuestion(userQuestion);
}

// 复制回答
function copyAnswer(content) {
  navigator.clipboard.writeText(content)
    .then(() => {
      showCopySuccess.value = true;
      setTimeout(() => {
        showCopySuccess.value = false;
      }, 2000);
    })
    .catch(err => {
      console.error('复制失败:', err);
      error.value = "复制失败，请手动复制";
    });
}

// 处理用户反馈
async function handleFeedback(feedbackData) {
  try {
    // 记录反馈数据到控制台（实际应用中应发送到服务器）
    console.log('用户反馈:', feedbackData);
    
    // 这里可以添加将反馈数据发送到服务器的逻辑
    // 示例代码：
    // await fetch('/api/feedback', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify(feedbackData)
    // });
    
    // 可以将反馈数据存储到messages数组中，用于后续分析
    const messageIndex = messages.value.findIndex(msg => msg.id === feedbackData.messageId);
    if (messageIndex !== -1) {
      messages.value[messageIndex].feedback = feedbackData;
    }
    
  } catch (error) {
    console.error('反馈处理失败:', error);
    error.value = "反馈提交失败，请稍后重试";
  }
}

// 发送消息（带问题参数）
async function sendWithQuestion(questionText) {
  try {
    isLoading.value = true;
    error.value = null;

    // 分析情绪
    const emotionResult = analyzeEmotion(questionText);

    // 直接发送请求（绕过 chat.js）
    const url = "http://127.0.0.1:8000/chat/send_message";
    // 从本地存储获取用户信息
    const userInfo = getUser() || {};
    const requestData = {
      user_id: userInfo.id || 1, // 如果没有用户信息，使用默认值 1
      user_input: questionText,
      session_id: sessionId.value
    };
    
    console.log("直接发送请求到:", url);
    console.log("直接发送请求数据:", requestData);
    
    // 创建中止控制器
    abortController.value = new AbortController();
    
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData),
      signal: abortController.value.signal
    });
    
    console.log("响应状态:", res.status);
    console.log("响应状态文本:", res.statusText);
    
    const data = await res.json();
    console.log("响应数据:", data);
    
    if (!res.ok) {
      throw new Error(`请求失败: ${res.status} ${res.statusText}`);
    }
    
    // 获取最新的回答
    const answer = data
      .filter(msg => msg.role === "assistant")
      .pop();
    
    // 添加 AI 回复（保留 message id 用于反馈入库）
    messages.value.push({ role: "ai", content: answer ? answer.content : "没有得到有效回答", id: answer?.id, session_id: answer?.session_id });

    // 更新对话历史
    history.value.push({ 
      question: questionText, 
      answer: answer ? answer.content : "没有得到有效回答",
      emotion: emotionResult.emotion,
      emotionIntensity: emotionResult.intensityLevel
    });
  } catch (err) {
    if (err.name === 'AbortError') {
      console.log('请求已中止');
    } else {
      error.value = `抱歉，服务暂时不可用: ${err.message}`;
      console.error("发送消息失败:", err);
    }
  } finally {
    isLoading.value = false;
    abortController.value = null;
    scrollToBottom();
  }
}

async function send() {
  if (!question.value.trim() || isLoading.value || isTransferring.value) return;
  if (!isLoggedIn()) {
    router.push('/login');
    return;
  }

  const questionText = question.value.trim();
  question.value = "";

  try {
    // 分析情绪
    const emotionResult = analyzeEmotion(questionText);

    // 检查是否需要转人工
    if (emotionResult.needsTransfer) {
      return;
    }

    // 用户消息
    messages.value.push({ 
      role: "user", 
      content: questionText,
      emotion: emotionResult.emotion,
      emotionIntensity: emotionResult.intensityLevel
    });
    scrollToBottom();

    // 检查是否为人工客服模式
    if (isHumanAgentMode.value) {
      // 真实落库：记录用户与人工客服的交互消息
      await saveMessageToServer('user', questionText);
      messages.value.push({ 
        role: "system", 
        content: `消息已发送给客服 ${currentAgent.value?.name || '客服'}，请等待回复。`
      });
      scrollToBottom();
      return;
    }

    // 智能客服模式：发送请求到AI
    const url = "http://127.0.0.1:8000/chat/send_message";
    // 从本地存储获取用户信息
    const userInfo = getUser() || {};
    const requestData = {
      user_id: userInfo.id || 1, // 如果没有用户信息，使用默认值 1
      user_input: questionText,
      session_id: sessionId.value
    };
    
    console.log("直接发送请求到:", url);
    console.log("直接发送请求数据:", requestData);
    
    abortController.value = new AbortController();
    
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData),
      signal: abortController.value.signal
    });
    
    console.log("响应状态:", res.status);
    console.log("响应状态文本:", res.statusText);
    
    const data = await res.json();
    console.log("响应数据:", data);
    
    if (!res.ok) {
      throw new Error(`请求失败: ${res.status} ${res.statusText}`);
    }
    
    // 获取最新的回答
    const answer = data
      .filter(msg => msg.role === "assistant")
      .pop();
    
    // 检查回答是否为转人工消息
    if (answer && answer.content.includes('转接人工客服')) {
      // 自动触发转人工流程
      requestTransfer();
    } else {
      // 添加 AI 回复
      messages.value.push({ role: "ai", content: answer ? answer.content : "没有得到有效回答", id: answer?.id, session_id: answer?.session_id });

      // 更新对话历史
      history.value.push({ 
        question: questionText, 
        answer: answer ? answer.content : "没有得到有效回答",
        emotion: emotionResult.emotion,
        emotionIntensity: emotionResult.intensityLevel
      });
      
      // 保存会话ID到本地存储
      if (data && data.length > 0 && data[0].session_id) {
        sessionId.value = data[0].session_id;
        localStorage.setItem('sessionId', data[0].session_id);
      }
      
      // 保存会话ID到本地存储
      if (data && data.length > 0 && data[0].session_id) {
        sessionId.value = data[0].session_id;
        localStorage.setItem('sessionId', data[0].session_id);
      }
    }
  } catch (err) {
    if (err.name === 'AbortError') {
      console.log('请求已中止');
      if (messages.value.length > 0) {
        const lastMessage = messages.value[messages.value.length - 1];
        if (lastMessage.role === 'user') {
          messages.value.pop();
        }
      }
    } else {
      error.value = `抱歉，服务暂时不可用: ${err.message}`;
      console.error("发送消息失败:", err);
    }
  } finally {
    isLoading.value = false;
    abortController.value = null;
    scrollToBottom();
  }
}

// 请求转人工
async function requestTransfer() {
  if (isLoading.value || isTransferring.value) return;

  try {
    isTransferring.value = true;
    error.value = null;

    // 显示转人工弹出消息框
    showTransferPopup.value = true;

    // 构建用户上下文
    const sid = await ensureSessionId();
    const userContext = {
      userInfo: {
        userId: `user_${Date.now()}`,
        timestamp: new Date().toISOString()
      },
      sessionId: sid,
      sessionHistory: history.value,
      emotionAnalysis: analyzeEmotion(question.value || '用户请求转人工'),
      attemptedSolutions: messages.value.filter(msg => msg.role === 'ai').map(msg => msg.content)
    };

    // 发起转接请求
    const result = await transferService.requestTransfer(userContext);
    transferRequestId.value = result.id;
    transferStatus.value = result;

    // 轮询转接状态
    await pollTransferStatus(result.id);
  } catch (err) {
    error.value = "转接失败，请稍后重试";
    console.error("转接失败:", err);
    transferStatus.value = {
      status: 'failed',
      error: err.message || '转接失败'
    };
    // 失败时也关闭弹出消息框
    showTransferPopup.value = false;
  } finally {
    isTransferring.value = false;
    scrollToBottom();
  }
}

// 轮询转接状态
async function pollTransferStatus(requestId) {
  let attempts = 0;
  const maxAttempts = 30;
  const interval = 1000;

  while (attempts < maxAttempts) {
    attempts++;
    await new Promise(resolve => setTimeout(resolve, interval));

    const status = transferService.getTransferStatus(requestId);
    if (status) {
      transferStatus.value = status;
      
      if (status.status === 'completed' || status.status === 'failed') {
        // 关闭转人工弹出消息框
        showTransferPopup.value = false;
        
        // 显示最终状态消息
        if (status.status === 'completed') {
          // 转人工成功，设置人工客服模式
        isHumanAgentMode.value = true;
        currentAgent.value = status.agent;
        
        // 保存人工客服模式状态到本地存储
        localStorage.setItem('isHumanAgentMode', 'true');
        localStorage.setItem('currentAgent', JSON.stringify(status.agent));
          
          messages.value.push({ 
            role: "system", 
            content: `已成功转接至客服 ${status.agent.name}，请直接与客服交流。`
          });
        // 真实落库：转人工成功的操作记录（作为 system 消息，方便后台查看）
        await saveMessageToServer('system', `转人工成功：已转接至 ${status.agent.name}`);
        } else {
          messages.value.push({ 
            role: "system", 
            content: `转接失败: ${status.error}`
          });
        }
        scrollToBottom();
        // 清除转接状态，不再显示提示框
        setTimeout(() => {
          transferStatus.value = null;
        }, 2000);
        break;
      }
    }
  }
}

// 重试转接
function retryTransfer() {
  transferStatus.value = null;
  requestTransfer();
}

// 会话管理
const sessionId = ref(null);

// 初始化会话
function initSession() {
  // 从localStorage获取会话ID，如果没有则为null
  const savedSessionId = localStorage.getItem('sessionId');
  if (savedSessionId) {
    sessionId.value = parseInt(savedSessionId);
  }
  
  // 从localStorage恢复人工客服模式状态
  const savedHumanMode = localStorage.getItem('isHumanAgentMode');
  if (savedHumanMode === 'true') {
    isHumanAgentMode.value = true;
    // 恢复客服信息
    const savedAgent = localStorage.getItem('currentAgent');
    if (savedAgent) {
      currentAgent.value = JSON.parse(savedAgent);
    }
  }
}

// 开始新会话
function startNewSession() {
  // 清空本地消息
  messages.value = [];
  history.value = [];
  question.value = '';
  error.value = null;
  
  // 重置会话ID（设为null，让后端创建新会话）
  sessionId.value = null;
  localStorage.removeItem('sessionId');
  
  // 重置人工客服模式
  isHumanAgentMode.value = false;
  currentAgent.value = null;
  transferStatus.value = null;
  
  // 清除本地存储中的人工客服状态
  localStorage.removeItem('isHumanAgentMode');
  localStorage.removeItem('currentAgent');
  
  // 显示欢迎消息
  scrollToBottom();
}

// 页面加载时滚动到底部
onMounted(() => {
  initSession();
  scrollToBottom();
});
</script>

<style scoped>
/* 气泡模式：收起状态 */
.chat-bubble-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
  cursor: pointer;
  transition: transform var(--transition-fast);
}

.chat-bubble-container:hover {
  transform: scale(1.05);
}

.chat-bubble {
  background-color: var(--primary);
  color: var(--text-light);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  min-width: 120px;
  max-width: 180px;
  animation: bubbleFloat 3s ease-in-out infinite;
  cursor: move;
}

.chat-bubble:active {
  cursor: grabbing;
}

.bubble-icon {
  font-size: 1.5rem;
}

.bubble-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.bubble-text span:first-child {
  font-weight: 500;
  font-size: var(--text-base);
}

.bubble-status {
  font-size: var(--text-xs);
  opacity: 0.8;
}

@keyframes bubbleFloat {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}

/* 主容器 */
.chat-container {
  position: fixed;
  width: 450px;
  height: 600px;
  background-color: var(--surface);
  border-radius: var(--radius-2xl, 1.5rem);
  box-shadow: var(--shadow-xl, 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04));
  overflow: hidden;
  position: relative;
  border: 1px solid var(--border-light);
  z-index: 1000;
  animation: slideUp 0.3s ease-in-out;
  cursor: move;
  display: flex;
  flex-direction: column;
}

.chat-container:active {
  cursor: grabbing;
}

.chat-container.expanded {
  max-height: 80vh;
}

/* 调整大小手柄 */
.resize-handles {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 100;
}

.resize-handle {
  position: absolute;
  background-color: transparent;
  pointer-events: auto;
  z-index: 1000;
}

/* 角落手柄 */
.resize-handle.resize-top-left {
  top: -5px;
  left: -5px;
  width: 10px;
  height: 10px;
  cursor: nwse-resize;
}

.resize-handle.resize-top-right {
  top: -5px;
  right: -5px;
  width: 10px;
  height: 10px;
  cursor: nesw-resize;
}

.resize-handle.resize-bottom-left {
  bottom: -5px;
  left: -5px;
  width: 10px;
  height: 10px;
  cursor: nesw-resize;
}

.resize-handle.resize-bottom-right {
  bottom: -5px;
  right: -5px;
  width: 10px;
  height: 10px;
  cursor: nwse-resize;
}

/* 边缘手柄 */
.resize-handle.resize-top {
  top: -5px;
  left: 10px;
  right: 10px;
  height: 10px;
  cursor: ns-resize;
}

.resize-handle.resize-bottom {
  bottom: -5px;
  left: 10px;
  right: 10px;
  height: 10px;
  cursor: ns-resize;
}

.resize-handle.resize-left {
  left: -5px;
  top: 10px;
  bottom: 10px;
  width: 10px;
  cursor: ew-resize;
}

.resize-handle.resize-right {
  right: -5px;
  top: 10px;
  bottom: 10px;
  width: 10px;
  cursor: ew-resize;
}

/* 头部 */
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg) var(--spacing-xl);
  background-color: var(--primary);
  color: var(--text-light);
  border-bottom: 1px solid var(--primary-light);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 10;
}

.chat-title {
  font-size: var(--text-lg);
  font-weight: 600;
  margin: 0;
  font-family: var(--font-sans);
  letter-spacing: 0.02em;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.chat-header-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.chat-status {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--text-xs);
  font-weight: 500;
  background-color: rgba(255, 255, 255, 0.1);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-full);
  backdrop-filter: blur(10px);
}

.close-button {
  background: none;
  border: none;
  color: var(--text-light);
  cursor: pointer;
  font-size: var(--text-lg);
  padding: 0;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.close-button:hover {
  background-color: rgba(255, 255, 255, 0.1);
  transform: rotate(90deg);
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--success-light);
  animation: pulse 2s infinite;
  box-shadow: 0 0 10px var(--success-light);
}

.status-indicator.online {
  background-color: var(--success-light);
}

@keyframes pulse {
  0% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.1);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

/* 消息区域 */
.messages {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-md);
  background-color: var(--background);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  position: relative;
  min-height: 0;
}

/* 消息区域背景纹理 */
.messages::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(circle at 25px 25px, rgba(79, 70, 229, 0.05) 2px, transparent 0),
    radial-gradient(circle at 75px 75px, rgba(79, 70, 229, 0.05) 2px, transparent 0);
  background-size: 100px 100px;
  pointer-events: none;
  z-index: 0;
}

/* 消息内容层 */
.messages > * {
  position: relative;
  z-index: 1;
}

/* 欢迎消息 */
.welcome-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-md, 0.75rem);
  text-align: center;
  margin: var(--spacing-sm) 0;
  background-color: var(--surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  border: 0.5px solid var(--border-light);
  animation: welcomeFadeIn 0.8s ease-in-out;
}

@keyframes welcomeFadeIn {
  from {
    opacity: 0;
    transform: translateY(10px) scale(0.85);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.welcome-icon {
  font-size: 1.5rem;
  margin-bottom: var(--spacing-xs);
  animation: bounce 2s ease-in-out infinite;
  filter: drop-shadow(0 2px 3px rgba(0, 0, 0, 0.1));
}

.welcome-message h2 {
  color: var(--text-primary);
  margin-bottom: var(--spacing-xs);
  font-size: var(--text-base);
  font-weight: 600;
  letter-spacing: 0.02em;
}

.welcome-message p {
  color: var(--text-secondary);
  font-size: 10px;
  max-width: 90%;
  line-height: 1.3;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-8px);
  }
  60% {
    transform: translateY(-4px);
  }
}

/* 加载消息 */
.loading-message {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  justify-content: center;
  padding: var(--spacing-md) var(--spacing-lg);
  background-color: var(--surface);
  border-radius: var(--radius-xl);
  align-self: flex-start;
  margin: 0 auto;
  animation: fadeIn 0.3s ease-in-out;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
}

.pause-button {
  padding: var(--spacing-xs);
  border: none;
  border-radius: var(--radius-full);
  background-color: var(--surface);
  color: var(--text-secondary);
  cursor: pointer;
  font-size: var(--text-sm);
  transition: all var(--transition-fast);
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pause-button:hover {
  background-color: var(--primary-light);
  color: var(--primary);
  transform: scale(1.1);
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-light);
  border-top: 2px solid var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes transferPopupFadeIn {
  from {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
  }
}

/* 输入区域 */
.input-area {
  display: flex;
  gap: var(--spacing-sm);
  padding: var(--spacing-lg);
  background-color: var(--surface);
  border-top: 1px solid var(--border);
  align-items: stretch;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
  position: sticky;
  bottom: 0;
  z-index: 10;
}

.message-input {
  flex: 1;
  min-height: 40px;
  resize: none;
  border: 1.5px solid var(--border);
  border-radius: var(--radius-2xl);
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: var(--text-sm);
  transition: all var(--transition-fast);
  background-color: var(--surface);
  font-family: var(--font-sans);
  line-height: 1.4;
}

.message-input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
  background-color: var(--surface-hover);
}

.message-input::placeholder {
  color: var(--text-muted);
  font-style: italic;
}

.input-buttons {
  display: flex;
  gap: var(--spacing-sm);
  align-items: stretch;
}

.transfer-button {
  min-width: 50px;
  height: 100%;
  border-radius: var(--radius-2xl);
  font-weight: 500;
  transition: all var(--transition-fast);
  font-size: 10px;
  letter-spacing: 0.02em;
  background-color: var(--warning);
  color: var(--text-light);
  border: none;
  box-shadow: 0 3px 8px rgba(245, 158, 11, 0.3);
  flex-shrink: 0;
  padding: 0 var(--spacing-xs);
}

.transfer-button:hover:not(:disabled) {
  background-color: var(--warning-dark);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
  transform: translateY(-1px);
}

.transfer-button:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 3px 8px rgba(245, 158, 11, 0.3);
}

.transfer-button:disabled {
  background-color: var(--text-muted);
  box-shadow: none;
  cursor: not-allowed;
  transform: none;
  opacity: 0.6;
  border: 1px solid var(--border);
  color: var(--text-secondary);
  pointer-events: none;
}

.transfer-button:disabled:hover {
  background-color: var(--text-muted);
  box-shadow: none;
  transform: none;
  opacity: 0.6;
}

.send-button {
  min-width: 50px;
  max-width: 60px;
  height: 100%;
  border-radius: var(--radius-2xl);
  font-weight: 500;
  transition: all var(--transition-fast);
  font-size: 10px;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  background-color: var(--primary);
  color: var(--text-light);
  border: none;
  box-shadow: 0 3px 8px rgba(59, 130, 246, 0.3);
  flex-shrink: 0;
  padding: 0 var(--spacing-xs);
}

.send-button:hover:not(:disabled) {
  background-color: var(--primary-hover);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
  transform: translateY(-1px);
}

.send-button:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 3px 8px rgba(79, 70, 229, 0.3);
}

.send-button:disabled {
  background-color: var(--text-muted);
  box-shadow: none;
  cursor: not-allowed;
  transform: none;
}

.button-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* 错误消息 */
.error-message {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-lg);
  background-color: rgba(220, 38, 38, 0.1);
  border-left: 4px solid var(--error);
  color: var(--error);
  font-size: var(--text-sm);
  animation: slideIn 0.3s ease-in-out;
  border-radius: 0 var(--radius-lg) var(--radius-lg) 0;
  box-shadow: var(--shadow-sm);
  margin: var(--spacing-sm) 0;
}

/* 复制成功提示 */
.copy-success {
  position: absolute;
  bottom: 100px;
  right: var(--spacing-lg);
  background-color: var(--success);
  color: var(--text-light);
  padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  animation: slideIn 0.3s ease-in-out;
  z-index: 1000;
}

/* 转人工弹出消息框 */
.transfer-popup {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: var(--surface);
  color: var(--text-primary);
  padding: var(--spacing-lg) var(--spacing-xl);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  animation: transferPopupFadeIn 0.3s ease-in-out;
  z-index: 2000;
  border: 1px solid var(--border-light);
  backdrop-filter: blur(10px);
  min-width: 200px;
  justify-content: center;
}

.error-icon {
  font-size: var(--text-lg);
  flex-shrink: 0;
}

.new-session-button {
  background: none;
  border: none;
  color: var(--text-light);
  cursor: pointer;
  font-size: var(--text-lg);
  padding: 0;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
  margin-right: var(--spacing-sm);
}

.new-session-button:hover {
  background-color: rgba(255, 255, 255, 0.1);
  transform: rotate(15deg);
}

.feedback-entry-button {
  border: 1px solid rgba(255, 255, 255, 0.45);
  background: rgba(255, 255, 255, 0.18);
  color: #fff;
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 12px;
  cursor: pointer;
}

.feedback-entry-button:hover {
  background: rgba(255, 255, 255, 0.28);
}

.error-close:hover {
  background: rgba(220, 38, 38, 0.1);
  transform: none;
  box-shadow: none;
  opacity: 0.8;
}

@keyframes slideIn {
  from {
    transform: translateX(-100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-bubble-container {
    bottom: 15px;
    right: 15px;
  }
  
  .chat-bubble {
    min-width: 180px;
    max-width: 240px;
    padding: var(--spacing-sm);
  }
  
  .chat-container {
    width: 100%;
    height: 100vh;
    max-height: none;
    border-radius: 0;
    bottom: 0;
    right: 0;
    box-shadow: none;
    border: none;
  }
  
  .chat-header {
    padding: var(--spacing-md) var(--spacing-lg);
  }
  
  .messages {
    padding: var(--spacing-sm);
  }
  
  .input-area {
    padding: var(--spacing-lg);
  }
  
  .welcome-message {
    padding: var(--spacing-2xl);
  }
  
  .welcome-icon {
    font-size: 4rem;
  }
  
  .message-input {
    min-height: 48px;
  }
  
  .send-button {
    min-width: 80px;
    height: 48px;
  }
}

@media (max-width: 480px) {
  .chat-title {
    font-size: var(--text-lg);
  }
  
  .chat-header {
    padding: var(--spacing-sm) var(--spacing-md);
  }
  
  .messages {
    padding: var(--spacing-xs);
  }
  
  .input-area {
    padding: var(--spacing-md);
    gap: var(--spacing-sm);
  }
  
  .message-input {
    min-height: 44px;
    padding: var(--spacing-sm) var(--spacing-md);
  }
  
  .send-button {
    min-width: 60px;
    height: 44px;
    padding: var(--spacing-sm);
    font-size: 12px;
  }
  
  .welcome-message {
    padding: var(--spacing-xl);
  }
  
  .welcome-icon {
    font-size: 3rem;
  }
  
  .welcome-message h2 {
    font-size: var(--text-xl);
  }
}

/* 滚动条优化 */
.messages::-webkit-scrollbar {
  width: 8px;
}

.messages::-webkit-scrollbar-track {
  background: var(--border-light);
  border-radius: var(--radius-full);
  margin: var(--spacing-md);
}

.messages::-webkit-scrollbar-thumb {
  background: var(--text-muted);
  border-radius: var(--radius-full);
  transition: all var(--transition-fast);
}

.messages::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
  transform: scaleX(1.1);
}

/* 情绪提示 */
.emotion-alert {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--radius-xl);
  margin: var(--spacing-md) 0;
  animation: slideIn 0.3s ease-in-out;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
}

.emotion-alert.emotion-high {
  background-color: rgba(245, 158, 11, 0.1);
  border-left: 4px solid var(--warning);
  color: var(--warning-dark);
}

.emotion-icon {
  font-size: var(--text-lg);
  flex-shrink: 0;
}

.emotion-text {
  flex: 1;
  font-size: var(--text-sm);
  line-height: 1.4;
}

.emotion-close {
  background: none;
  border: none;
  color: inherit;
  font-size: var(--text-lg);
  cursor: pointer;
  padding: var(--spacing-xs);
  border-radius: var(--radius-full);
  transition: all var(--transition-fast);
}

.emotion-close:hover {
  background: rgba(0, 0, 0, 0.1);
  transform: none;
  box-shadow: none;
  opacity: 0.8;
}

/* 转接状态 */
.transfer-status {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--radius-xl);
  margin: var(--spacing-md) 0;
  animation: slideIn 0.3s ease-in-out;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
  background-color: var(--surface);
}

.transfer-status.pending,
.transfer-status.inProgress {
  background-color: rgba(59, 130, 246, 0.1);
  border-left: 4px solid var(--primary);
  color: var(--primary-dark);
}

.transfer-status.completed {
  background-color: rgba(16, 185, 129, 0.1);
  border-left: 4px solid var(--success);
  color: var(--success-dark);
}

.transfer-status.failed {
  background-color: rgba(239, 68, 68, 0.1);
  border-left: 4px solid var(--error);
  color: var(--error-dark);
}

.transfer-pending,
.transfer-in-progress {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  flex: 1;
}

.transfer-info {
  flex: 1;
  line-height: 1.4;
}

.transfer-info p {
  margin: 0;
  font-size: var(--text-sm);
}

.wait-time,
.agent-info {
  font-weight: 500;
  margin-top: var(--spacing-xs) !important;
}

.error-message {
  font-size: var(--text-xs) !important;
  opacity: 0.8;
  margin-top: var(--spacing-xs) !important;
}

.retry-button {
  margin-top: var(--spacing-sm) !important;
  padding: var(--spacing-xs) var(--spacing-sm);
  font-size: var(--text-xs);
  border: 1px solid var(--error);
  background-color: var(--error);
  color: var(--text-light);
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.retry-button:hover {
  background-color: var(--error-dark);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
}

.feedback-modal-mask {
  position: absolute;
  inset: 0;
  z-index: 3000;
  background: rgba(17, 24, 39, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
}

.feedback-modal {
  width: min(92%, 420px);
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.2);
}

.feedback-modal h3 {
  margin: 0 0 10px;
  font-size: 16px;
  color: #1f2937;
}

.feedback-textarea {
  width: 100%;
  min-height: 120px;
  resize: vertical;
  border: 1px solid #dbe2f0;
  border-radius: 10px;
  padding: 10px;
  font-size: 14px;
  outline: none;
}

.feedback-textarea:focus {
  border-color: #4f73ff;
  box-shadow: 0 0 0 3px rgba(79, 115, 255, 0.15);
}

.feedback-meta {
  margin-top: 6px;
  text-align: right;
  font-size: 12px;
  color: #64748b;
}

.feedback-actions {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.feedback-cancel,
.feedback-submit {
  border: none;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 13px;
  cursor: pointer;
}

.feedback-cancel {
  background: #e5e7eb;
  color: #374151;
}

.feedback-submit {
  background: #4f73ff;
  color: #fff;
}

.success-icon,
.error-icon {
  font-size: var(--text-lg);
  flex-shrink: 0;
}

/* 响应式设计调整 */
@media (max-width: 768px) {
  .input-buttons {
    flex-direction: column;
  }
  
  .transfer-button,
  .send-button {
    min-width: 60px;
    height: 48px;
  }
  
  .emotion-alert,
  .transfer-status {
    padding: var(--spacing-sm) var(--spacing-md);
  }
  
  .emotion-text,
  .transfer-info p {
    font-size: var(--text-xs);
  }
}

@media (max-width: 480px) {
  .input-buttons {
    flex-direction: column;
  }
  
  .transfer-button,
  .send-button {
    min-width: 50px;
    height: 44px;
    font-size: 10px;
  }
}
</style>
