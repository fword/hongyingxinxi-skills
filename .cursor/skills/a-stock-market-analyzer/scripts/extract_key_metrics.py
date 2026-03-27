#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取市场核心指标
用法: python extract_key_metrics.py
输出: JSON格式的核心指标，方便进一步处理
"""

import requests
import json
import sys
import io

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def extract_key_metrics():
    """提取核心市场指标"""
    try:
        response = requests.get('http://139.9.141.198:60717/jihejingjia/data', timeout=10)
        data = response.json()
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
    
    ms = data['market_stats']
    lu = data['limit_up_analysis']
    ga = data['gainian_analysis']
    
    # 提取封单TOP10
    all_boards = []
    for board_name, stocks in lu['board_details'].items():
        all_boards.extend(stocks)
    all_boards.sort(key=lambda x: x['buy1_amt'], reverse=True)
    
    top_10_stocks = [
        {
            'name': s['name'],
            'code': s['code'],
            'board': s['board_key'],
            'buy1_amt_yi': round(s['buy1_amt'] / 1e8, 2),
            'reason': s['reason'],
            'time': s['time']
        }
        for s in all_boards[:10]
    ]
    
    # 计算涨跌比例
    up_ratio = round(ms['up_total'] / (ms['up_total'] + ms['down_total']) * 100, 1)
    
    # 分析情绪
    consec_rate = lu['consecutive_rates']['二板']['value']
    if consec_rate > 30:
        mood = "强势"
    elif consec_rate > 15:
        mood = "一般"
    else:
        mood = "较弱"
    
    # 构建核心指标
    metrics = {
        'timestamp': data['timestamp'],
        'market': {
            'total_amount': round(ms['total_amount'], 2),
            'up_total': ms['up_total'],
            'down_total': ms['down_total'],
            'up_ratio': up_ratio,
            'limit_up': lu['total_zt'],
            'limit_down': lu['total_dt']
        },
        'sentiment': {
            'consecutive_rate_2': consec_rate,
            'level': lu['consecutive_rates']['二板']['level'],
            'mood': mood,
            'board_counts': lu['board_counts']
        },
        'top_capital': top_10_stocks,
        'top_gainian': [
            {
                'rank': g['rank'],
                'name': g['gainian_name'],
                'zt_count': g['zt_count'],
                'avg_pct_chg': g['avg_pct_chg']
            }
            for g in ga['top_5_limit_up_count']
        ],
        'gainers': [
            {
                'rank': g['rank'],
                'name': g['gainian_name'],
                'avg_pct_chg': g['avg_pct_chg'],
                'zt_count': g['zt_count']
            }
            for g in ga['top_5_gainers'][:3]
        ]
    }
    
    return metrics


if __name__ == '__main__':
    metrics = extract_key_metrics()
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
