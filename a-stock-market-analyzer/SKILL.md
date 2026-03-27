---
name: a-stock-market-analyzer
description: 获取并分析A股实时行情数据。通过HTTP API获取涨跌统计、涨停板分析（连板率、封单金额）、概念板块表现，生成市场分析报告。当用户询问大盘、行情、涨停板、市场情况、板块表现、能否追高时使用。
---

# A股市场分析器

本skill用于获取和分析A股市场实时数据，生成市场概况报告。

## 快速开始

### 方式1：使用预置脚本（推荐 ⭐）

直接执行分析脚本生成完整报告：

```bash
python .cursor/skills/a-stock-market-analyzer/scripts/analyze.py
```

或生成简化版报告：

```bash
python .cursor/skills/a-stock-market-analyzer/scripts/analyze.py --simple
```

提取核心指标（JSON格式）：

```bash
python .cursor/skills/a-stock-market-analyzer/scripts/extract_key_metrics.py
```

**优势**：
- 已处理所有编码问题
- 包含错误处理和超时控制
- 格式统一、输出美观
- 自动计算情绪和风险等级

### 方式2：手动编写代码（自定义分析时）

```python
# 1. 获取数据（必须用Python，避免编码问题）
import requests
API_URL = 'YOUR_API_URL_HERE'  # 替换为实际的API地址
r = requests.get(API_URL)
data = r.json()

# 2. 提取关键数据
ms = data['market_stats']          # 市场统计
lu = data['limit_up_analysis']     # 涨停板分析
ga = data['gainian_analysis']      # 概念板块

# 3. 关键指标
涨跌比 = f"{ms['up_total']} / {ms['down_total']}"
连板率 = lu['consecutive_rates']['二板']['value']  # <15%需谨慎
封单TOP = sorted(所有涨停股, key=封单金额)[:10]
```

## 分析重点优先级

1. **市场情绪**（最重要）- 看二板连板率，<15%表示情绪弱
2. **主流题材** - 看涨停数量最多的概念板块
3. **资金强度** - 看封单金额TOP10
4. **风险评估** - 看跌停数、大跌股数量

## 预置工具脚本

为提高效率和可靠性，本skill提供两个Python脚本：

### 1. analyze.py - 完整报告生成器

```bash
# 生成详细的市场分析报告
python scripts/analyze.py

# 生成简化快报（只看核心指标）
python scripts/analyze.py --simple
```

**功能**：
- 自动获取数据（已处理编码和异常）
- 分析市场情绪、连板率、封单排名
- 生成格式化报告（含emoji和分隔线）
- 提供操作建议和风险评估

### 2. extract_key_metrics.py - 核心指标提取

```bash
# 输出JSON格式的核心指标
python scripts/extract_key_metrics.py

# 保存到文件供后续处理
python scripts/extract_key_metrics.py > metrics.json
```

**输出内容**：市场统计、情绪评级、封单TOP10、热门概念等结构化数据。

**使用建议**：
- 当用户问"大盘怎么样"时 → 直接运行 `analyze.py`
- 需要快速查看 → 运行 `analyze.py --simple`
- 需要进一步分析或保存数据 → 运行 `extract_key_metrics.py`

详细说明见 [scripts/README.md](scripts/README.md)

## 数据获取

**优先使用预置脚本** - 已处理编码和异常：

```bash
# 完整报告
python scripts/analyze.py

# 简化报告
python scripts/analyze.py --simple

# 提取JSON指标
python scripts/extract_key_metrics.py
```

**手动获取** - 当需要自定义分析时：

```python
import requests
# 替换为你的API地址
API_URL = 'YOUR_API_URL_HERE'
response = requests.get(API_URL)
data = response.json()
```

注意：避免使用PowerShell或curl，会有中文乱码问题。

## 数据结构（关键字段）

API返回JSON，主要使用：

- `market_stats`: 市场统计
  - `total_amount`: 成交额（亿元）
  - `up_total` / `down_total`: 涨跌数量
  - `segments`: 涨跌分布数组

- `limit_up_analysis`: 涨停板数据
  - `board_counts`: 板高度统计
  - `consecutive_rates`: **连板率（核心指标）**
  - `board_details`: 涨停股详情（含`buy1_amt`封单金额、`reason`题材）

- `gainian_analysis`: 概念板块
  - `top_5_gainers`: 涨幅TOP5
  - `top_5_limit_up_count`: 涨停数TOP5（含`zt_count`、`avg_pct_chg`）

## 核心诊断指标

快速判断市场状态的关键指标：

| 指标 | 计算方式 | 健康标准 |
|------|---------|---------|
| **涨跌比** | up_total / down_total | > 3:1 为强势 |
| **二板率** | 连板率['二板']['value'] | > 20% 为健康 |
| **涨停数** | total_zt | > 80只 为活跃 |
| **封单强度** | TOP1封单金额 | > 5亿 为强势 |
| **主流板块** | 涨停数TOP1 | > 15只 有主线 |

## 报告生成要点

生成报告时按以下优先级：

1. **开头必须包含**：成交额、涨跌比、涨停数
2. **核心分析**：连板率 + 情绪判断（最重要）
3. **资金流向**：封单TOP5-10即可
4. **热点识别**：涨停数最多的概念（TOP3）
5. **结论建议**：根据连板率给出操作策略

报告格式使用markdown + emoji，分5个部分：
- 📊 市场概况
- 🔥 涨停板分析（强调连板率）
- 💰 封单金额TOP10
- 🎯 概念板块表现
- 💡 市场热点总结（优势+风险+建议）

