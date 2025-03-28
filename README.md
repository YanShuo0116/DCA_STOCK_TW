# 台股定期定額投資回測工具

這是一個幫助投資者分析台股定期定額投資策略的網頁工具。透過這個工具，您可以模擬並分析在不同時期、不同金額下的定期定額投資結果。

## 功能特點

- 支援台灣上市櫃股票回測分析
- 自訂投資起始日期、金額與頻率
- 分析投資報酬率與風險指標
- 數據每日自動更新（使用 GitHub Actions）
- 使用 Yahoo Finance 作為數據來源
- 支援手續費設定與計算

## 使用方法

1. 訪問網站：[https://yanshuo0116.github.io/DCA_STOCK_TW/](https://yanshuo0116.github.io/DCA_STOCK_TW/)
2. 從列表中選擇想要分析的股票
3. 設定投資參數：
   - 投資起始日期
   - 每月投資金額
   - 投資日期（可多選）
   - 手續費率
4. 查看分析結果：
   - 總投資金額
   - 現值
   - 總報酬率
   - 年化報酬率
   - 手續費支出
   - 損益金額

## 技術實現

- 前端：HTML, CSS (Bootstrap), JavaScript
- 數據更新：Python (yfinance, pandas, requests, beautifulsoup4)
- 自動化部署：GitHub Actions（每個工作日晚上9點自動更新數據）
- 託管：GitHub Pages

## 本地開發

1. 克隆專案：
```bash
git clone https://github.com/YanShuo0116/DCA_STOCK_TW.git
```

2. 安裝依賴：
```bash
pip install pandas yfinance requests beautifulsoup4
```

3. 更新數據：
```bash
python update_data.py
```

## 資料來源

- 股票數據來源：Yahoo Finance
- 股票列表來源：臺灣證券交易所、證券櫃檯買賣中心

## 授權

MIT License 
