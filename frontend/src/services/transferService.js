// 人工客服转接服务（对接真实后端）
const API_BASE = 'http://127.0.0.1:8000';

// 转接服务类
class TransferService {
  constructor() {
    this.transferStatus = {
      pending: 'pending',
      inProgress: 'inProgress',
      completed: 'completed',
      failed: 'failed'
    };
    
    this.transferRequests = new Map();
  }

  // 发起转接请求
  async requestTransfer(userContext) {
    const requestId = `transfer_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    // 创建转接请求
    const transferRequest = {
      id: requestId,
      status: this.transferStatus.pending,
      userContext,
      createdAt: new Date(),
      updatedAt: new Date(),
      agent: null,
      estimatedWaitTime: 0
    };

    this.transferRequests.set(requestId, transferRequest);

    try {
      const sessionId = userContext?.sessionId;
      if (!sessionId) throw new Error('缺少 sessionId，无法转人工');

      transferRequest.status = this.transferStatus.inProgress;
      transferRequest.updatedAt = new Date();

      // 真实后端：创建转人工记录（落库 manual_interventions）
      const res = await fetch(`${API_BASE}/manual_interventions/transfer_with_emotion/${sessionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || '转人工失败');
      }

      // 这里没有真实排队系统，先认为转接完成
      transferRequest.status = this.transferStatus.completed;
      transferRequest.updatedAt = new Date();
      transferRequest.agent = { id: 'support', name: '人工客服', status: 'available' };
      transferRequest.estimatedWaitTime = 0;
    } catch (error) {
      transferRequest.status = this.transferStatus.failed;
      transferRequest.error = error.message || '转接失败';
      transferRequest.updatedAt = new Date();
      console.error('转接失败:', error);
    }

    // 记录转接日志
    this.logTransfer(transferRequest);

    return transferRequest;
  }

  // 获取转接状态
  getTransferStatus(requestId) {
    return this.transferRequests.get(requestId);
  }

  // 取消转接请求
  cancelTransfer(requestId) {
    const request = this.transferRequests.get(requestId);
    if (request) {
      request.status = this.transferStatus.failed;
      request.error = '用户取消转接';
      request.updatedAt = new Date();
      this.logTransfer(request);
      return true;
    }
    return false;
  }

  // 记录转接日志
  logTransfer(transferRequest) {
    const logEntry = {
      timestamp: new Date().toISOString(),
      requestId: transferRequest.id,
      status: transferRequest.status,
      userInfo: transferRequest.userContext.userInfo,
      sessionHistory: transferRequest.userContext.sessionHistory.length,
      emotionAnalysis: transferRequest.userContext.emotionAnalysis,
      agent: transferRequest.agent,
      estimatedWaitTime: transferRequest.estimatedWaitTime,
      error: transferRequest.error,
      duration: transferRequest.updatedAt - transferRequest.createdAt
    };

    console.log('转接日志:', logEntry);
    
    // 实际项目中可以发送到后端存储
    // 这里仅做控制台输出
  }

  // 预留：后续可以从后端拉取客服状态
}

// 导出单例实例
export const transferService = new TransferService();
