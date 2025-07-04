#!/usr/bin/env python3
"""
簡化版初始化腳本 - 直接使用 period="max" 獲取最完整數據
更快速且數據更完整
"""

import yfinance as yf
import pandas as pd
import json
from datetime import datetime
import time
import os

def ensure_data_directory():
    """確保數據目錄存在"""
    if not os.path.exists('stock_data'):
        os.makedirs('stock_data')

def load_companies():
    """載入公司列表"""
    with open('companies.json', 'r', encoding='utf-8') as f:
        companies = json.load(f)
    return companies

def fetch_max_history(symbol):
    """
    直接使用 period="max" 獲取最完整的歷史數據
    """
    try:
        ticker_symbol = f"{symbol}.TW"
        stock = yf.Ticker(ticker_symbol)
        
        print(f"  使用 period='max' 獲取最完整數據...")
        df = stock.history(period="max")
        
        if df.empty:
            print(f"  ❌ 無法獲取數據")
            return {}
        
        print(f"  ✅ 成功獲取 {len(df)} 筆數據")
        print(f"  數據範圍: {df.index[0].strftime('%Y-%m-%d')} 到 {df.index[-1].strftime('%Y-%m-%d')}")
        
        # 轉換為價格字典
        prices = {}
        for date, row in df.iterrows():
            if pd.notna(row['Close']):
                date_str = date.strftime('%Y-%m-%d')
                prices[date_str] = round(float(row['Close']), 2)
        
        return prices
        
    except Exception as e:
        print(f"  ❌ 獲取數據失敗: {e}")
        return {}

def init_all_stock_data_simple():
    """
    簡化版：直接使用 max period 初始化所有股票數據
    """
    ensure_data_directory()
    companies = load_companies()
    
    success_count = 0
    total_count = len(companies)
    
    print(f"=== 簡化版初始化：{total_count} 支股票 ===")
    print("策略：直接使用 period='max' 獲取最完整數據")
    print()
    
    for i, (symbol, company) in enumerate(companies.items(), 1):
        print(f"[{i}/{total_count}] {symbol} ({company.get('chinese_name', '')})")
        
        # 直接獲取最大範圍數據
        prices = fetch_max_history(symbol)
        
        if not prices:
            print(f"  ❌ 跳過")
            continue
        
        # 排序價格數據
        sorted_prices = dict(sorted(prices.items()))
        
        # 創建股票數據結構
        stock_data = {
            'symbol': symbol,
            'ipo_date': company.get('ipo_date'),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_source': 'yfinance_max_period',
            'total_records': len(sorted_prices),
            'date_range': {
                'start': min(sorted_prices.keys()) if sorted_prices else None,
                'end': max(sorted_prices.keys()) if sorted_prices else None
            },
            'prices': sorted_prices
        }
        
        # 保存到文件
        file_path = f'stock_data/{symbol}.json'
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(stock_data, f, ensure_ascii=False, indent=2)
            
            print(f"  ✅ 保存成功：{len(sorted_prices)} 筆數據")
            success_count += 1
            
        except Exception as e:
            print(f"  ❌ 保存失敗: {e}")
        
        print()
        
        # 控制請求頻率
        time.sleep(1)
    
    print(f"=== 完成 ===")
    print(f"成功: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    return success_count, total_count

def main():
    try:
        success, total = init_all_stock_data_simple()
        
        if success == total:
            print("🎉 所有股票數據初始化成功！")
        else:
            print(f"⚠️ 成功率: {success/total*100:.1f}%")
            
    except Exception as e:
        print(f"初始化失敗: {e}")

if __name__ == "__main__":
    main()