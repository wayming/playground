const stockColors = [
    'rgba(0, 212, 170, 0.7)',
    'rgba(255, 107, 107, 0.7)',
    'rgba(255, 195, 0, 0.7)',
    'rgba(155, 89, 182, 0.7)',
    'rgba(243, 156, 18, 0.7)',
    'rgba(52, 152, 219, 0.7)',
];

function getStockColor(idx) {
    return stockColors[idx % stockColors.length].replace('0.7', '1');
}

function getStockColorAlpha(idx, alpha = '0.7') {
    return stockColors[idx % stockColors.length].replace('0.7', alpha);
}

const industryMetrics = {
    'banks': [
        { key: 'NIM', name: '净息差', altKeys: ['净息差'], benchmark: [1.5, 1.8], polarity: 'higher', good: 1.8, bad: 1.5 },
        { key: 'CET1', name: '资本充足率', altKeys: ['CET1', '资本充足率'], benchmark: [11.5, 12.5], polarity: 'higher', good: 12.5, bad: 11.5 },
        { key: 'Cost-to-Income', name: '成本收入比', altKeys: ['成本收入比'], benchmark: [47, 55], polarity: 'lower', good: 43, bad: 55 },
        { key: 'ROE', name: '净资产收益率', altKeys: ['ROE', '净资产收益率'], benchmark: [11, 12], polarity: 'higher', good: 12, bad: 11 },
        { key: 'Bad Debt', name: '不良贷款率', altKeys: ['Bad Debt', 'Credit Risk', '不良贷款率'], benchmark: [0.1, 0.15], polarity: 'lower', good: 0.1, bad: 0.15 },
        { key: 'Payout', name: '股息支付率', altKeys: ['Payout', '股息支付率'], benchmark: [70, 80], polarity: 'range', goodMin: 70, goodMax: 80 },
        { key: 'LVR', name: '贷款价值比', altKeys: ['LVR', 'Group Average LVR', '贷款价值比'], benchmark: [50, 75], polarity: 'lower', good: 50, bad: 75 }
    ],
    'materials': [
        { key: 'Operating Cost', name: '运营成本率', altKeys: ['Operating Cost', '运营成本率'], benchmark: [1.0, 1.5], polarity: 'higher', good: 1.5, bad: 1.0 },
        { key: 'Production', name: '产量增长', altKeys: ['Production', 'Revenue Growth', '产量增长'], benchmark: [0, 5], polarity: 'higher', good: 5, bad: 0 },
        { key: 'Underlying NPAT', name: '核心净利润', altKeys: ['Underlying NPAT', '核心净利润'], benchmark: [0, 10000], polarity: 'higher', good: 10000, bad: 0 },
        { key: 'FCF Yield', name: '现金流收益率', altKeys: ['FCF Yield', '现金流收益率'], benchmark: [8, 15], polarity: 'higher', good: 15, bad: 8 },
        { key: 'Net Debt/EBITDA', name: '净杠杆率', altKeys: ['Net Debt/EBITDA', '净杠杆率'], benchmark: [0.5, 1.0], polarity: 'lower', good: 0.5, bad: 1.0 },
        { key: 'Dividend Policy', name: '分红政策', altKeys: ['Dividend Policy', '分红政策'], benchmark: [50, 70], polarity: 'higher', good: 70, bad: 50 }
    ],
    'infrastructure': [
        { key: 'EBITDA Margin', name: '运营利润率', altKeys: ['EBITDA Margin', '运营利润率'], benchmark: [55, 70], polarity: 'higher', good: 70, bad: 55 },
        { key: 'Cash Conv', name: '现金转化率', altKeys: ['Cash Conv', '现金转化率'], benchmark: [95, 100], polarity: 'higher', good: 100, bad: 95 },
        { key: 'Interest Cover', name: '利息覆盖', altKeys: ['Interest Cover', '利息覆盖率'], benchmark: [3, 5], polarity: 'higher', good: 5, bad: 3 },
        { key: 'EV/EBITDA', name: '企业价值倍数', altKeys: ['EV/EBITDA', '企业价值倍数'], benchmark: [12, 15], polarity: 'range', goodMin: 12, goodMax: 15 },
        { key: 'Debt/Equity', name: '债务权益比', altKeys: ['Debt/Equity', '债务权益比'], benchmark: [1.5, 2.0], polarity: 'lower', good: 1.5, bad: 2.0 },
        { key: 'Current Ratio', name: '流动比率', altKeys: ['Current Ratio', '流动比率'], benchmark: [1.5, 2.0], polarity: 'higher', good: 2.0, bad: 1.5 }
    ],
    'healthcare': [
        { key: 'EBITDA Margin', name: '运营利润率', altKeys: ['EBITDA Margin', '运营利润率'], benchmark: [25, 35], polarity: 'higher', good: 35, bad: 25 },
        { key: 'ROE', name: '净资产收益率', altKeys: ['ROE', '净资产收益率'], benchmark: [15, 20], polarity: 'higher', good: 20, bad: 15 },
        { key: 'FCF Yield', name: '现金流收益率', altKeys: ['FCF Yield', '现金流收益率'], benchmark: [2, 5], polarity: 'higher', good: 5, bad: 2 },
        { key: 'Net Debt/EBITDA', name: '净杠杆率', altKeys: ['Net Debt/EBITDA', '净杠杆率'], benchmark: [2.0, 2.5], polarity: 'lower', good: 2.0, bad: 2.5 },
        { key: 'Dividend Policy', name: '分红政策', altKeys: ['Dividend Policy', '分红政策'], benchmark: [40, 70], polarity: 'range', goodMin: 40, goodMax: 70 },
        { key: 'EV/EBITDA', name: '企业价值倍数', altKeys: ['EV/EBITDA', '企业价值倍数'], benchmark: [10, 20], polarity: 'range', goodMin: 10, goodMax: 20 }
    ],
    'telecom': [
        { key: 'EBITDA Margin', name: '运营利润率', altKeys: ['EBITDA Margin', '运营利润率'], benchmark: [35, 45], polarity: 'higher', good: 45, bad: 35 },
        { key: 'FCF Yield', name: '现金流收益率', altKeys: ['FCF Yield', '现金流收益率'], benchmark: [5, 10], polarity: 'higher', good: 10, bad: 5 },
        { key: 'Net Debt/EBITDA', name: '净杠杆率', altKeys: ['Net Debt/EBITDA', '净杠杆率'], benchmark: [2.0, 2.5], polarity: 'lower', good: 2.0, bad: 2.5 },
        { key: 'Dividend Policy', name: '分红政策', altKeys: ['Dividend Policy', '分红政策'], benchmark: [60, 90], polarity: 'range', goodMin: 60, goodMax: 90 },
        { key: 'EV/EBITDA', name: '企业价值倍数', altKeys: ['EV/EBITDA', '企业价值倍数'], benchmark: [6, 10], polarity: 'range', goodMin: 6, goodMax: 10 },
        { key: 'Current Ratio', name: '流动比率', altKeys: ['Current Ratio', '流动比率'], benchmark: [0.8, 1.2], polarity: 'higher', good: 1.2, bad: 0.8 }
    ],
    'consumer': [
        { key: 'EBIT Margin', name: '息税前利润率', altKeys: ['EBIT Margin', '息税前利润率'], benchmark: [4.5, 6], polarity: 'range', goodMin: 4.5, goodMax: 6 },
        { key: 'ROE', name: '净资产收益率', altKeys: ['ROE', '净资产收益率'], benchmark: [25, 35], polarity: 'higher', good: 35, bad: 25 },
        { key: 'Inventory Days', name: '库存周转天数', altKeys: ['Inventory Days', '库存周转天数'], benchmark: [30, 60], polarity: 'lower', good: 30, bad: 60 },
        { key: 'Forward PE', name: '远期市盈率', altKeys: ['Forward PE', '远期市盈率'], benchmark: [20, 24], polarity: 'range', goodMin: 20, goodMax: 24 },
        { key: 'Dividend Yield', name: '股息收益率', altKeys: ['Dividend Yield', '股息收益率'], benchmark: [4, 6], polarity: 'higher', good: 6, bad: 4 },
        { key: 'Payout', name: '股息支付率', altKeys: ['Payout', '股息支付率'], benchmark: [60, 80], polarity: 'range', goodMin: 60, goodMax: 80 }
    ]
};

