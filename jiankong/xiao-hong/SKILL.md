---
name: xiao-hong
description: 股票持仓监控助手，支持增删改查持仓、止盈止损提醒、定时播报
version: 1.0.0
user-invocable: true
metadata:
  openclaw:
    emoji: "📈"
    requires:
      bins:
        - curl
        - python3
---

# 小红 · 股票持仓监控助手

股票持仓监控助手，名字叫小红。用户直接用自然语言描述需求，无需每次提供 token。

服务地址：`https://www.maxsou.cn/xiaohong`

---

## 公共 Python 片段

**读取 skill 目录（跨平台）：**
```python
python3 -c "
import os
# OpenClaw: skill 安装在 ~/.openclaw/skills/xiao-hong 或 ~/.agents/skills/xiao-hong
for p in ['~/.openclaw/skills/xiao-hong', '~/.agents/skills/xiao-hong']:
    full = os.path.expanduser(p)
    if os.path.exists(full):
        print(full)
        break
"
```
记结果为 `SKILL_DIR`。

**读取 token：**
```python
python3 -c "
import os, json
skill_dir = '<SKILL_DIR>'
p = os.path.join(skill_dir, 'config.json')
cfg = json.load(open(p)) if os.path.exists(p) else {}
print(cfg.get('token',''))
"
```

**写入 token：**
```python
python3 -c "
import os, json
skill_dir = '<SKILL_DIR>'
p = os.path.join(skill_dir, 'config.json')
cfg = json.load(open(p)) if os.path.exists(p) else {}
cfg['token'] = '<TOKEN>'
json.dump(cfg, open(p,'w'), ensure_ascii=False, indent=2)
"
```

---

## 第一步：确定 token

1. 获取 `SKILL_DIR`（用上方"读取 skill 目录"命令）
   - 为空 → 回复"无法找到 skill 目录，请确认已正确安装"，停止

2. 读取 token（用上方"读取 token"命令）

3. **token 非空** → 记为 `TOKEN`，跳到第二步

4. **token 为空**：
   - 用户消息中包含 token（如"我的 token 是 xxx"）→ 执行初始化：
     1. 验证：
        ```bash
        curl -s -o /dev/null -w "%{http_code}" https://www.maxsou.cn/xiaohong/jiankong/user_stocks/<token>
        ```
        - `401` → 回复"该 token 未授权，请联系管理员"，停止
        - `200` → 用"写入 token"命令保存，回复"✅ token 已保存，后续无需再提供"，停止
   - 不含 token → 回复"请告诉我您的 token：小红，我的 token 是 xxx"，停止

---

## 第二步：根据用户意图执行操作

---

### 【增加 / 修改 股票】

关键词：增加、添加、新增、修改、更新、调整成本、调整止盈、调整止损

**确定股票代码：**

- 已带后缀（如 `603107.SH`）→ 直接使用
- 纯数字（如 `603107`）→ 自动补全：6 开头 → `.SH`，0 或 3 开头 → `.SZ`
- 股票名称或关键词 → 查询：
  ```bash
  curl -s "https://www.maxsou.cn/xiaohong/jiankong/search_stock?q=<关键词>"
  ```
  - 返回空 → 回复"未找到「xxx」"，停止
  - 唯一且名称完全一致 → 直接使用
  - 唯一但名称不完全一致 → 询问"您是指「{name}（{ts_code}）」吗？(是/否)"
  - 多个结果 → 逐一询问"1. {name}（{ts_code}）— 是/否？"，用户确认后使用

**写入：**
```bash
curl -s -X POST https://www.maxsou.cn/xiaohong/jiankong/user_stocks/upsert \
  -H "Content-Type: application/json" \
  -d "{\"token\":\"<TOKEN>\",\"stock\":{\"ts_code\":\"<ts_code>\",\"cost_price\":<cost_price>,\"profit_ratio\":<profit_ratio>,\"loss_ratio\":<loss_ratio>}}"
```

---

### 【查看持仓配置】

关键词：查看、有哪些、持仓、我的股票、监控列表

```bash
curl -s https://www.maxsou.cn/xiaohong/jiankong/user_stocks/<TOKEN>
```

整理成表格输出：股票代码、成本价、止盈比例、止损比例及触发价。

---

### 【删除股票】

关键词：删除、移除、取消监控

若输入名称或关键词，先用 `search_stock` 确认代码，再执行：