## 分析要点

### 1. 市场情绪判断标准
- **连板率 > 30%**: 情绪较好，延续性强 ✅
- **连板率 15-30%**: 情绪一般，需观察 ⚡
- **连板率 < 15%**: 情绪较弱，谨慎追高 ⚠️

### 2. 封单金额解读
- **> 3亿**: 主力资金强势介入，确定性强
- **1-3亿**: 中等资金关注，可持续观察
- **< 1亿**: 散户情绪为主，持续性存疑

### 3. 板块轮动识别方法
- 找出涨停数量多（>5只）且平均涨幅高（>3%）的概念
- 对比涨幅榜和涨停榜，交集部分为最强主线
- 跌幅榜中出现前期热点板块 → 警惕板块切换

### 4. 风险等级评估

| 指标 | 低风险 | 中风险 | 高风险 |
|------|--------|--------|--------|
| 跌停数 | < 5只 | 5-10只 | > 10只 |
| 大跌股票 | < 50只 | 50-100只 | > 100只 |
| 二板成功率 | > 20% | 10-20% | < 10% |
| 高度板 | > 0只 | 0只 | 0只且连板率<10% |

综合评估：任意2项达到高风险 → 风险等级为高

### 5. 题材热度判断
- **持续性强**：涨停数>10只 且 平均涨幅>3% 且 封单TOP10中占3只以上
- **一日游**：涨停数多但平均涨幅低(<2%) 或 封单金额普遍<1亿
- **分歧加大**：涨幅榜TOP1在跌幅榜也出现 → 板块内部分化严重

## 使用方法

### 快速分析流程

1. **获取数据**（使用Python避免编码问题）
```python
import requests
r = requests.get('http://139.9.141.198:60717/jihejingjia/data')
data = r.json()
```

2. **提取核心指标**
```python
ms = data['market_stats']          # 市场统计
lu = data['limit_up_analysis']     # 涨停板数据
ga = data['gainian_analysis']      # 概念板块数据
```

3. **生成分析报告**
- 先给出市场概况（成交额、涨跌比）
- 重点分析连板率（最关键的情绪指标）
- 展示封单TOP10（资金流向）
- 总结热点板块和操作建议

### 典型问题处理

**用户问**: "今天A股怎么样？"
- 重点：市场涨跌比、涨停数量、主流题材、情绪判断

**用户问**: "涨停板情况如何？"
- 重点：连板率分析、封单金额TOP10、板高度分布

**用户问**: "什么板块最强？"
- 重点：概念板块涨停数量排名、涨幅榜对比

**用户问**: "现在能追高吗？"
- 重点：连板率、高度板情况、风险等级评估

## 注意事项

### 编码问题
- **必须使用Python的requests库**，PowerShell会有中文乱码
- 避免使用curl或PowerShell直接解析JSON

### 数据说明
- 数据为实时快照，务必标注时间戳
- 封单金额单位为**元**，展示时转换为**亿元**（除以1e8）
- 连板率level：低、中、高
- 涨停原因包含多个题材，用"+"分隔

### 关键计算
```python
# 封单金额转换
amt_yi = buy1_amt / 1e8  # 元 → 亿元

# 涨跌比例
up_ratio = up_total / (up_total + down_total) * 100

# 市场情绪判断
if consecutive_rate_2 > 30:
    mood = "情绪亢奋"
elif consecutive_rate_2 > 15:
    mood = "情绪一般"
else:
    mood = "情绪较弱，谨慎追高"
```

### API异常处理
- 如果请求超时（>5秒），提示用户稍后重试
- 如果返回错误，检查网络连接或API状态

## 完整代码示例

### 推荐：直接使用预置脚本

最简单的方式是直接执行脚本：

```bash
# 完整分析报告
python .cursor/skills/a-stock-market-analyzer/scripts/analyze.py

# 快速查看核心指标
python .cursor/skills/a-stock-market-analyzer/scripts/analyze.py --simple
```

### 自定义分析代码

当需要特殊分析逻辑时，参考以下代码：

```python
import requests

# 获取数据（替换为你的API地址）
API_URL = 'YOUR_API_URL_HERE'
r = requests.get(API_URL)
data = r.json()

ms = data['market_stats']
lu = data['limit_up_analysis']
ga = data['gainian_analysis']

# 市场概况
print(f"总成交额: {ms['total_amount']:.2f}亿元")
print(f"涨跌比: {ms['up_total']}↑ / {ms['down_total']}↓")

# 连板率分析（关键）
consec_rate = lu['consecutive_rates']['二板']['value']
mood = "情绪较弱" if consec_rate < 15 else "情绪一般" if consec_rate < 30 else "情绪强势"
print(f"市场情绪: {mood} (二板率{consec_rate}%)")

# 封单TOP10
all_stocks = []
for board_name, stocks in lu['board_details'].items():
    all_stocks.extend(stocks)
all_stocks.sort(key=lambda x: x['buy1_amt'], reverse=True)

print("\n封单TOP10:")
for i, stock in enumerate(all_stocks[:10], 1):
    amt = stock['buy1_amt'] / 1e8
    print(f"{i}. {stock['name']} - {amt:.2f}亿 - {stock['reason']}")

# 最强概念
print(f"\n最强概念: {ga['top_5_limit_up_count'][0]['gainian_name']}")
print(f"涨停数: {ga['top_5_limit_up_count'][0]['zt_count']}只")
```