let currentIndustry = 'banks';
let portfolioChart = null;
let selectedStocks = new Set();

async function showPeers() {
    console.log('showPeers called');
    const modal = document.getElementById('portfolioModal');
    modal.style.display = 'flex';

    document.getElementById('portfolioStats').innerHTML = '<p>Loading...</p>';

    try {
        const response = await fetch('/api/history');
        console.log('Response status:', response.status);
        if (!response.ok) throw new Error('Network error');
        const stocks = await response.json();
        console.log('Stocks:', stocks);

        if (!stocks || stocks.length === 0) {
            document.getElementById('portfolioStats').innerHTML = '<p>No stocks analyzed yet. Analyze some stocks first!</p>';
            return;
        }

        const industryGroups = {};
        stocks.forEach(s => {
            const ind = s.industry || 'materials';
            console.log('Stock:', s.symbol, 'Industry:', ind);
            if (!industryGroups[ind]) industryGroups[ind] = [];
            industryGroups[ind].push(s);
        });
        console.log('Industry groups:', industryGroups);

        const industryLabel = {
            'banks': 'Banks',
            'materials': 'Materials',
            'infrastructure': 'Infrastructure',
            'healthcare': 'Healthcare',
            'telecom': 'Telecom',
            'consumer_staples': 'Consumer'
        };

        const tabsContainer = document.getElementById('industryTabs');
        const industries = Object.keys(industryGroups);

        if (industries.length === 0) {
            document.getElementById('portfolioStats').innerHTML = '<p>No stocks analyzed yet</p>';
            return;
        }

        tabsContainer.innerHTML = industries.map((ind, idx) =>
            `<div class="industry-tab ${idx === 0 ? 'active' : ''}" data-industry="${ind}">${industryLabel[ind] || ind}</div>`
        ).join('');

        selectedStocks = new Set(stocks.map(s => s.symbol));

        const filterHtml = `
            <div class="stock-filter">
                <span class="filter-label">显示:</span>
                <button class="filter-btn active" onclick="toggleAllStocks(true)">全部</button>
                <button class="filter-btn" onclick="toggleAllStocks(false)">清除</button>
                ${stocks.map((s, idx) => `
                    <label class="stock-checkbox" style="color: ${getStockColor(idx)}">
                        <input type="checkbox" ${selectedStocks.has(s.symbol) ? 'checked' : ''} onchange="toggleStock('${s.symbol}', this.checked)">
                        ${s.symbol}
                    </label>
                `).join('')}
            </div>
        `;
        document.getElementById('stockFilter').innerHTML = filterHtml;

        tabsContainer.querySelectorAll('.industry-tab').forEach(tab => {
            tab.addEventListener('click', function() {
                tabsContainer.querySelectorAll('.industry-tab').forEach(t => t.classList.remove('active'));
                this.classList.add('active');
                const targetIndustry = this.dataset.industry;
                if (industryGroups[targetIndustry]) {
                    renderRadarChart(industryGroups[targetIndustry], targetIndustry);
                    renderStockList(industryGroups[targetIndustry], targetIndustry);
                }
            });
        });

        const firstIndustry = industries[0];
        if (industryGroups[firstIndustry]) {
            renderRadarChart(industryGroups[firstIndustry], firstIndustry);
            renderStockList(industryGroups[firstIndustry], firstIndustry);
        }

    } catch (error) {
        console.error('Error loading peers:', error);
        document.getElementById('portfolioStats').innerHTML = '<p>加载数据出错</p>';
    }
}

