# A股市场分析器

A股实时行情数据分析工具，提供市场概况、涨停板分析、概念板块表现等全方位市场诊断。

## 功能特性

- ✅ 实时获取A股市场数据
- ✅ 涨停板深度分析（连板率、封单金额、板高度）
- ✅ 概念板块排名（涨幅TOP5、涨停数TOP5）
- ✅ 市场情绪智能判断
- ✅ 风险等级自动评估
- ✅ 操作建议生成

## 快速使用

### 方式1：使用预置脚本（推荐）

```bash
# 完整分析报告
python .cursor/skills/a-stock-market-analyzer/scripts/analyze.py

# 快速查看（简化版）
python .cursor/skills/a-stock-market-analyzer/scripts/analyze.py --simple

# 提取JSON数据
python .cursor/skills/a-stock-market-analyzer/scripts/extract_key_metrics.py
```

### 方式2：在对话中询问

直接问Agent：
- "今天A股怎么样？"
- "涨停板情况如何？"
- "什么板块最强？"
- "现在能追高吗？"

Agent会自动调用此skill进行分析。

## 核心指标说明

| 指标 | 健康标准 | 说明 |
|------|---------|------|
| **涨跌比** | > 3:1 | 上涨股票数/下跌股票数 |
| **二板率** | > 20% | 昨日一板今日成二板的比例，核心情绪指标 |
| **涨停数** | > 80只 | 反映市场活跃度 |
| **封单强度** | > 5亿 | 第一名封单金额，反映资金强度 |

## 市场情绪判断

- **二板率 > 30%**: 情绪强势，可积极参与连板 ✅
- **二板率 15-30%**: 情绪一般，谨慎操作 ⚡
- **二板率 < 15%**: 情绪较弱，避免追高 ⚠️

## 文件结构

```
a-stock-market-analyzer/
├── SKILL.md              # 主要说明文档
├── README.md            # 本文件
└── scripts/
    ├── README.md        # 脚本详细说明
    ├── analyze.py       # 市场分析报告生成器
    └── extract_key_metrics.py  # 核心指标提取器
```

## 依赖安装

```bash
pip install requests
```

## 示例输出

### 简化报告示例

```
【20260327 14:32】A股市场快报
--------------------------------------------------
成交额: 27394亿 | 涨跌: 4125↑/1072↓ | 涨停: 72只
⚠️ 情绪: 情绪较弱，谨慎追高 (二板率3.4%)

💰 封单TOP3:
1. 赣锋锂业 - 5.25亿 - 固态电池+人形机器人+锂矿龙头
2. 东方新能 - 5.03亿 - 风电+绿色能源
3. 诺德股份 - 4.90亿 - HVLP铜箔+固态电池铜箔

🎯 最强板块: 锂电池 (18只涨停)
```

### JSON输出示例

```json
{
  "market": {
    "total_amount": 27394.52,
    "up_total": 4125,
    "down_total": 1072,
    "up_ratio": 79.4,
    "limit_up": 72
  },
  "sentiment": {
    "consecutive_rate_2": 3.4,
    "mood": "较弱"
  },
  "top_capital": [
    {
      "name": "赣锋锂业",
      "buy1_amt_yi": 5.25,
      "reason": "固态电池+人形机器人+锂矿龙头"
    }
  ]
}
```

## 数据来源

**配置说明**: 使用前需要在脚本中配置API地址

1. 编辑 `scripts/analyze.py`，设置 `API_URL` 变量
2. 编辑 `scripts/extract_key_metrics.py`，设置 `API_URL` 变量
3. 在 `SKILL.md` 中的代码示例也需要替换为实际地址

数据更新频率: 实时（交易时间内约每3分钟更新）
