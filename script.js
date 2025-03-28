// 全域變數
let stockData = null;
let companiesData = {};
let performanceChart = null;
let selectedStock = null;

// 初始化
document.addEventListener('DOMContentLoaded', async () => {
    await loadCompaniesData();
    await initializeStockCards();
    initializeDateRange();
    setupSearchFilter();
    setupIndustryFilter();
    addSmoothScroll();
});

// 載入公司數據
async function loadCompaniesData() {
    try {
        const response = await fetch('companies.json');
        companiesData = await response.json();
        
        // 按照 JSON 順序顯示公司列表
        const stockList = document.getElementById('stockList');
        stockList.innerHTML = '';
        
        Object.entries(companiesData).forEach(([symbol, company]) => {
            const stockItem = document.createElement('div');
            stockItem.className = 'stock-item';
            stockItem.onclick = () => selectStock(symbol);
            
            stockItem.innerHTML = `
                <img src="icons/${symbol}.svg" onerror="this.src='default-icon.png'" alt="${company.chinese_name}">
                <div class="stock-info">
                    <div class="stock-name">${company.chinese_name}</div>
                    <div class="stock-symbol">${symbol}</div>
                </div>
            `;
            
            stockList.appendChild(stockItem);
        });
        
        // 預設顯示第一家公司
        const firstSymbol = Object.keys(companiesData)[0];
        if (firstSymbol) {
            selectStock(firstSymbol);
        }
    } catch (error) {
        console.error('載入公司數據時發生錯誤:', error);
    }
}

// 載入特定股票的數據
async function loadStockData(symbol) {
    try {
        const response = await fetch(`stock_data/${symbol}.json`);
        const data = await response.json();
        return data.prices;
    } catch (error) {
        console.error(`載入 ${symbol} 數據時發生錯誤:`, error);
        alert(`載入 ${symbol} 數據時發生錯誤，請稍後再試`);
        return null;
    }
}

// 設置產業篩選功能
function setupIndustryFilter() {
    const industryFilters = document.querySelector('.industry-filters');
    
    // 清空現有按鈕
    industryFilters.innerHTML = '';
    
    // 從公司資料中收集所有獨特的產業
    const industries = new Set();
    Object.values(companiesData).forEach(company => {
        if (company.industry) {
            industries.add(company.industry);
        }
    });
    
    // 將產業排序並創建按鈕
    const sortedIndustries = Array.from(industries).sort();
    
    // 添加"顯示全部"按鈕
    const allButton = document.createElement('button');
    allButton.className = 'industry-btn active';
    allButton.dataset.industry = 'all';
    allButton.textContent = '顯示全部';
    industryFilters.appendChild(allButton);
    
    // 添加各產業按鈕
    sortedIndustries.forEach(industry => {
        const button = document.createElement('button');
        button.className = 'industry-btn';
        button.dataset.industry = industry;
        button.textContent = industry;
        industryFilters.appendChild(button);
    });
    
    // 添加點擊事件
    const buttons = document.querySelectorAll('.industry-btn');
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            const industry = button.dataset.industry;
            filterByIndustry(industry);
            
            // 更新按鈕狀態
            buttons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
        });
    });
}