function toggleStock(symbol, checked) {
    if (checked) {
        selectedStocks.add(symbol);
    } else {
        selectedStocks.delete(symbol);
    }
    renderCurrentIndustryRadar();
}

function toggleAllStocks(selectAll) {
    const activeTab = document.querySelector('.industry-tab.active');
    const industry = activeTab?.dataset?.industry || currentIndustry;
    const stocks = _cachedIndustryGroups?.[industry];

    if (stocks) {
        stocks.forEach(s => {
            if (selectAll) {
                selectedStocks.add(s.symbol);
            } else {
                selectedStocks.delete(s.symbol);
            }
        });
        document.querySelectorAll('.stock-checkbox input').forEach(cb => {
            cb.checked = selectAll;
        });
        document.querySelectorAll('.filter-btn').forEach((btn, idx) => {
            btn.classList.toggle('active', idx === (selectAll ? 0 : 1));
        });
        renderRadarChart(stocks, industry);
    }
}

function renderCurrentIndustryRadar() {
    const activeTab = document.querySelector('.industry-tab.active');
    const industry = activeTab?.dataset?.industry || currentIndustry;
    const stocks = _cachedIndustryGroups?.[industry];
    if (stocks) {
        renderRadarChart(stocks, industry);
    }
}

let _cachedIndustryGroups = null;

