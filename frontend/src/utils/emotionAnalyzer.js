// 情绪识别工具类
// 基于关键词和规则的情绪分析实现

// 情绪关键词库
const emotionKeywords = {
  // 积极情绪
  positive: [
    '好', '很好', '非常好', '棒', '棒极了', '不错', '满意', '开心', '高兴', '快乐',
    '喜欢', '满意', '感谢', '谢谢', '感激', '赞', '优秀', '完美', '出色', '成功'
  ],
  
  // 消极情绪
  negative: [
    '不好', '很差', '非常差', '糟糕', '垃圾', '失望', '生气', '愤怒', '不满', '抱怨',
    '投诉', '退款', '退货', '错误', '失败', '问题', '麻烦', '困难', '痛苦', '伤心'
  ],
  
  // 中性情绪
  neutral: [
    '请问', '咨询', '了解', '知道', '想', '需要', '希望', '能否', '是否', '可以'
  ],
  
  // 转人工关键词
  transfer: [
    '转人工', '人工客服', '人工服务', '真人', '人工', '找客服', '客服人员', '接线员'
  ]
};

// 情绪强度等级
const emotionIntensity = {
  low: 1,
  medium: 2,
  high: 3,
  very_high: 4
};

// 情绪分析类
class EmotionAnalyzer {
  constructor() {
    this.config = {
      // 情绪激动阈值
      transferThreshold: 3, // 当情绪强度达到3或以上时触发转接
      // 关键词权重
      weights: {
        positive: 1,
        negative: 1.5, // 消极情绪权重更高
        neutral: 0.5
      }
    };
  }

  // 分析文本情绪
  analyze(text) {
    if (!text || typeof text !== 'string') {
      return {
        emotion: 'neutral',
        intensity: 1,
        score: 0,
        needsTransfer: false,
        transferRequested: false
      };
    }

    let positiveScore = 0;
    let negativeScore = 0;
    let neutralScore = 0;
    let transferRequested = false;

    // 检查转人工请求
    for (const keyword of emotionKeywords.transfer) {
      if (text.includes(keyword)) {
        transferRequested = true;
        break;
      }
    }

    // 分析情绪
    for (const keyword of emotionKeywords.positive) {
      if (text.includes(keyword)) {
        positiveScore += this.config.weights.positive;
      }
    }

    for (const keyword of emotionKeywords.negative) {
      if (text.includes(keyword)) {
        negativeScore += this.config.weights.negative;
      }
    }

    for (const keyword of emotionKeywords.neutral) {
      if (text.includes(keyword)) {
        neutralScore += this.config.weights.neutral;
      }
    }

    // 计算总得分
    const totalScore = positiveScore - negativeScore;
    
    // 确定情绪类型
    let emotion = 'neutral';
    if (totalScore > 2) {
      emotion = 'positive';
    } else if (totalScore < -2) {
      emotion = 'negative';
    }

    // 计算情绪强度
    const intensityScore = Math.abs(totalScore);
    let intensity = emotionIntensity.low;
    if (intensityScore >= 6) {
      intensity = emotionIntensity.very_high;
    } else if (intensityScore >= 4) {
      intensity = emotionIntensity.high;
    } else if (intensityScore >= 2) {
      intensity = emotionIntensity.medium;
    }

    // 确定是否需要转接
    const needsTransfer = transferRequested || (emotion === 'negative' && intensity >= this.config.transferThreshold);

    return {
      emotion,
      intensity,
      score: totalScore,
      needsTransfer,
      transferRequested,
      intensityLevel: this.getIntensityLevel(intensity)
    };
  }

  // 获取情绪强度等级文本
  getIntensityLevel(intensity) {
    switch (intensity) {
      case emotionIntensity.very_high:
        return '非常强烈';
      case emotionIntensity.high:
        return '强烈';
      case emotionIntensity.medium:
        return '中等';
      case emotionIntensity.low:
      default:
        return '轻微';
    }
  }

  // 获取情绪文本描述
  getEmotionText(emotion) {
    const emotionMap = {
      positive: '积极',
      negative: '消极',
      neutral: '中性'
    };
    return emotionMap[emotion] || '中性';
  }

  // 更新配置
  updateConfig(newConfig) {
    this.config = { ...this.config, ...newConfig };
  }

  // 获取当前配置
  getConfig() {
    return { ...this.config };
  }
}

// 导出单例实例
export const emotionAnalyzer = new EmotionAnalyzer();