// 根據產業篩選股票
function filterByIndustry(industry) {
    const cards = document.querySelectorAll('.stock-card');
    cards.forEach(card => {
        const stockSymbol = card.querySelector('.stock-symbol').textContent;
        const company = companiesData[stockSymbol];
        
        if (industry === 'all' || company.industry === industry) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// 初始化股票卡片
async function initializeStockCards() {
    const stockGrid = document.getElementById('stockGrid');
    stockGrid.innerHTML = '';

    // 直接使用 Object.entries 保持原始順序
    Object.entries(companiesData).forEach(([symbol, company]) => {
        const card = document.createElement('div');
        card.className = 'stock-card';
        card.style.cursor = 'pointer';
        
        card.addEventListener('click', () => selectStock(symbol));

        // 移除"股份有限公司"
        let displayName = company.chinese_name.replace(/股份有限公司$/, '');

        card.innerHTML = `
            <h3>${displayName}</h3>
            <p class="stock-symbol">${symbol}</p>
            <p class="stock-sector">${company.sector} | ${company.industry}</p>
        `;

        stockGrid.appendChild(card);
    });
}

// 設置搜索過濾功能
function setupSearchFilter() {
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const cards = document.querySelectorAll('.stock-card');

        cards.forEach(card => {
            const symbol = card.querySelector('.stock-symbol').textContent.toLowerCase();
            const name = card.querySelector('h3').textContent.toLowerCase();
            const sector = card.querySelector('.stock-sector').textContent.toLowerCase();

            if (symbol.includes(searchTerm) || 
                name.includes(searchTerm) || 
                sector.includes(searchTerm)) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    });
}

// 初始化日期範圍
function initializeDateRange() {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setFullYear(endDate.getFullYear() - 5);

    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');

    // 設置最大日期為今天
    const today = new Date().toISOString().split('T')[0];
    endDateInput.max = today;
    
    // 設置預設值
    startDateInput.value = startDate.toISOString().split('T')[0];
    endDateInput.value = today;

    // 添加日期變更事件監聽器
    startDateInput.addEventListener('change', function() {
        // 確保結束日期不早於開始日期
        if (endDateInput.value < this.value) {
            endDateInput.value = this.value;
        }
    });

    endDateInput.addEventListener('change', function() {
        // 確保開始日期不晚於結束日期
        if (startDateInput.value > this.value) {
            startDateInput.value = this.value;
        }
    });
}

// 返回主頁面
function showMainPage() {
    document.getElementById('mainPage').style.display = 'block';
    document.getElementById('backtestPage').style.display = 'none';
    selectedStock = null;

    // 重置所有績效指標
    resetResults();
}

// 重置績效指標
function resetResults() {
    // 重置數值顯示
    document.getElementById('totalInvestment').textContent = '$0';
    document.getElementById('currentValue').textContent = '$0';
    document.getElementById('totalProfitLoss').textContent = '$0';
    document.getElementById('totalReturn').textContent = '0%';
    document.getElementById('annualReturn').textContent = '0%';
    document.getElementById('totalFees').textContent = '$0';

    // 移除所有正負值的類別
    const elements = ['totalProfitLoss', 'totalReturn', 'annualReturn'];
    elements.forEach(id => {
        const element = document.getElementById(id);
        element.classList.remove('price-up', 'price-down');
    });

    // 清除圖表
    if (window.myChart) {
        window.myChart.destroy();
        window.myChart = null;
    }

    // 隱藏結果區域
    document.getElementById('resultsSection').style.display = 'none';

    // 重置投資日期選擇
    document.querySelectorAll('input[name="investmentDay"]').forEach(checkbox => {
        checkbox.checked = false;
    });

    // 重置其他輸入欄位
    document.getElementById('monthlyInvestment').value = '1000';
    document.getElementById('feeRate').value = '0.1';
    document.getElementById('holidayHandling').value = 'next';
}

// 選擇股票
function selectStock(symbol) {
    try {
        selectedStock = symbol;
        const company = companiesData[symbol];

        if (!company) {
            console.error('找不到公司資料:', symbol);
            alert('找不到公司資料，請重新整理頁面後再試');
            return;
        }

        // 只檢查最基本必要的欄位
        const requiredFields = ['chinese_name', 'description', 'sector', 'industry'];
        const missingFields = requiredFields.filter(field => !company[field]);
        
        if (missingFields.length > 0) {
            console.error('公司資料缺少必要欄位:', symbol, missingFields);
            alert('公司資料不完整');
            return;
        }

        // 設置日期限制
        const startDateInput = document.getElementById('startDate');
        const endDateInput = document.getElementById('endDate');
        
        if (!startDateInput || !endDateInput) {
            console.error('找不到日期輸入欄位');
            alert('頁面元素缺失，請重新整理後再試');
            return;
        }

        // 設置最小日期為公司上市日期
        startDateInput.min = company.ipo_date;
        const currentStartDate = new Date(startDateInput.value);
        const ipoDate = new Date(company.ipo_date);
        
        // 如果目前選擇的日期早於上市日期，則設為上市日期
        if (currentStartDate < ipoDate) {
            startDateInput.value = company.ipo_date;
        }

        // 設置最大日期為今天
        const today = new Date().toISOString().split('T')[0];
        endDateInput.max = today;
        const currentEndDate = new Date(endDateInput.value);
        
        // 如果結束日期晚於今天，則設為今天
        if (currentEndDate > new Date(today)) {
            endDateInput.value = today;
        }

        // 更新回測頁面的公司信息
        const stockName = document.getElementById('selectedStockName');
        const stockDesc = document.getElementById('selectedStockDescription');

        if (!stockName || !stockDesc) {
            console.error('找不到公司資訊顯示元素');
            alert('頁面元素缺失，請重新整理後再試');
            return;
        }

        // 移除"股份有限公司"
        let displayName = company.chinese_name.replace(/股份有限公司$/, '');
        stockName.textContent = `${displayName} (${symbol})`;

        // 簡化公司資訊顯示
        let detailsHTML = `
            <p>${company.description}</p>
            <p>上市時間 ${company.ipo_date}</p>
            <p>總部 ${company.headquarters}</p>
            <div class="company-products">
                <h4>主要產品</h4>
                <p>${company.key_products ? company.key_products.join('、') : '無'}</p>
                <h4>主要服務</h4>
                <p>${company.key_services ? company.key_services.join('、') : '無'}</p>
            </div>
            <p><a href="https://tw.stock.yahoo.com/quote/${symbol}" target="_blank" class="yahoo-link">查看更多資訊</a></p>
        `;

        stockDesc.innerHTML = detailsHTML;

        // 重置結果區域
        resetResults();

        // 切換頁面顯示
        const mainPage = document.getElementById('mainPage');
        const backtestPage = document.getElementById('backtestPage');
        
        if (!mainPage || !backtestPage) {
            console.error('找不到頁面切換元素');
            alert('頁面元素缺失，請重新整理後再試');
            return;
        }

        mainPage.style.display = 'none';
        backtestPage.style.display = 'block';

    } catch (error) {
        console.error('選擇股票時發生錯誤:', error);
        alert('發生未預期的錯誤，請重新整理頁面後再試');
    }
}

// 計算投資組合表現
async function calculatePortfolioPerformance() {
    if (!selectedStock) {
        alert('請先選擇一支股票');
        return;
    }

    // 在手機版上，滾動到結果區域
    if (window.innerWidth <= 768) {
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            setTimeout(() => {
                resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 500); // 等待結果顯示後再滾動
        }
    }

    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const monthlyInvestment = parseFloat(document.getElementById('monthlyInvestment').value);
    const feeRate = parseFloat(document.getElementById('feeRate').value) / 100;
    const company = companiesData[selectedStock];
    
    // 檢查開始日期是否早於上市日期
    if (new Date(startDate) < new Date(company.ipo_date)) {
        alert(`此公司上市時間：${company.ipo_date}`);
        document.getElementById('startDate').value = company.ipo_date;
        return;
    }

    // 獲取選擇的投資日期
    const selectedDays = Array.from(document.querySelectorAll('input[name="investmentDay"]:checked'))
        .map(checkbox => parseInt(checkbox.value));

    if (selectedDays.length === 0) {
        alert('請至少選擇一個投資日期');
        return;
    }

    // 載入股票數據
    const priceData = await loadStockData(selectedStock);
    if (!priceData) return;

    // 過濾日期範圍內的數據並排序
    const tradingDays = Object.entries(priceData)
        .filter(([date]) => date >= startDate && date <= endDate)
        .sort(([dateA], [dateB]) => new Date(dateA) - new Date(dateB));

    // 計算每月投資結果
    let totalInvestment = 0;
    let totalShares = 0;
    let totalFees = 0;
    let monthlyResults = [];
    let currentMonth = '';
    let pendingDays = [];

    // 對每個交易日進行處理
    tradingDays.forEach(([date, price]) => {
        const currentDate = new Date(date);
        const dayOfMonth = currentDate.getDate();
        const month = date.substring(0, 7); // YYYY-MM

        // 檢查是否進入新月份
        if (month !== currentMonth) {
            currentMonth = month;
            pendingDays = [...selectedDays]; // 重置待處理投資日期
        }

        // 找出當天需要投資的日期（即選定日期在或早於當天且尚未投資）
        const investDays = pendingDays.filter(day => day <= dayOfMonth);

        if (investDays.length > 0) {
            let dailyInvestment = 0;
            let dailyShares = 0;
            let dailyFees = 0;

            // 為每個應投資的日期計算投資金額
            investDays.forEach(day => {
                const investment = monthlyInvestment / selectedDays.length;
                const fee = investment * feeRate;
                const actualInvestment = investment - fee;
                const shares = actualInvestment / price;

                dailyInvestment += investment;
                dailyFees += fee;
                dailyShares += shares;
            });

            // 更新總計
            totalInvestment += dailyInvestment;
            totalFees += dailyFees;
            totalShares += dailyShares;

            // 記錄當天結果
            monthlyResults.push({
                date,
                price,
                dailyInvestment,
                dailyShares,
                dailyFees,
                totalInvestment,
                totalFees,
                totalShares,
                currentValue: totalShares * price
            });

            // 從待處理清單中移除已投資的日期
            pendingDays = pendingDays.filter(day => !investDays.includes(day));
        }
    });

    // 計算報酬率和其他指標
    const lastResult = monthlyResults[monthlyResults.length - 1];
    const totalProfitLoss = lastResult.currentValue - lastResult.totalInvestment;
    const totalReturn = totalProfitLoss / lastResult.totalInvestment;
    const years = (new Date(endDate) - new Date(startDate)) / (1000 * 60 * 60 * 24 * 365);
    const annualReturn = Math.pow(1 + totalReturn, 1 / years) - 1;

    // 更新績效指標
    document.getElementById('totalInvestment').textContent = formatCurrency(lastResult.totalInvestment);
    document.getElementById('currentValue').textContent = formatCurrency(lastResult.currentValue);
    
    const totalProfitLossElement = document.getElementById('totalProfitLoss');
    totalProfitLossElement.textContent = formatCurrency(totalProfitLoss);
    totalProfitLossElement.className = totalProfitLoss >= 0 ? 'price-up' : 'price-down';
    
    const totalReturnElement = document.getElementById('totalReturn');
    totalReturnElement.textContent = formatPercentage(totalReturn);
    totalReturnElement.className = totalReturn >= 0 ? 'price-up' : 'price-down';
    
    const annualReturnElement = document.getElementById('annualReturn');
    annualReturnElement.textContent = formatPercentage(annualReturn);
    annualReturnElement.className = annualReturn >= 0 ? 'price-up' : 'price-down';
    
    document.getElementById('totalFees').textContent = formatCurrency(lastResult.totalFees);

    // 更新圖表
    updatePerformanceChart(monthlyResults);
}

// 更新績效圖表
function updatePerformanceChart(results) {
    const ctx = document.getElementById('performanceChart').getContext('2d');
    
    if (window.myChart) {
        window.myChart.destroy();
    }

    const dates = results.map(r => r.date);
    const investments = results.map(r => r.totalInvestment);
    const values = results.map(r => r.currentValue);
    const fees = results.map(r => r.totalFees);

    window.myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [
                {
                    label: '總投資金額',
                    data: investments,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                },
                {
                    label: '投資組合價值',
                    data: values,
                    borderColor: 'rgb(255, 99, 132)',
                    tension: 0.1
                },
                {
                    label: '累計手續費',
                    data: fees,
                    borderColor: 'rgb(255, 159, 64)',
                    tension: 0.1
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    ticks: {
                        color: '#ffffff' // X 軸標籤變白色
                    }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#ffffff', // Y 軸標籤變白色
                        callback: value => formatCurrency(value)
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#ffffff' // 圖例文字變白色
                    }
                },
                tooltip: {
                    callbacks: {
                        label: context => formatCurrency(context.raw)
                    }
                }
            }
        }
    });

    // 顯示結果區域
    document.getElementById('resultsSection').style.display = 'block';
}