function renderRadarChart(stocks, industry) {
    currentIndustry = industry;
    _cachedIndustryGroups = _cachedIndustryGroups || {};
    _cachedIndustryGroups[industry] = stocks;

    const metrics = industryMetrics[industry] || industryMetrics['banks'];

    const selectedStockList = stocks.filter(s => selectedStocks.has(s.symbol));

    const getScoreValue = (details, metricDef) => {
        const keys = [metricDef.key, ...(metricDef.altKeys || [])];
        const found = details.find(d => {
            const metricName = d.metric || '';
            return keys.some(k =>
                metricName === k ||
                metricName.toLowerCase() === k.toLowerCase() ||
                metricName.toLowerCase().includes(k.toLowerCase())
            );
        });
        if (!found) {
            console.log('Not found for', metricDef.key, 'keys:', keys, 'available:', details.map(d => d.metric));
            return 0;
        }
        let val = found.value;
        if (typeof val === 'string') {
            val = parseFloat(val.replace(/[$,%M]/g, ''));
        }
        return val || 0;
    };

    const getScoreFromDetails = (details, metricDef) => {
        const keys = [metricDef.key, ...(metricDef.altKeys || [])];
        const found = details.find(d => {
            const metricName = d.metric || '';
            return keys.some(k =>
                metricName === k ||
                metricName.toLowerCase() === k.toLowerCase() ||
                metricName.toLowerCase().includes(k.toLowerCase())
            );
        });
        if (!found) return null;
        return found.score || 0;
    };

    const datasets = selectedStockList.map((stock, idx) => {
        const values = metrics.map(m => {
            const score = getScoreFromDetails(stock.details, m);
            return score !== null ? score : 0;
        });

        return {
            label: stock.symbol,
            data: values,
            backgroundColor: getStockColorAlpha(idx, '0.2'),
            borderColor: getStockColor(idx),
            borderWidth: 2,
            pointBackgroundColor: getStockColor(idx),
            pointBorderColor: '#fff',
            pointRadius: 4
        };
    });

    const ctx = document.getElementById('portfolioRadarChart').getContext('2d');
    if (portfolioChart) portfolioChart.destroy();

    portfolioChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: metrics.map(m => m.name),
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 10,
                    ticks: {
                        stepSize: 2,
                        color: '#888',
                        backdropColor: 'transparent'
                    },
                    grid: { color: '#333' },
                    angleLines: { color: '#333' },
                    pointLabels: {
                        color: '#ccc',
                        font: { size: 11 }
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#fff', padding: 20 }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const stock = selectedStockList[context.datasetIndex];
                            const metric = metrics[context.dataIndex];
                            const rawVal = getScoreValue(stock.details, metric);
                            return `${stock.symbol} - ${metric.name}: ${rawVal}`;
                        }
                    }
                }
            },
            onClick: (e, elements) => {
                if (elements.length > 0) {
                    const stock = selectedStockList[elements[0].datasetIndex];
                    document.getElementById('symbolInput').value = stock.symbol;
                    closePortfolio();
                    analyzeStock();
                }
            }
        }
    });
}

