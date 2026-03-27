# A股市场分析器脚本

本目录包含用于分析A股市场数据的实用脚本。

## 脚本列表

### 1. analyze.py - 市场分析报告生成器

生成格式化的市场分析报告。

**用法**:

```bash
# 完整报告（包含详细的涨跌分布、封单TOP10、概念板块等）
python scripts/analyze.py

# 简化报告（只显示核心指标，快速查看）
python scripts/analyze.py --simple
```

**输出内容**:
- 市场概况（成交额、涨跌比）
- 涨停板分析（板高度、连板率、情绪判断）
- 封单金额TOP10
- 概念板块TOP5
- 市场热点总结和操作建议

### 2. extract_key_metrics.py - 核心指标提取器

提取市场核心指标，输出JSON格式，便于进一步处理或保存。

**用法**:

```bash
# 输出到控制台
python scripts/extract_key_metrics.py

# 保存到文件
python scripts/extract_key_metrics.py > metrics.json
```

**输出字段**:
```json
{
  "timestamp": "时间戳",
  "market": {
    "total_amount": "成交额",
    "up_total": "上涨数",
    "down_total": "下跌数",
    "up_ratio": "上涨比例%",
    "limit_up": "涨停数",
    "limit_down": "跌停数"
  },
  "sentiment": {
    "consecutive_rate_2": "二板成功率",
    "mood": "情绪评级",
    "board_counts": "板高度分布"
  },
  "top_capital": "封单TOP10数组",
  "top_gainian": "涨停最多板块TOP5",
  "gainers": "涨幅最高板块TOP3"
}
```

## 依赖要求

```bash
pip install requests
```

## 注意事项

- 脚本已处理Windows控制台编码问题
- 包含错误处理和超时控制（10秒）
- 封单金额自动转换为亿元单位
- 支持情绪自动判断和风险等级评估
