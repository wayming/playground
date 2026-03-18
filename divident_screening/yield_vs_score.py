"""
Yield vs Score - 性价比曲线模块

实现"质量-估值"二维对比系统:
- 横轴: 量化总分 (0-10 分)
- 纵轴: 股息率 (Dividend Yield) 或 Earning Yield (1/PE)

价值象限:
              高估值(贵)          低估值(便宜)
              PE>20              PE<15
    高质量   ┌──────────┐        ┌──────────┐
   (>6分)   │ 价值陷阱  │   ★    │ 优质低估 │
              └──────────┘        └──────────┘
    低质量   ┌──────────┐        ┌──────────┐
   (<4分)   │   垃圾   │        │ 价值风险 │
              └──────────┘        └──────────┘
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class StockData:
    """股票数据"""
    ticker: str
    score: float  # 0-10 分
    dividend_yield: Optional[float] = None  # 股息率 %
    pe: Optional[float] = None  # 市盈率
    industry: str = ""
    name: str = ""

    @property
    def earning_yield(self) -> Optional[float]:
        """计算 Earning Yield = 1/PE"""
        if self.pe and self.pe > 0:
            return (1 / self.pe) * 100
        return None

    @property
    def valuation_yield(self) -> Optional[float]:
        """获取估值收益率 (优先使用 Earning Yield，否则用 Dividend Yield)"""
        if self.earning_yield is not None:
            return self.earning_yield
        return self.dividend_yield


class Quadrant:
    """象限定义"""
    HIGH_QUALITY_HIGH_VALUATION = "价值陷阱"  # 高分 + 高估值 (贵)
    HIGH_QUALITY_LOW_VALUATION = "优质低估"  # 高分 + 低估值 (便宜) ★ 推荐
    LOW_QUALITY_HIGH_VALUATION = "垃圾"  # 低分 + 高估值 (贵)
    LOW_QUALITY_LOW_VALUATION = "价值风险"  # 低分 + 低估值 (便宜)


# 象限边界
SCORE_THRESHOLD_HIGH = 6.0  # 高质量阈值
SCORE_THRESHOLD_LOW = 4.0   # 低质量阈值
YIELD_THRESHOLD = 4.0       # 股息率/收益阈值 (%)


class YieldVsScore:
    """性价比曲线分析器"""

    def __init__(self):
        self.stocks: List[StockData] = []
        self.industries: Dict[str, List[str]] = {}  # industry -> [tickers]

    def add_stock(
        self,
        ticker: str,
        score: float,
        dividend_yield: Optional[float] = None,
        pe: Optional[float] = None,
        industry: str = "",
        name: str = ""
    ) -> None:
        """添加一只股票的数据"""
        stock = StockData(
            ticker=ticker,
            score=score,
            dividend_yield=dividend_yield,
            pe=pe,
            industry=industry,
            name=name or ticker
        )
        self.stocks.append(stock)

        # 更新行业索引
        if industry:
            if industry not in self.industries:
                self.industries[industry] = []
            if ticker not in self.industries[industry]:
                self.industries[industry].append(ticker)

    def add_industry(self, industry: str, stocks: List[Dict[str, Any]]) -> None:
        """添加一个行业的所有股票"""
        for stock_data in stocks:
            self.add_stock(
                ticker=stock_data.get('ticker', ''),
                score=stock_data.get('score', 0),
                dividend_yield=stock_data.get('dividend_yield'),
                pe=stock_data.get('pe'),
                industry=industry,
                name=stock_data.get('name', '')
            )

    def classify_quadrant(self, stock: StockData) -> str:
        """分类股票到象限"""
        yield_val = stock.valuation_yield

        # 无法分类
        if yield_val is None:
            return "未知"

        # 高质量 (score >= 6)
        if stock.score >= SCORE_THRESHOLD_HIGH:
            if yield_val >= YIELD_THRESHOLD:
                return Quadrant.HIGH_QUALITY_LOW_VALUATION  # 优质低估
            else:
                return Quadrant.HIGH_QUALITY_HIGH_VALUATION  # 价值陷阱

        # 低质量 (score <= 4)
        elif stock.score <= SCORE_THRESHOLD_LOW:
            if yield_val >= YIELD_THRESHOLD:
                return Quadrant.LOW_QUALITY_LOW_VALUATION  # 价值风险
            else:
                return Quadrant.LOW_QUALITY_HIGH_VALUATION  # 垃圾

        # 中间地带 (4 < score < 6)
        else:
            if yield_val >= YIELD_THRESHOLD:
                return "中性偏低估值"
            else:
                return "中性偏高估值"

    def get_recommendations(self) -> List[Dict[str, Any]]:
        """获取推荐: 右上象限(高质量+低估值)"""
        recommendations = []

        for stock in self.stocks:
            quadrant = self.classify_quadrant(stock)

            if quadrant == Quadrant.HIGH_QUALITY_LOW_VALUATION:
                recommendations.append({
                    'ticker': stock.ticker,
                    'name': stock.name,
                    'score': stock.score,
                    'dividend_yield': stock.dividend_yield,
                    'pe': stock.pe,
                    'earning_yield': stock.earning_yield,
                    'industry': stock.industry,
                    'quadrant': quadrant,
                    'reason': '高质量 + 低估值'
                })

        # 按分数排序
        recommendations.sort(key=lambda x: x['score'], reverse=True)

        return recommendations

    def get_all_by_quadrant(self) -> Dict[str, List[Dict[str, Any]]]:
        """获取所有象限的股票"""
        result = {
            Quadrant.HIGH_QUALITY_LOW_VALUATION: [],
            Quadrant.HIGH_QUALITY_HIGH_VALUATION: [],
            Quadrant.LOW_QUALITY_LOW_VALUATION: [],
            Quadrant.LOW_QUALITY_HIGH_VALUATION: [],
            "中性偏低估值": [],
            "中性偏高估值": [],
            "未知": []
        }

        for stock in self.stocks:
            quadrant = self.classify_quadrant(stock)
            stock_info = {
                'ticker': stock.ticker,
                'name': stock.name,
                'score': stock.score,
                'dividend_yield': stock.dividend_yield,
                'pe': stock.pe,
                'earning_yield': stock.earning_yield,
                'valuation_yield': stock.valuation_yield,
                'industry': stock.industry
            }
            result[quadrant].append(stock_info)

        return result

    def generate_scatter_html(self, output_path: Optional[str] = None) -> str:
        """生成散点图 HTML 报告"""
        # 准备数据
        datasets = []
        colors = {
            Quadrant.HIGH_QUALITY_LOW_VALUATION: '#52c41a',  # 绿色 - 推荐
            Quadrant.HIGH_QUALITY_HIGH_VALUATION: '#faad14',  # 黄色 - 价值陷阱
            Quadrant.LOW_QUALITY_LOW_VALUATION: '#ff4d4f',  # 红色 - 风险
            Quadrant.LOW_QUALITY_HIGH_VALUATION: '#999999',  # 灰色 - 垃圾
            "中性偏低估值": '#1890ff',  # 蓝色
            "中性偏高估值": '#722ed1',  # 紫色
            "未知": '#666666'
        }

        # 按行业分组
        industry_colors = [
            '#1890ff', '#52c41a', '#faad14', '#ff4d4f',
            '#722ed1', '#13c2c2', '#eb2f96', '#fa8c16'
        ]

        industry_color_map = {}
        color_idx = 0

        for stock in self.stocks:
            industry = stock.industry or "Unknown"
            if industry not in industry_color_map:
                industry_color_map[industry] = industry_colors[color_idx % len(industry_colors)]
                color_idx += 1

        # 为每个行业创建数据集
        for industry, tickers in self.industries.items():
            data = []
            for ticker in tickers:
                for stock in self.stocks:
                    if stock.ticker == ticker:
                        yield_val = stock.valuation_yield
                        if yield_val is not None:
                            data.append({
                                'name': stock.ticker,
                                'value': [round(stock.score, 2), round(yield_val, 2)]
                            })
                        break

            if data:
                datasets.append({
                    'name': industry,
                    'type': 'scatter',
                    'symbolSize': 20,
                    'data': data,
                    'label': {
                        'show': True,
                        'formatter': '{b}',
                        'position': 'right'
                    }
                })

        # 如果没有行业数据，创建默认数据集
        if not datasets:
            data = []
            for stock in self.stocks:
                yield_val = stock.valuation_yield
                if yield_val is not None:
                    data.append({
                        'name': stock.ticker,
                        'value': [round(stock.score, 2), round(yield_val, 2)]
                    })

            if data:
                datasets.append({
                    'name': 'Stocks',
                    'type': 'scatter',
                    'symbolSize': 20,
                    'data': data,
                    'label': {
                        'show': True,
                        'formatter': '{b}',
                        'position': 'right'
                    }
                })

        # 象限背景区域
        mark_areas = [
            # 右上 - 优质低估 (推荐)
            {
                'name': '优质低估',
                'itemStyle': {'color': 'rgba(82, 196, 26, 0.1)'},
                'coord': [[SCORE_THRESHOLD_HIGH, YIELD_THRESHOLD], [10, 15]]
            },
            # 左上 - 价值陷阱
            {
                'name': '价值陷阱',
                'itemStyle': {'color:': 'rgba(250, 173, 20, 0.1)'},
                'coord': [[0, YIELD_THRESHOLD], [SCORE_THRESHOLD_HIGH, 15]]
            },
            # 右下 - 价值风险
            {
                'name': '价值风险',
                'itemStyle': {'color': 'rgba(255, 77, 79, 0.1)'},
                'coord': [[SCORE_THRESHOLD_LOW, 0], [10, YIELD_THRESHOLD]]
            },
            # 左下 - 垃圾
            {
                'name': '垃圾',
                'itemStyle': {'color': 'rgba(153, 153, 153, 0.1)'},
                'coord': [[0, 0], [SCORE_THRESHOLD_LOW, YIELD_THRESHOLD]]
            }
        ]

        recommendations = self.get_recommendations()
        quadrant_data = self.get_all_by_quadrant()

        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>性价比曲线 - Yield vs Score</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; padding: 20px; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{ text-align: center; color: #fff; margin-bottom: 30px; }}
        .header h1 {{ font-size: 2em; margin-bottom: 10px; }}
        .header .subtitle {{ color: #888; font-size: 1em; }}
        .chart-container {{ background: rgba(255,255,255,0.05); border-radius: 20px; padding: 20px; margin-bottom: 30px; }}
        #scatterChart {{ width: 100%; height: 500px; }}
        .recommendations {{ background: rgba(255,255,255,0.05); border-radius: 20px; padding: 20px; }}
        .recommendations h2 {{ color: #52c41a; margin-bottom: 20px; font-size: 1.5em; }}
        .rec-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px; }}
        .rec-card {{ background: rgba(82, 196, 26, 0.1); border: 1px solid rgba(82, 196, 26, 0.3); border-radius: 12px; padding: 15px; }}
        .rec-card h3 {{ color: #fff; margin-bottom: 10px; }}
        .rec-card .score {{ color: #52c41a; font-size: 1.5em; font-weight: bold; }}
        .rec-card .yield {{ color: #faad14; }}
        .rec-card .industry {{ color: #888; font-size: 0.9em; }}
        .quadrant-summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 30px; }}
        .quadrant-card {{ background: rgba(255,255,255,0.05); border-radius: 12px; padding: 15px; }}
        .quadrant-card h4 {{ margin-bottom: 10px; }}
        .quadrant-card.recommended h4 {{ color: #52c41a; }}
        .quadrant-card.trap h4 {{ color: #faad14; }}
        .quadrant-card.risky h4 {{ color: #ff4d4f; }}
        .quadrant-card.garbage h4 {{ color: #999; }}
        .quadrant-card .count {{ font-size: 2em; font-weight: bold; color: #fff; }}
        .legend {{ display: flex; gap: 20px; justify-content: center; margin-bottom: 20px; flex-wrap: wrap; }}
        .legend-item {{ display: flex; align-items: center; gap: 8px; color: #fff; }}
        .legend-color {{ width: 16px; height: 16px; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>性价比曲线</h1>
            <div class="subtitle">质量 (Score) vs 估值 (Yield)</div>
        </div>

        <div class="legend">
            <div class="legend-item">
                <div class="legend-color" style="background: #52c41a;"></div>
                <span>优质低估 ★</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #faad14;"></div>
                <span>价值陷阱</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #ff4d4f;"></div>
                <span>价值风险</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #999;"></div>
                <span>垃圾</span>
            </div>
        </div>

        <div class="chart-container">
            <div id="scatterChart"></div>
        </div>

        <div class="recommendations">
            <h2>★ 推荐股票 (优质低估)</h2>
            <div class="rec-grid">
                {''.join(f'''
                <div class="rec-card">
                    <h3>{r['ticker']}</h3>
                    <div class="industry">{r['industry']}</div>
                    <div class="score">Score: {r['score']:.1f}</div>
                    <div class="yield">
                        {'Dividend: ' + str(round(r['dividend_yield'], 2)) + '%' if r['dividend_yield'] else 'PE: ' + str(round(r['pe'], 1)) + 'x'}
                    </div>
                </div>
                ''' for r in recommendations) if recommendations else '<p style="color:#888;">暂无推荐</p>'}
            </div>
        </div>

        <div class="quadrant-summary">
            <div class="quadrant-card recommended">
                <h4>★ 优质低估</h4>
                <div class="count">{len(quadrant_data.get(Quadrant.HIGH_QUALITY_LOW_VALUATION, []))}</div>
                <div style="color:#888">高质量 + 低估值</div>
            </div>
            <div class="quadrant-card trap">
                <h4>价值陷阱</h4>
                <div class="count">{len(quadrant_data.get(Quadrant.HIGH_QUALITY_HIGH_VALUATION, []))}</div>
                <div style="color:#888">高质量 + 高估值</div>
            </div>
            <div class="quadrant-card risky">
                <h4>价值风险</h4>
                <div class="count">{len(quadrant_data.get(Quadrant.LOW_QUALITY_LOW_VALUATION, []))}</div>
                <div style="color:#888">低质量 + 低估值</div>
            </div>
            <div class="quadrant-card garbage">
                <h4>垃圾</h4>
                <div class="count">{len(quadrant_data.get(Quadrant.LOW_QUALITY_HIGH_VALUATION, []))}</div>
                <div style="color:#888">低质量 + 高估值</div>
            </div>
        </div>
    </div>

    <script>
        var chart = echarts.init(document.getElementById('scatterChart'));
        var option = {{
            backgroundColor: 'transparent',
            tooltip: {{
                trigger: 'item',
                formatter: function(params) {{
                    return params.name + '<br/>Score: ' + params.value[0] + '<br/>Yield: ' + params.value[1] + '%';
                }}
            }},
            grid: {{
                left: '10%',
                right: '10%',
                top: '10%',
                bottom: '10%'
            }},
            xAxis: {{
                name: '质量分数 (Score)',
                nameLocation: 'middle',
                nameGap: 30,
                type: 'value',
                min: 0,
                max: 10,
                splitLine: {{
                    lineStyle: {{ color: 'rgba(255,255,255,0.1)' }}
                }},
                axisLine: {{ lineStyle: {{ color: 'rgba(255,255,255,0.3)' }} }},
                axisLabel: {{ color: '#fff' }},
                nameTextStyle: {{ color: '#fff', fontSize: 14 }}
            }},
            yAxis: {{
                name: '估值收益率 (%)',
                nameLocation: 'middle',
                nameGap: 50,
                type: 'value',
                min: 0,
                max: 15,
                splitLine: {{
                    lineStyle: {{ color: 'rgba(255,255,255,0.1)' }}
                }},
                axisLine: {{ lineStyle: {{ color: 'rgba(255,255,255,0.3)' }} }},
                axisLabel: {{ color: '#fff' }},
                nameTextStyle: {{ color: '#fff', fontSize: 14 }}
            }},
            series: {json.dumps(datasets)} + [
                {{
                    type: 'line',
                    data: [[{SCORE_THRESHOLD_HIGH}, 0], [{SCORE_THRESHOLD_HIGH}, 15]],
                    lineStyle: {{ color: 'rgba(255,255,255,0.3)', type: 'dashed' }},
                    symbol: 'none'
                }},
                {{
                    type: 'line',
                    data: [[0, {YIELD_THRESHOLD}], [10, {YIELD_THRESHOLD}]],
                    lineStyle: {{ color: 'rgba(255,255,255,0.3)', type: 'dashed' }},
                    symbol: 'none'
                }}
            ]
        }};
        chart.setOption(option);
        window.addEventListener('resize', function() {{ chart.resize(); }});
    </script>
</body>
</html>'''

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"报告已生成: {output_path}")

        return html


# ==================== 测试入口 ====================

if __name__ == '__main__':
    print("=== 性价比曲线测试 ===")

    # 创建分析器
    analyzer = YieldVsScore()

    # 添加测试数据
    analyzer.add_stock("CBA", score=8.5, dividend_yield=5.2, industry="Banks")
    analyzer.add_stock("NAB", score=6.5, dividend_yield=6.1, industry="Banks")
    analyzer.add_stock("WBC", score=5.5, dividend_yield=4.5, industry="Banks")
    analyzer.add_stock("ANZ", score=5.0, dividend_yield=5.8, industry="Banks")

    analyzer.add_stock("WES", score=7.5, dividend_yield=4.2, industry="Consumer")
    analyzer.add_stock("WOW", score=6.2, dividend_yield=3.5, industry="Consumer")
    analyzer.add_stock("COL", score=3.5, dividend_yield=5.5, industry="Consumer")

    analyzer.add_stock("BHP", score=7.0, dividend_yield=8.5, pe=12, industry="Materials")
    analyzer.add_stock("RIO", score=7.2, dividend_yield=7.8, pe=14, industry="Materials")
    analyzer.add_stock("FMG", score=5.5, dividend_yield=10.2, pe=8, industry="Materials")

    # 测试象限分类
    print("\n象限分类:")
    for stock in analyzer.stocks:
        q = analyzer.classify_quadrant(stock)
        print(f"  {stock.ticker}: score={stock.score}, yield={stock.valuation_yield} -> {q}")

    # 测试推荐
    print("\n推荐股票:")
    recommendations = analyzer.get_recommendations()
    for rec in recommendations:
        print(f"  {rec['ticker']}: score={rec['score']}, {rec['reason']}")

    # 生成 HTML
    print("\n生成 HTML 报告...")
    html = analyzer.generate_scatter_html("yield_vs_score_report.html")
    print("完成!")