function renderStockList(stocks, industry) {
    const container = document.getElementById('portfolioStats');
    const metrics = industryMetrics[industry] || industryMetrics['banks'];

    stocks.sort((a, b) => (b.score?.total || 0) - (a.score?.total || 0));

    let html = `
        <div class="comp-table-container">
            <table class="comp-table">
                <thead>
                    <tr>
                        <th>股票</th>
                        <th>总分</th>
                        ${metrics.map(m => `<th>${m.name}</th>`).join('')}
                    </tr>
                </thead>
                <tbody>
    `;

    stocks.forEach((stock, idx) => {
        const getVal = (details, metricDef) => {
            const keys = [metricDef.key, ...(metricDef.altKeys || [])];
            const found = details.find(d => {
                const n = d.metric || '';
                return keys.some(k =>
                    n === k ||
                    n.toLowerCase() === k.toLowerCase() ||
                    n.toLowerCase().includes(k.toLowerCase())
                );
            });
            return found ? found.value : '-';
        };

        const getDesc = (details, metricDef) => {
            const keys = [metricDef.key, ...(metricDef.altKeys || [])];
            const found = details.find(d => {
                const n = d.metric || '';
                return keys.some(k =>
                    n === k ||
                    n.toLowerCase() === k.toLowerCase() ||
                    n.toLowerCase().includes(k.toLowerCase())
                );
            });
            return found?.description || '';
        };

        const color = getStockColor(idx);

        html += `
            <tr style="cursor: pointer;" onclick="document.getElementById('symbolInput').value='${stock.symbol}';closePortfolio();analyzeStock();">
                <td style="color: ${color}; font-weight: bold;">${stock.symbol}</td>
                <td>${stock.score?.total || 0}</td>
                ${metrics.map(m => {
                    const val = getVal(stock.details, m);
                    const desc = getDesc(stock.details, m);
                    return `<td title="${desc}">${val}</td>`;
                }).join('')}
            </tr>
        `;
    });

    html += '</tbody></table></div>';
    container.innerHTML = html;
}

function closePortfolio() {
    document.getElementById('portfolioModal').style.display = 'none';
    if (portfolioChart) {
        portfolioChart.destroy();
        portfolioChart = null;
    }
}

function selectStock(symbol) {
    document.getElementById('symbolInput').value = symbol;
    closePortfolio();
    analyzeStock();
}

window.onclick = function(event) {
    const modal = document.getElementById('portfolioModal');
    if (event.target == modal) closePortfolio();
}

/* ========== Main App ========== */

document.addEventListener('DOMContentLoaded', () => {
    loadHistory();

    document.getElementById('symbolInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') analyzeStock();
    });
});

async function analyzeStock() {
    const symbol = document.getElementById('symbolInput').value.trim().toUpperCase();
    const btn = document.getElementById('analyzeBtn');

    if (!symbol) {
        showError('Please enter a stock symbol');
        return;
    }

    btn.disabled = true;
    btn.classList.add('loading');
    btn.textContent = 'Analyzing';
    hideError();
    document.getElementById('resultsSection').classList.remove('visible');

    const requestBody = { symbol };

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Analysis failed');
        }

        displayResults(data);
        loadHistory();
    } catch (error) {
        showError(error.message);
    } finally {
        btn.disabled = false;
        btn.classList.remove('loading');
        btn.textContent = 'Analyze';
    }
}

