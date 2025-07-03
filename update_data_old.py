import yfinance as yf
import pandas as pd
import json
from datetime import datetime, timedelta
import time
import os

# 從 companies.json 讀取股票列表
def load_companies():
    with open('companies.json', 'r', encoding='utf-8') as f:
        companies = json.load(f)
    return companies

def ensure_data_directory():
    """確保數據目錄存在"""
    if not os.path.exists('stock_data'):
        os.makedirs('stock_data')

def fetch_stock_data():
    """獲取股票數據並分別存儲"""
    ensure_data_directory()
    companies = load_companies()
    
    for symbol, company in companies.items():
        try:
            print(f"正在獲取 {symbol} 的數據...")
            
            # 為台股添加.TW後綴
            ticker_symbol = f"{symbol}.TW"
            
            # 獲取股票數據
            stock = yf.Ticker(ticker_symbol)
            
            # 從上市日期開始獲取數據
            ipo_date = company.get('ipo_date')
            if not ipo_date:
                print(f"警告：{symbol} 缺少上市日期，跳過")
                continue
            
            # 嘗試多種日期範圍策略
            df = None
            strategies = [
                # 策略1: 從上市日期開始
                {'start': ipo_date, 'period': None},
                # 策略2: 最近10年
                {'start': None, 'period': '10y'},
                # 策略3: 最近5年
                {'start': None, 'period': '5y'},
                # 策略4: 最近2年
                {'start': None, 'period': '2y'},
                # 策略5: 最近1年
                {'start': None, 'period': '1y'}
            ]
            
            for i, strategy in enumerate(strategies):
                try:
                    if strategy['start']:
                        df = stock.history(start=strategy['start'])
                    else:
                        df = stock.history(period=strategy['period'])
                    
                    if not df.empty:
                        print(f"  策略 {i+1} 成功: 獲取到 {len(df)} 筆數據")
                        break
                    else:
                        print(f"  策略 {i+1} 失敗: 數據為空")
                        
                except Exception as strategy_error:
                    print(f"  策略 {i+1} 失敗: {str(strategy_error)}")
                    continue
            
            # 如果所有策略都失敗，跳過這支股票
            if df is None or df.empty:
                print(f"❌ {symbol}: 所有策略都失敗，跳過")
                continue
            
            # 只保留收盤價
            prices = df['Close'].to_dict()
            
            # 將日期轉換為 ISO 格式字串
            formatted_prices = {
                date.strftime('%Y-%m-%d'): round(float(price), 2)  # 四捨五入到小數點後兩位
                for date, price in prices.items()
            }
            
            # 創建包含更多信息的數據結構
            stock_data = {
                'symbol': symbol,
                'ipo_date': ipo_date,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'prices': formatted_prices
            }
            
            # 將數據寫入獨立的 JSON 文件
            file_path = f'stock_data/{symbol}.json'
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(stock_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ {symbol}: 成功獲取並保存 {len(formatted_prices)} 筆數據")
            
            # 避免請求過於頻繁
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ {symbol}: 獲取數據時發生錯誤: {str(e)}")

def main():
    try:
        # 獲取並保存股票數據
        fetch_stock_data()
        print("數據更新完成")
    except Exception as e:
        print(f"更新數據時發生錯誤: {str(e)}")

if __name__ == "__main__":
    main() 