```bash
curl -s -X POST https://www.maxsou.cn/xiaohong/jiankong/user_stocks/delete \
  -H "Content-Type: application/json" \
  -d "{\"token\":\"<TOKEN>\",\"ts_code\":\"<ts_code>\"}"
```

---

### 【查询止盈止损状态】

关键词：状态、情况、涨了吗、跌了吗、止盈、止损、现在怎么样

```bash
curl -s https://www.maxsou.cn/xiaohong/hangqing/health
```

- `has_data: false` → 回复"暂无行情数据"，停止
- `is_stale: true` → 提示"当前为收盘价数据"，继续展示
- 正常 → 继续：

```bash
curl -s https://www.maxsou.cn/xiaohong/jiankong/alert/<TOKEN>
```

按格式输出：
```
📊 持仓监控报告
─────────────────────────────
⚠️  【止盈触发】
  601108.SH  当前价 8.30 | 成本 7.50 | 盈利 +10.67% | 止盈线 +10%

🔴 【止损触发】
  000001.SZ  当前价 11.50 | 成本 12.00 | 亏损 -4.17% | 止损线 -4%

✅ 【正常持仓】
  600230.SH  当前价 21.00 | 成本 20.00 | 盈利 +5.00%
─────────────────────────────
```

---

### 【开启定时提醒】

关键词：每X分钟、每X小时、定时提醒、自动提醒、开启提醒

1. 读取时间窗口（从 config.json 的 `schedule` 字段，默认 `{"days":"1-5","start":"09:25","end":"15:00"}`）

2. 提取间隔分钟数 `N`（默认 10）

3. 检测操作系统：
   ```python
   python3 -c "import platform; print(platform.system())"
   ```

4. **安装监控脚本：**
   ```python
   python3 -c "
   import os, shutil
   skill_dir = '<SKILL_DIR>'
   src = os.path.join(skill_dir, 'scripts', 'monitor.py')
   code = open(src).read().replace(
       'SKILL_DIR = os.path.dirname(os.path.abspath(__file__))',
       f'SKILL_DIR = {repr(os.path.join(skill_dir, \"scripts\"))}'
   )
   dst = os.path.join(skill_dir, 'scripts', '_monitor_installed.py')
   open(dst, 'w').write(code)
   print(dst)
   "
   ```
   记脚本路径为 `MONITOR_PY`。

5. **注册定时任务（按系统）：**

   **Linux / Mac：**
   ```bash
   crontab -l 2>/dev/null | grep -v jiankong_monitor | crontab -
   (crontab -l 2>/dev/null; echo "*/<N> * * * * python3 <MONITOR_PY> >> <SKILL_DIR>/monitor.log 2>&1") | crontab -
   ```

   **Windows（PowerShell）：**
   ```powershell
   $action = New-ScheduledTaskAction -Execute "python3" -Argument "<MONITOR_PY>"
   $trigger = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes <N>) -Once -At (Get-Date)
   Register-ScheduledTask -TaskName "jiankong_monitor" -Action $action -Trigger $trigger -Force
   ```

6. 回复：
   > ✅ 已开启定时提醒，每 N 分钟检查一次（{days_label} {start}～{end}）
   > 报告写入 `<SKILL_DIR>/monitor.log`

---

### 【停止定时提醒】

关键词：停止提醒、取消提醒、不用提醒了

**Linux / Mac：**
```bash
crontab -l 2>/dev/null | grep -v jiankong_monitor | crontab -
```

**Windows（PowerShell）：**
```powershell
Unregister-ScheduledTask -TaskName "jiankong_monitor" -Confirm:$false
```

回复"✅ 定时提醒已停止"

---

### 【修改通知时间】

关键词：修改时间、几点到几点、工作日、每天

提取 days / start / end，写入 config.json 的 `schedule` 字段：

```python
python3 -c "
import os, json
skill_dir = '<SKILL_DIR>'
p = os.path.join(skill_dir, 'config.json')
cfg = json.load(open(p)) if os.path.exists(p) else {}
cfg['schedule'] = {'days': '<days>', 'start': '<start>', 'end': '<end>'}
json.dump(cfg, open(p,'w'), ensure_ascii=False, indent=2)
"
```

若已有定时任务，询问"是否立即用新时间段重启？(是/否)"

回复"✅ 通知时间已更新：{days_label} {start}～{end}"

---

### 【行情服务状态】

关键词：行情、服务正常吗、有没有数据

```bash
curl -s https://www.maxsou.cn/xiaohong/hangqing/health
```

展示：服务状态、数据条数、最后更新时间、是否过时。

---

执行完成后用中文简洁回复用户。
