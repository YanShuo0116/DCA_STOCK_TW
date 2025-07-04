#!/usr/bin/env python3
"""
新的股票數據更新腳本 - 使用多種穩定數據源
不依賴 yfinance，使用台灣證券交易所官方 API 和其他穩定源
"""

import requests
import json
import pandas as pd
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

def get_twse_data(stock_id, year_month):
    """
    從台灣證券交易所獲取股票數據
    API: https://www.twse.com.tw/exchangeReport/STOCK_DAY
    """
    url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY"
    params = {
        'response': 'json',
        'date': year_month,  # 格式: YYYYMM01
        'stockNo': stock_id
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'data' in data and data['data']:
                # 解析數據格式
                # data['data'] 是一個列表，每個元素包含 [日期, 成交股數, 成交金額, 開盤價, 最高價, 最低價, 收盤價, 漲跌價差, 成交筆數]
                prices = {}
                
                for row in data['data']:
                    if len(row) >= 7:
                        date_str = row[0].replace('/', '-')  # 轉換日期格式
                        # 處理民國年轉西元年
                        if len(date_str.split('-')[0]) == 3:  # 民國年
                            year_parts = date_str.split('-')
                            year_parts[0] = str(int(year_parts[0]) + 1911)
                            date_str = '-'.join(year_parts)
                        
                        close_price = row[6].replace(',', '')  # 移除千分位逗號
                        
                        try:
                            prices[date_str] = round(float(close_price), 2)
                        except ValueError:
                            continue  # 跳過無效數據
                
                return prices
            else:
                print(f"  TWSE API 無數據: {data.get('stat', 'Unknown')}")
                return {}
        else:
            print(f"  TWSE API 請求失敗: {response.status_code}")
            return {}
            
    except Exception as e:
        print(f"  TWSE API 錯誤: {e}")
        return {}

def get_yahoo_data(symbol):
    """
    從 Yahoo Finance 獲取股票數據（備用方案）
    """
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}.TW"
        
        # 獲取最近2年的數據
        end_time = int(datetime.now().timestamp())
        start_time = int((datetime.now() - timedelta(days=730)).timestamp())
        
        params = {
            'period1': start_time,
            'period2': end_time,
            'interval': '1d'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'chart' in data and data['chart']['result']:
                result = data['chart']['result'][0]
                timestamps = result['timestamp']
                closes = result['indicators']['quote'][0]['close']
                
                prices = {}
                for i, timestamp in enumerate(timestamps):
                    if closes[i] is not None:
                        date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
                        prices[date_str] = round(float(closes[i]), 2)
                
                return prices
            else:
                return {}
        else:
            return {}
            
    except Exception as e:
        print(f"  Yahoo API 錯誤: {e}")
        return {}

def fetch_stock_data_new():
    """
    使用新的數據源獲取股票數據
    """
    ensure_data_directory()
    companies = load_companies()
    
    success_count = 0
    total_count = len(companies)
    
    for i, (symbol, company) in enumerate(companies.items(), 1):
        print(f"[{i}/{total_count}] 正在獲取 {symbol} ({company.get('chinese_name', '')}) 的數據...")
        
        ipo_date = company.get('ipo_date')
        if not ipo_date:
            print(f"  ❌ 缺少上市日期，跳過")
            continue
        
        all_prices = {}
        
        # 策略1: 使用 TWSE API 獲取歷史數據
        try:
            ipo_year = int(ipo_date.split('-')[0])
            current_year = datetime.now().year
            
            # 從上市年份開始，逐月獲取數據（移除5年限制）
            for year in range(ipo_year, current_year + 1):  # 獲取完整歷史數據
                for month in range(1, 13):
                    if year == current_year and month > datetime.now().month:
                        break
                        
                    year_month = f"{year}{month:02d}01"
                    monthly_prices = get_twse_data(symbol, year_month)
                    
                    if monthly_prices:
                        all_prices.update(monthly_prices)
                        print(f"  ✅ {year}-{month:02d}: {len(monthly_prices)} 筆數據")
                    
                    time.sleep(1)  # 避免請求過於頻繁
                    
                    # 如果已經有足夠數據，可以提早結束
                    if len(all_prices) > 1000:
                        break
                
                if len(all_prices) > 1000:
                    break
                    
        except Exception as e:
            print(f"  ⚠️ TWSE 獲取失敗: {e}")
        
        # 策略2: 如果 TWSE 數據不足，使用 Yahoo 作為備用
        if len(all_prices) < 50:
            print(f"  🔄 TWSE 數據不足 ({len(all_prices)} 筆)，嘗試 Yahoo API...")
            yahoo_prices = get_yahoo_data(symbol)
            
            if yahoo_prices:
                all_prices.update(yahoo_prices)
                print(f"  ✅ Yahoo: 新增 {len(yahoo_prices)} 筆數據")
        
        # 如果還是沒有數據，跳過
        if not all_prices:
            print(f"  ❌ 所有數據源都失敗，跳過")
            continue
        
        # 排序並保存數據
        sorted_prices = dict(sorted(all_prices.items()))
        
        stock_data = {
            'symbol': symbol,
            'ipo_date': ipo_date,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'prices': sorted_prices
        }
        
        # 保存到文件
        file_path = f'stock_data/{symbol}.json'
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(stock_data, f, ensure_ascii=False, indent=2)
            
            print(f"  ✅ 成功保存 {len(sorted_prices)} 筆數據")
            success_count += 1
            
        except Exception as e:
            print(f"  ❌ 保存失敗: {e}")
        
        # 避免請求過於頻繁
        time.sleep(2)
    
    print(f"\n=== 更新完成 ===")
    print(f"成功: {success_count}/{total_count} 個股票")

def main():
    try:
        print("=== 使用新數據源更新股票數據 ===")
        print("數據源: 台灣證券交易所 API + Yahoo Finance 備用")
        
        fetch_stock_data_new()
        print("數據更新完成")
        
    except Exception as e:
        print(f"更新數據時發生錯誤: {str(e)}")

if __name__ == "__main__":
    main()