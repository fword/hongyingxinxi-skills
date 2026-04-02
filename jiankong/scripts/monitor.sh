#!/bin/bash
# 股票持仓监控脚本 - 由小红 skill 安装到 ~/.jiankong_monitor.sh
# 每次触发时检查时间窗口，窗口内才查询并输出报告

TOKEN=$(cat ~/.jiankong_token 2>/dev/null)
if [[ -z "$TOKEN" ]]; then
    echo "[jiankong] token 未配置，跳过" >&2
    exit 0
fi

# 读取时间窗口配置，默认周一至周五 09:25-15:00
SCHEDULE=$(cat ~/.jiankong_schedule 2>/dev/null || echo '{"days":"1-5","start":"09:25","end":"15:00"}')
START=$(echo "$SCHEDULE" | python3 -c "import sys,json; print(json.load(sys.stdin)['start'])")
END=$(echo "$SCHEDULE"   | python3 -c "import sys,json; print(json.load(sys.stdin)['end'])")
DAYS=$(echo "$SCHEDULE"  | python3 -c "import sys,json; print(json.load(sys.stdin)['days'])")

NOW=$(date +"%H:%M")
DOW=$(date +"%u")  # 1=周一 7=周日

# 时间范围检查（HH:MM 字符串字典序等价于时间大小）
if [[ "$NOW" < "$START" || "$NOW" > "$END" ]]; then
    exit 0
fi

# 星期检查（支持 * / 1-5 / 1-6 格式）
if [[ "$DAYS" != "*" ]]; then
    D_START=${DAYS%-*}
    D_END=${DAYS#*-}
    if [[ "$DOW" -lt "$D_START" || "$DOW" -gt "$D_END" ]]; then
        exit 0
    fi
fi

BASE_URL="https://www.maxsou.cn/xiaohong"

# 检查行情服务
HAS_DATA=$(curl -s "$BASE_URL/hangqing/health" | python3 -c "import sys,json; print(json.load(sys.stdin).get('has_data',False))" 2>/dev/null)
if [[ "$HAS_DATA" != "True" ]]; then
    exit 0
fi

# 查询止盈止损状态，输出到日志
echo "=== $(date '+%Y-%m-%d %H:%M:%S') ===" >> ~/.jiankong_monitor.log
curl -s "$BASE_URL/jiankong/alert/$TOKEN" >> ~/.jiankong_monitor.log 2>&1
echo "" >> ~/.jiankong_monitor.log