function displayResults(data) {
    console.log('displayResults received:', data);
    document.getElementById('resultsSection').classList.add('visible');
    document.getElementById('symbolDisplay').textContent = data.symbol;

    const score = data.score.total;
    const max = data.score.max;
    const percentage = (score / max) * 100;

    const scoreCircle = document.getElementById('scoreCircle');
    const scoreNumber = document.getElementById('scoreNumber');
    const scoreLabel = document.getElementById('scoreLabel');
    const scoreMax = document.getElementById('scoreMax');

    scoreNumber.textContent = score;
    scoreMax.textContent = `/ ${max}`;

    const circumference = 2 * Math.PI * 80;
    const offset = circumference - (score / max) * circumference;
    setTimeout(() => {
        scoreCircle.style.strokeDashoffset = offset;
    }, 100);

    let colorClass = 'low';
    let label = 'Needs Review';
    if (percentage >= 70) {
        colorClass = 'high';
        label = 'Strong Buy';
    } else if (percentage >= 50) {
        colorClass = 'medium';
        label = 'Hold';
    }

    scoreCircle.className = `score-circle-fill ${colorClass}`;
    scoreNumber.className = `score-number ${colorClass}`;
    scoreLabel.className = `score-label ${colorClass}`;
    scoreLabel.textContent = label;

    updateRadarChart(data.details);

    const metricsGrid = document.getElementById('metricsGrid');
    metricsGrid.innerHTML = data.details.map(d => {
        const pct = (d.score / d.max) * 100;
        let barClass = 'low';
        if (pct >= 70) barClass = 'high';
        else if (pct >= 40) barClass = 'medium';

        return `
            <div class="metric-item" title="${d.description || ''}">
                <div class="metric-name">${d.metric}</div>
                <div class="metric-value">${d.value !== null ? d.value : 'N/A'}</div>
                <div class="metric-bar">
                    <div class="metric-bar-fill ${barClass}" style="width: ${pct}%"></div>
                </div>
            </div>
        `;
    }).join('');

    const checksList = document.getElementById('checksList');
    checksList.innerHTML = '';

    data.passed_checks.forEach(check => {
        checksList.innerHTML += `
            <div class="check-item passed">
                <span class="check-icon">✓</span>
                <span>${check}</span>
            </div>
        `;
    });

    data.failed_checks.forEach(check => {
        checksList.innerHTML += `
            <div class="check-item failed">
                <span class="check-icon">✗</span>
                <span>${check}</span>
            </div>
        `;
    });

    if (data.passed_checks.length === 0 && data.failed_checks.length === 0) {
        checksList.innerHTML = '<div class="check-item">No checks available</div>';
    }
}

let radarChart = null;

function updateRadarChart(details) {
    const ctx = document.getElementById('radarChart').getContext('2d');

    const labels = details.map(d => d.metric);
    const scores = details.map(d => (d.score / d.max) * 100);

    if (radarChart) {
        radarChart.destroy();
    }

    radarChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Score',
                data: scores,
                backgroundColor: 'rgba(0, 212, 170, 0.2)',
                borderColor: 'rgba(0, 212, 170, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(0, 212, 170, 1)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20,
                        color: '#555566',
                        backdropColor: 'transparent',
                        font: {
                            family: "'JetBrains Mono', monospace",
                            size: 10
                        }
                    },
                    grid: {
                        color: '#2a2a3a'
                    },
                    angleLines: {
                        color: '#2a2a3a'
                    },
                    pointLabels: {
                        color: '#8888a0',
                        font: {
                            family: "'Outfit', sans-serif",
                            size: 11,
                            weight: 500
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            },
            animation: {
                duration: 1500,
                easing: 'easeOutQuart'
            }
        }
    });
}

async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        const history = await response.json();

        const historyGrid = document.getElementById('historyGrid');

        if (history.length === 0) {
            historyGrid.innerHTML = '<p style="color: var(--text-muted); grid-column: 1/-1; text-align: center;">No analyses yet</p>';
            return;
        }

        const grouped = {};
        history.forEach(h => {
            if (!grouped[h.symbol]) {
                grouped[h.symbol] = h;
            }
        });

        historyGrid.innerHTML = Object.values(grouped).slice(0, 8).map(h => `
            <div class="history-item" onclick="loadFromHistory('${h.symbol}')">
                <div class="history-symbol">${h.symbol}</div>
                <div class="history-date">${h.timestamp.substring(0, 8)}</div>
            </div>
        `).join('');
    } catch (e) {
        console.error('Failed to load history:', e);
    }
}

function loadFromHistory(symbol) {
    document.getElementById('symbolInput').value = symbol;
    analyzeStock();
}

function showError(message) {
    const errorEl = document.getElementById('errorMessage');
    errorEl.textContent = message;
    errorEl.style.display = 'block';
}

function hideError() {
    document.getElementById('errorMessage').style.display = 'none';
}
