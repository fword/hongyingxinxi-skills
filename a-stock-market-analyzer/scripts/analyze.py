#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股市场数据分析脚本
用法: python analyze.py [--simple]
"""

import requests
import sys
import json
import io

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def fetch_market_data():
    """获取市场数据"""
    try:
        response = requests.get('http://139.9.141.198:60717/jihejingjia/data', timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print("❌ 请求超时，请稍后重试")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络错误: {e}")
        sys.exit(1)
    except json.JSONDecodeError:
        print("❌ 数据解析失败")
        sys.exit(1)


def analyze_market_mood(consecutive_rate):
    """分析市场情绪"""
    if consecutive_rate > 30:
        return "情绪亢奋，延续性强", "✅"
    elif consecutive_rate > 15:
        return "情绪一般，需观察", "⚡"
    else:
        return "情绪较弱，谨慎追高", "⚠️"


def calculate_risk_level(data):
    """计算风险等级"""
    lu = data['limit_up_analysis']
    ms = data['market_stats']
    
    risk_score = 0
    risk_items = []
    
    # 跌停数
    if lu['total_dt'] > 10:
        risk_score += 2
        risk_items.append(f"跌停数{lu['total_dt']}只")
    elif lu['total_dt'] > 5:
        risk_score += 1
    
    # 大跌股票
    da_die = ms['segments']['down'][4]['value'] if len(ms['segments']['down']) > 4 else 0
    if da_die > 100:
        risk_score += 2
        risk_items.append(f"大跌股{da_die}只")
    elif da_die > 50:
        risk_score += 1
    
    # 二板成功率
    consec_rate = lu['consecutive_rates']['二板']['value']
    if consec_rate < 10:
        risk_score += 2
        risk_items.append("连板率极低")
    elif consec_rate < 20:
        risk_score += 1
    
    # 高度板
    if lu['board_counts']['高度板'] == 0 and consec_rate < 10:
        risk_score += 1
        risk_items.append("无高度板")
    
    if risk_score >= 4:
        return "高", risk_items
    elif risk_score >= 2:
        return "中", risk_items
    else:
        return "低", []


def print_full_report(data):
    """生成完整分析报告"""
    ms = data['market_stats']
    lu = data['limit_up_analysis']
    ga = data['gainian_analysis']
    
    print('=' * 60)
    print('📈 A股市场实时分析报告')
    print('=' * 60)
    print(f"\n【数据时间】{data['timestamp']}")
    print()
    
    # 一、市场概况
    print('📊 一、市场概况')
    print('-' * 60)
    print(f"总成交额: {ms['total_amount']:.2f} 亿元")
    print(f"总股票数: {ms['total_stocks']} 只")
    print(f"涨跌比例: {ms['up_total']}只上涨 ↑ / {ms['down_total']}只下跌 ↓")
    
    up_ratio = ms['up_total'] / (ms['up_total'] + ms['down_total']) * 100
    down_ratio = 100 - up_ratio
    print(f"涨跌占比: {up_ratio:.1f}% vs {down_ratio:.1f}%")
    print()
    
    print("涨跌分布:")
    for seg in ms['segments']['up']:
        print(f"  {seg['name']:8s}: {seg['value']:4d}只 ({seg['percentage']:4.1f}%)")
    print(f"  {'平盘':8s}: {ms['flat_total']:4d}只 ({ms['flat_total']/ms['total_stocks']*100:4.1f}%)")
    for seg in ms['segments']['down']:
        print(f"  {seg['name']:8s}: {seg['value']:4d}只 ({seg['percentage']:4.1f}%)")
    print()
    
    # 二、涨停板分析
    print('🔥 二、涨停板分析')
    print('-' * 60)
    print(f"涨停数量: {lu['total_zt']}只 | 跌停数量: {lu['total_dt']}只")
    print()
    print("板块高度分布:")
    print(f"  一板: {lu['board_counts']['一板']}只 (新题材萌芽)")
    print(f"  二板: {lu['board_counts']['二板']}只")
    print(f"  三板: {lu['board_counts']['三板']}只")
    print(f"  高度板: {lu['board_counts']['高度板']}只")
    print()
    
    print("连板成功率分析 (关键情绪指标):")
    for board_name in ['二板', '三板', '高度板']:
        info = lu['consecutive_rates'][board_name]
        print(f"  {board_name}: {info['value']}% (等级: {info['level']})")
        print(f"    → {info['description']}")
    print()
    
    # 情绪判断
    consec_rate = lu['consecutive_rates']['二板']['value']
    mood, emoji = analyze_market_mood(consec_rate)
    print(f"{emoji} 【市场情绪】: {mood} (二板成功率{consec_rate}%)")
    print()
    
    # 三、封单金额TOP10
    print('💰 三、封单金额TOP10 (主力资金强度)')
    print('-' * 60)
    all_boards = []
    for board_name, stocks in lu['board_details'].items():
        all_boards.extend(stocks)
    all_boards.sort(key=lambda x: x['buy1_amt'], reverse=True)
    
    for i, stock in enumerate(all_boards[:10], 1):
        amt_yi = stock['buy1_amt'] / 1e8
        print(f"{i:2d}. {stock['name']:8s} ({stock['code']}) [{stock['board_key']}]")
        print(f"    封单: {amt_yi:.2f}亿 | 涨停: {stock['time']} | 题材: {stock['reason']}")
    print()
    
    # 四、概念板块表现
    print('🎯 四、概念板块表现')
    print('-' * 60)
    print("【涨幅榜TOP5】")
    for g in ga['top_5_gainers']:
        print(f"{g['rank']}. {g['gainian_name']}: 平均涨幅{g['avg_pct_chg']:.2f}%, 涨停{g['zt_count']}只")
        print(f"   代表股: {g['representative_stocks']}")
    print()
    
    print("【涨停数量TOP5】")
    for g in ga['top_5_limit_up_count']:
        print(f"{g['rank']}. {g['gainian_name']}: {g['zt_count']}只涨停, 平均涨幅{g['avg_pct_chg']:.2f}%")
        if 'stocks_display' in g:
            print(f"   涨停股: {g['stocks_display']}")
    print()
    
    # 五、市场热点总结
    print('💡 五、市场热点总结')
    print('-' * 60)
    
    print("✅ 【市场优势】")
    if up_ratio > 75:
        print(f"  • 普涨行情，{up_ratio:.1f}%个股上涨，赚钱效应好")
    print(f"  • 涨停{lu['total_zt']}只，市场活跃度{'高' if lu['total_zt'] > 80 else '中等'}")
    print()
    
    print("📈 【主流题材】")
    top_gainian = ga['top_5_limit_up_count'][0]
    print(f"  • 最强板块: {top_gainian['gainian_name']} ({top_gainian['zt_count']}只涨停)")
    top_gainer = ga['top_5_gainers'][0]
    print(f"  • 涨幅最高: {top_gainer['gainian_name']} (平均{top_gainer['avg_pct_chg']:.2f}%)")
    print()
    
    print("💰 【资金流向】")
    top_stock = all_boards[0]
    print(f"  • 封单最强: {top_stock['name']} - {top_stock['buy1_amt']/1e8:.2f}亿")
    print(f"  • 题材方向: {top_stock['reason']}")
    print()
    
    # 风险评估
    risk_level, risk_items = calculate_risk_level(data)
    print(f"⚠️  【风险等级】: {risk_level}")
    if risk_items:
        print(f"  • 风险点: {', '.join(risk_items)}")
    else:
        print("  • 市场运行平稳")
    print()
    
    # 操作建议
    print("📋 【操作建议】")
    if consec_rate < 15:
        print("  • 适合: 关注低位首板，避免追高")
        print("  • 谨慎: 不建议追二板以上，连板率太低")
    elif consec_rate < 30:
        print("  • 适合: 可适当参与二板，控制仓位")
        print("  • 谨慎: 三板以上需观察持续性")
    else:
        print("  • 适合: 可积极参与连板股")
        print("  • 关注: 高度板龙头")
    
    print(f"  • 重点方向: {top_gainian['gainian_name']}、{ga['top_5_limit_up_count'][1]['gainian_name']}")
    print()
    print('=' * 60)


def print_simple_report(data):
    """生成简化报告"""
    ms = data['market_stats']
    lu = data['limit_up_analysis']
    ga = data['gainian_analysis']
    
    print(f"\n【{data['timestamp']}】A股市场快报")
    print('-' * 50)
    
    # 核心指标
    print(f"成交额: {ms['total_amount']:.0f}亿 | 涨跌: {ms['up_total']}↑/{ms['down_total']}↓ | 涨停: {lu['total_zt']}只")
    
    # 情绪
    consec_rate = lu['consecutive_rates']['二板']['value']
    mood, emoji = analyze_market_mood(consec_rate)
    print(f"{emoji} 情绪: {mood} (二板率{consec_rate}%)")
    
    # 封单TOP3
    all_boards = []
    for board_name, stocks in lu['board_details'].items():
        all_boards.extend(stocks)
    all_boards.sort(key=lambda x: x['buy1_amt'], reverse=True)
    
    print(f"\n💰 封单TOP3:")
    for i, stock in enumerate(all_boards[:3], 1):
        print(f"{i}. {stock['name']} - {stock['buy1_amt']/1e8:.2f}亿 - {stock['reason']}")
    
    # 最强概念
    top_gainian = ga['top_5_limit_up_count'][0]
    print(f"\n🎯 最强板块: {top_gainian['gainian_name']} ({top_gainian['zt_count']}只涨停)")
    print('-' * 50)


def main():
    """主函数"""
    # 检查命令行参数
    simple_mode = '--simple' in sys.argv
    
    # 获取数据
    print("正在获取市场数据...")
    data = fetch_market_data()
    
    # 生成报告
    if simple_mode:
        print_simple_report(data)
    else:
        print_full_report(data)


if __name__ == '__main__':
    main()
