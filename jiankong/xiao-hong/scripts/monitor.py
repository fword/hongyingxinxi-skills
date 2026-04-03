#!/usr/bin/env python3
"""
股票持仓监控脚本 - 跨平台版本（Windows / Mac / Linux）
由小红 skill 注册到系统定时任务，定期检查止盈止损状态。
"""
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime

BASE_URL = "https://www.maxsou.cn/xiaohong"
# skill 目录由安装时写入此变量
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))


def load_config() -> dict:
    config_path = os.path.join(SKILL_DIR, "..", "config.json")
    config_path = os.path.normpath(config_path)
    if not os.path.exists(config_path):
        return {}
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


def load_schedule() -> dict:
    config = load_config()
    return config.get("schedule", {"days": "1-5", "start": "09:25", "end": "15:00"})


def in_time_window(schedule: dict) -> bool:
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    dow = now.isoweekday()  # 1=周一 7=周日

    start = schedule.get("start", "09:25")
    end = schedule.get("end", "15:00")
    days = schedule.get("days", "1-5")

    if current_time < start or current_time > end:
        return False

    if days != "*":
        d_start, d_end = int(days.split("-")[0]), int(days.split("-")[1])
        if dow < d_start or dow > d_end:
            return False

    return True


def http_get(url: str) -> dict | None:
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def main():
    config = load_config()
    token = config.get("token", "").strip()
    if not token:
        print("[jiankong] token 未配置", file=sys.stderr)
        sys.exit(0)

    schedule = load_schedule()
    if not in_time_window(schedule):
        sys.exit(0)

    health = http_get(f"{BASE_URL}/hangqing/health")
    if not health or not health.get("has_data"):
        sys.exit(0)

    result = http_get(f"{BASE_URL}/jiankong/alert/{token}")
    if not result:
        sys.exit(0)

    # 写入日志
    log_path = os.path.join(os.path.dirname(SKILL_DIR), "monitor.log")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n=== {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        f.write(json.dumps(result, ensure_ascii=False, indent=2))
        f.write("\n")


if __name__ == "__main__":
    main()
