#!/usr/bin/env python3
"""
每日增量更新股票數據腳本
只更新最新的股價數據，保留舊數據不變
快速且不會出現數據缺失問題
"""

import yfinance as yf
import pandas as pd
import json
from datetime import datetime, timedelta
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

def load_existing_data(symbol):
    """
    載入現有的股票數據
    """
    file_path = f'stock_data/{symbol}.json'
    
    if not os.path.exists(file_path):
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"  ⚠️ 讀取現有數據失敗: {e}")
        return None

def get_latest_prices(symbol, start_date):
    """
    獲取指定日期之後的最新價格數據
    """
    try:
        ticker_symbol = f"{symbol}.TW"
        stock = yf.Ticker(ticker_symbol)
        
        # 獲取從指定日期開始的數據
        df = stock.history(start=start_date)
        
        if df.empty:
            return {}
        
        # 轉換為價格字典
        prices = {}
        for date, row in df.iterrows():
            if pd.notna(row['Close']):
                date_str = date.strftime('%Y-%m-%d')
                prices[date_str] = round(float(row['Close']), 2)
        
        return prices
        
    except Exception as e:
        print(f"  ❌ 獲取最新數據失敗: {e}")
        return {}

def update_stock_data(symbol, existing_data, new_prices):
    """
    更新股票數據，合併新舊數據
    """
    if not new_prices:
        return existing_data, 0
    
    # 獲取現有價格數據
    existing_prices = existing_data.get('prices', {})
    
    # 計算新增的數據筆數
    new_count = 0
    for date, price in new_prices.items():
        if date not in existing_prices:
            existing_prices[date] = price
            new_count += 1
        else:
            # 更新現有日期的價格（可能有修正）
            if existing_prices[date] != price:
                existing_prices[date] = price
    
    # 排序價格數據
    sorted_prices = dict(sorted(existing_prices.items()))
    
    # 更新數據結構
    updated_data = existing_data.copy()
    updated_data.update({
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_records': len(sorted_prices),
        'prices': sorted_prices
    })
    
    # 更新日期範圍
    if sorted_prices:
        updated_data['date_range'] = {
            'start': min(sorted_prices.keys()),
            'end': max(sorted_prices.keys())
        }
    
    return updated_data, new_count

def daily_update_all():
    """
    每日更新所有股票數據
    """
    ensure_data_directory()
    companies = load_companies()
    
    # 計算更新起始日期（最近7天，確保不遺漏週末數據）
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    success_count = 0
    total_count = len(companies)
    total_new_records = 0
    
    print(f"=== 每日增量更新開始 ===")
    print(f"更新日期範圍: {start_date} 至今")
    print(f"股票數量: {total_count}")
    print()
    
    for i, (symbol, company) in enumerate(companies.items(), 1):
        print(f"[{i}/{total_count}] 更新 {symbol} ({company.get('chinese_name', '')})")
        
        # 載入現有數據
        existing_data = load_existing_data(symbol)
        
        if existing_data is None:
            print(f"  ⚠️ 無現有數據，請先執行 init_data.py 進行初始化")
            continue
        
        # 獲取最新價格數據
        new_prices = get_latest_prices(symbol, start_date)
        
        if not new_prices:
            print(f"  ℹ️ 無新數據")
            continue
        
        # 更新數據
        updated_data, new_count = update_stock_data(symbol, existing_data, new_prices)
        
        # 保存更新後的數據
        file_path = f'stock_data/{symbol}.json'
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(updated_data, f, ensure_ascii=False, indent=2)
            
            if new_count > 0:
                print(f"  ✅ 新增 {new_count} 筆數據")
                total_new_records += new_count
            else:
                print(f"  ✅ 數據已是最新")
            
            success_count += 1
            
        except Exception as e:
            print(f"  ❌ 保存失敗: {e}")
        
        # 避免請求過於頻繁
        time.sleep(1)
    
    print()
    print(f"=== 每日更新完成 ===")
    print(f"處理股票: {success_count}/{total_count}")
    print(f"新增數據: {total_new_records} 筆")
    
    return success_count, total_count, total_new_records

def main():
    try:
        success, total, new_records = daily_update_all()
        
        if success == total:
            print("🎉 所有股票數據更新成功！")
        else:
            print(f"⚠️ 部分股票更新失敗，成功率: {success/total*100:.1f}%")
            
        if new_records > 0:
            print(f"📈 總共新增了 {new_records} 筆最新數據")
        else:
            print("📊 所有數據都已是最新狀態")
            
    except Exception as e:
        print(f"每日更新過程中發生錯誤: {str(e)}")

if __name__ == "__main__":
    main()