// 格式化貨幣
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(value);
}

// 格式化百分比
function formatPercentage(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'percent',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
}

// 為計算按鈕添加點擊效果
document.getElementById('calculateBtn').addEventListener('click', function(e) {
    const btn = e.currentTarget;
    
    // 創建漣漪效果
    const ripple = document.createElement('span');
    ripple.classList.add('ripple');
    btn.appendChild(ripple);
    
    // 設置漣漪位置
    const rect = btn.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = e.clientX - rect.left - size/2 + 'px';
    ripple.style.top = e.clientY - rect.top - size/2 + 'px';
    
    // 移除漣漪元素
    ripple.addEventListener('animationend', () => {
        ripple.remove();
    });
    
    // 執行計算
    calculatePortfolioPerformance();
});

// 添加平滑滾動功能
document.addEventListener('DOMContentLoaded', function() {
    // 監聽所有按鈕點擊
    document.querySelectorAll('button').forEach(button => {
        button.addEventListener('click', function(e) {
            // 添加漣漪效果
            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            this.appendChild(ripple);
            
            // 設置漣漪位置
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = e.clientX - rect.left - size/2 + 'px';
            ripple.style.top = e.clientY - rect.top - size/2 + 'px';
            
            // 移除漣漪元素
            ripple.addEventListener('animationend', () => {
                ripple.remove();
            });
        });
    });

    // 監聽股票卡片懸停
    document.querySelectorAll('.stock-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}); 
