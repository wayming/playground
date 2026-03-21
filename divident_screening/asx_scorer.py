#!/usr/bin/env python3
"""
ASX Stock Scoring System - 12刀打分体系
生成带雷达图的HTML报告

这是一个 thin wrapper，调用各个行业 scorer 模块进行评分。
"""

import json
import argparse
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

# Import scoring modules
from scorers.banks import calculate_banks_score
from scorers.materials import calculate_materials_score
from scorers.infrastructure import calculate_infrastructure_score
from scorers.consumer import calculate_consumer_score

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ScoreResult:
    ticker: str
    industry: str
    total_score: float = 0
    max_score: float = 0
    details: List[Dict[str, Any]] = field(default_factory=list)
    passed_checks: List[str] = field(default_factory=list)
    failed_checks: List[str] = field(default_factory=list)
    debug_logs: List[str] = field(default_factory=list)

    def log(self, message: str):
        """添加调试日志"""
        self.debug_logs.append(f"[{self.ticker}] {message}")
        logger.debug(f"{self.ticker}: {message}")


class ScoringSystem:
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.ticker = data.get('ticker', '')

    def _prepare_data(self) -> Dict[str, Any]:
        """
        将原始数据整理为统一的格式供各个 scorer 使用。

        保持原始结构 (ratios/income_statement/balance_sheet/cash_flow)，
        让各个 scorer 的 get_value 函数能够正确提取数据。

        每个数据项优先使用 TTM 值，其次是 Current，最后是年度数据。
        """
        result = {'ticker': self.ticker}

        # 定义数据源 sections
        sections = ['ratios', 'income_statement', 'balance_sheet', 'cash_flow', 'extra']

        for section in sections:
            source = self.data.get(section, {})
            if not source:
                continue

            result[section] = {}
            for key, value in source.items():
                if isinstance(value, dict):
                    # 优先级: TTM > Current > FY 2025 > Annual Report
                    if 'TTM' in value:
                        result[section][key] = value['TTM']
                    elif 'Current' in value:
                        result[section][key] = value['Current']
                    elif 'FY 2025' in value:
                        result[section][key] = value['FY 2025']
                    elif 'Annual Report 2025' in value:
                        result[section][key] = value['Annual Report 2025']
                else:
                    result[section][key] = value

        return result

    def score_banks(self) -> ScoreResult:
        """银行评分 - 调用 banks scorer"""
        prepared_data = self._prepare_data()
        score_data = calculate_banks_score(prepared_data)

        return self._convert_to_score_result(score_data, "Banks")

    def score_materials(self) -> ScoreResult:
        """矿企评分 - 调用 materials scorer"""
        prepared_data = self._prepare_data()
        score_data = calculate_materials_score(prepared_data)

        return self._convert_to_score_result(score_data, "Materials")

    def score_infrastructure(self) -> ScoreResult:
        """基建评分 - 调用 infrastructure scorer"""
        prepared_data = self._prepare_data()
        score_data = calculate_infrastructure_score(prepared_data)

        return self._convert_to_score_result(score_data, "Infrastructure")

    def score_consumer_staples(self) -> ScoreResult:
        """必需消费评分 - 调用 consumer scorer"""
        prepared_data = self._prepare_data()
        score_data = calculate_consumer_score(prepared_data)

        return self._convert_to_score_result(score_data, "Consumer Staples")

    def _convert_to_score_result(self, score_data: Dict[str, Any], industry: str) -> ScoreResult:
        """
        将 scorer 返回的数据转换为 ScoreResult 格式。
        """
        result = ScoreResult(
            ticker=score_data.get('ticker', self.ticker),
            industry=industry,
            total_score=score_data.get('total_score', 0),
            max_score=score_data.get('max_score', 10)
        )

        # 转换 metrics 为 details 列表
        metrics = score_data.get('metrics', {})
        for metric_name, metric_data in metrics.items():
            weight = metric_data.get('weight', 0)

            # 跳过权重为 0 的指标 (如 LVR 惩罚项)
            if weight == 0 and metric_name != 'LVR':
                continue

            detail = {
                'metric': metric_name,
                'value': self._format_value(metric_data.get('value')),
                'score': metric_data.get('score', 0),
                'max': 10,
                'benchmark': metric_data.get('benchmark', ''),
                'description': metric_data.get('description', ''),
            }

            # 添加单位 (如果有)
            if 'unit' in metric_data:
                detail['unit'] = metric_data['unit']

            result.details.append(detail)

            # 根据级别判断是否通过
            level = metric_data.get('level', '')
            if level in ('excellent', 'good') or (isinstance(metric_data.get('score', 0), (int, float)) and metric_data.get('score', 0) >= 7):
                result.passed_checks.append(metric_name)

        # 检查 LVR 惩罚
        if score_data.get('lvr_penalty', False):
            result.log("LVR > 75%, 总分折半")

        return result

    def _format_value(self, value: Any) -> str:
        """格式化值为字符串"""
        if value is None:
            return "N/A"
        if isinstance(value, (int, float)):
            return f"{value:.2f}"
        return str(value)

    def score(self, industry: str) -> ScoreResult:
        """根据行业类型调用对应的评分函数"""
        industry = industry.lower()

        if 'bank' in industry or '金融' in industry:
            result = self.score_banks()
        elif 'material' in industry or 'mining' in industry or '矿' in industry:
            result = self.score_materials()
        elif 'infrastructure' in industry or 'infra' in industry or 'utilities' in industry or '基建' in industry or '公用' in industry:
            result = self.score_infrastructure()
        elif 'consumer' in industry or 'staples' in industry or '消费' in industry:
            result = self.score_consumer_staples()
        elif 'health' in industry or '医' in industry or 'pharma' in industry:
            # Healthcare 暂未实现，使用通用评分
            raise ValueError("Healthcare 行业暂未实现，请使用 banks/materials/infrastructure/consumer")
        elif 'tele' in industry or '通信' in industry:
            # Telecom 暂未实现，使用通用评分
            raise ValueError("Telecom 行业暂未实现，请使用 banks/materials/infrastructure/consumer")
        else:
            raise ValueError(f"未知行业: {industry}")

        logging.info(f"Completed industry-specific scoring for {self.ticker} in {industry}")
        return result


def generate_html_report(result: ScoreResult) -> str:
    """生成带雷达图的HTML报告"""

    # 准备雷达图数据
    indicators = []
    values = []
    for d in result.details:
        if not d.get('is_common', False):
            indicators.append({
                'name': d['metric'],
                'max': d['max']
            })
            values.append(round(d['score'], 1))

    # 如果指标不够6个，补充空值
    while len(indicators) < 6:
        indicators.append({'name': '', 'max': 10})
        values.append(0)

    # 添加通用指标
    common_values = []
    for d in result.details:
        if d.get('is_common', False):
            common_values.append(round(d['score'], 1))

    percentage = (result.total_score / result.max_score * 100) if result.max_score > 0 else 0

    if percentage >= 80:
        rating = "★★★★★ 优等生"
        rating_color = "#52c41a"
    elif percentage >= 60:
        rating = "★★★★☆ 良好"
        rating_color = "#1890ff"
    elif percentage >= 40:
        rating = "★★★☆☆ 合格"
        rating_color = "#faad14"
    else:
        rating = "★★☆☆☆ 不推荐"
        rating_color = "#ff4d4f"

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{result.ticker} - 12刀评分报告</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ text-align: center; color: #fff; margin-bottom: 30px; }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header .industry {{ color: #888; font-size: 1.2em; }}
        .score-card {{ background: rgba(255,255,255,0.1); border-radius: 20px; padding: 30px; margin-bottom: 30px; display: flex; align-items: center; justify-content: center; gap: 40px; }}
        .score-circle {{ width: 150px; height: 150px; border-radius: 50%; background: conic-gradient({rating_color} {percentage * 3.6}deg, rgba(255,255,255,0.1) 0deg); display: flex; align-items: center; justify-content: center; position: relative; }}
        .score-circle::before {{ content: ''; position: absolute; width: 120px; height: 120px; background: #1a1a2e; border-radius: 50%; }}
        .score-circle .score-text {{ position: relative; z-index: 1; text-align: center; color: #fff; }}
        .score-circle .score-text .big {{ font-size: 2.5em; font-weight: bold; }}
        .score-circle .score-text .label {{ font-size: 0.9em; color: #888; }}
        .rating {{ color: {rating_color}; font-size: 1.8em; font-weight: bold; }}
        .content {{ display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }}
        .chart-card {{ background: rgba(255,255,255,0.05); border-radius: 20px; padding: 20px; }}
        .chart-card h3 {{ color: #fff; margin-bottom: 15px; font-size: 1.2em; }}
        #radarChart {{ width: 100%; height: 400px; }}
        .checks {{ display: flex; gap: 20px; flex-wrap: wrap; }}
        .check-item {{ padding: 8px 16px; border-radius: 20px; font-size: 0.9em; }}
        .check-pass {{ background: rgba(82, 196, 26, 0.2); color: #52c41a; }}
        .check-fail {{ background: rgba(255, 77, 79, 0.2); color: #ff4d4f; }}
        .table-card {{ background: rgba(255,255,255,0.05); border-radius: 20px; padding: 20px; grid-column: 1 / -1; }}
        .table-card h3 {{ color: #fff; margin-bottom: 15px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }}
        th {{ color: #888; font-weight: normal; }}
        td {{ color: #fff; }}
        .score-bar {{ height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden; }}
        .score-bar-fill {{ height: 100%; background: linear-gradient(90deg, #1890ff, #52c41a); border-radius: 4px; }}
        @media (max-width: 768px) {{ .content {{ grid-template-columns: 1fr; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{result.ticker}</h1>
            <div class="industry">{result.industry}</div>
        </div>

        <div class="score-card">
            <div class="score-circle">
                <div class="score-text">
                    <div class="big">{percentage:.0f}%</div>
                    <div class="label">得分率</div>
                </div>
            </div>
            <div class="rating">{rating}</div>
            <div style="color: #fff; text-align: center;">
                <div style="font-size: 2em; font-weight: bold;">{result.total_score:.0f}</div>
                <div style="color: #888;">/ {result.max_score:.0f} 分</div>
            </div>
        </div>

        <div class="content">
            <div class="chart-card">
                <h3>六维能力图</h3>
                <div id="radarChart"></div>
            </div>

            <div class="chart-card">
                <h3>检查结果</h3>
                <div class="checks">
                    {''.join(f'<span class="check-item check-pass">+ {c}</span>' for c in result.passed_checks)}
                    {''.join(f'<span class="check-item check-fail">- {c}</span>' for c in result.failed_checks)}
                </div>
            </div>

            <div class="table-card">
                <h3>详细指标</h3>
                <table>
                    <thead>
                        <tr>
                            <th>指标</th>
                            <th>数值</th>
                            <th>基准</th>
                            <th>得分</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(f'''<tr>
                            <td>{d['metric']}</td>
                            <td>{d['value']} {d.get('unit', '')}</td>
                            <td>{d.get('benchmark', '')}</td>
                            <td style="width: 30%;">
                                <div class="score-bar"><div class="score-bar-fill" style="width: {d['score']/d['max']*100}%"></div></div>
                                <span>{d['score']:.1f}/{d['max']}</span>
                            </td>
                        </tr>''' for d in result.details)}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        var chart = echarts.init(document.getElementById('radarChart'));
        var option = {{
            backgroundColor: 'transparent',
            tooltip: {{}},
            radar: {{
                indicator: {json.dumps(indicators)},
                shape: 'polygon',
                splitNumber: 5,
                axisName: {{ color: '#fff', fontSize: 14 }},
                splitLine: {{ lineStyle: {{ color: 'rgba(255,255,255,0.1)' }} }},
                splitArea: {{ show: true, areaStyle: {{ color: ['rgba(255,255,255,0.02)', 'rgba(255,255,255,0.05)'] }} }},
                axisLine: {{ lineStyle: {{ color: 'rgba(255,255,255,0.2)' }} }}
            }},
            series: [{{
                name: 'Score',
                type: 'radar',
                data: [{{
                    value: {json.dumps(values)},
                    name: '行业指标',
                    areaStyle: {{ color: 'rgba(24, 144, 255, 0.3)' }},
                    lineStyle: {{ color: '#1890ff', width: 3 }},
                    itemStyle: {{ color: '#1890ff' }}
                }}]
            }}]
        }};
        chart.setOption(option);
        window.addEventListener('resize', function() {{ chart.resize(); }});
    </script>
</body>
</html>'''

    return html




def generate_comparison_html(results):
    """生成多股票对比 HTML 报告

    Args:
        results: List of ScoreResult for multiple stocks

    Returns:
        HTML string with comparison charts and tables
    """
    import json

    if not results:
        return "<html><body>No data to compare</body></html>"

    # Define colors for different stocks
    colors = ['#1890ff', '#52c41a', '#faad14', '#ff4d4f', '#722ed1', '#13c2c2']

    # Get all unique indicators from all results
    all_indicators = []
    for result in results:
        for d in result.details:
            if not d.get('is_common', False):
                metric_name = d['metric'].split('(')[0].strip()
                if metric_name not in [ind['name'] for ind in all_indicators]:
                    all_indicators.append({
                        'name': metric_name,
                        'max': d['max']
                    })

    # Pad to 6 indicators if needed
    while len(all_indicators) < 6:
        all_indicators.append({'name': '', 'max': 10})

    # Prepare radar chart data
    radar_datasets = []
    for i, result in enumerate(results):
        values = []
        result_metrics = {d['metric'].split('(')[0].strip(): d['score'] for d in result.details if not d.get('is_common', False)}
        for ind in all_indicators:
            values.append(round(result_metrics.get(ind['name'], 0), 1))

        radar_datasets.append({
            'ticker': result.ticker,
            'data': values,
            'color': colors[i % len(colors)]
        })

    # Generate radar datasets JavaScript
    radar_series = []
    for ds in radar_datasets:
        color = ds['color']
        radar_series.append('''{
            value: ''' + json.dumps(ds['data']) + ''',
            name: "''' + ds['ticker'] + '''",
            areaStyle: { color: "''' + color + '''30" },
            lineStyle: { color: "''' + color + '''", width: 2 },
            itemStyle: { color: "''' + color + '''" }
        }''')

    # Generate comparison table rows
    table_data = []
    for i, result in enumerate(results):
        percentage = (result.total_score / result.max_score * 100) if result.max_score > 0 else 0
        if percentage >= 80:
            rating = "★★★★★"
        elif percentage >= 60:
            rating = "★★★★☆"
        elif percentage >= 40:
            rating = "★★★☆☆"
        else:
            rating = "★★☆☆☆"

        table_data.append({
            'ticker': result.ticker,
            'industry': result.industry,
            'score': result.total_score,
            'max': result.max_score,
            'percentage': percentage,
            'rating': rating,
            'color': colors[i % len(colors)],
            'passed': ', '.join(result.passed_checks) if result.passed_checks else '-'
        })

    # Legend HTML
    legend_html = ''.join('<div class="legend-item"><div class="legend-dot" style="background: ' + colors[i % len(colors)] + '"></div><span>' + r.ticker + '</span></div>' for i, r in enumerate(results))

    # Table rows HTML
    table_rows = ''
    for row in table_data:
        table_rows += '''<tr>
            <td style="color: ''' + row['color'] + '''; font-weight: bold;">''' + row['ticker'] + '''</td>
            <td>''' + row['industry'] + '''</td>
            <td>
                <div class="score-bar"><div class="score-bar-fill" style="width: ''' + str(round(row['percentage'], 1)) + '''%; background: ''' + row['color'] + '''"></div></div>
                <span>''' + str(round(row['score'], 1)) + '/' + str(row['max']) + '''</span>
            </td>
            <td class="rating">''' + row['rating'] + '''</td>
            <td>''' + row['passed'] + '''</td>
        </tr>'''

    # X-axis data for bar chart
    bar_x_data = json.dumps([r.ticker for r in results])
    bar_data = json.dumps([{'value': round(r.total_score, 1), 'itemStyle': {'color': colors[i % len(colors)]}} for i, r in enumerate(results)])

    # Legend data for radar
    radar_legend = json.dumps([r.ticker for r in results])

    # Indicators for radar
    indicators_json = json.dumps(all_indicators)

    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>股票对比分析</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 1400px; margin: 0 auto; }
        .header { text-align: center; color: #fff; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .content { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }
        .chart-card { background: rgba(255,255,255,0.05); border-radius: 20px; padding: 20px; }
        .chart-card h3 { color: #fff; margin-bottom: 15px; font-size: 1.2em; }
        #radarChart { width: 100%; height: 450px; }
        #barChart { width: 100%; height: 350px; }
        .legend { display: flex; justify-content: center; gap: 20px; margin-bottom: 20px; flex-wrap: wrap; }
        .legend-item { display: flex; align-items: center; gap: 8px; color: #fff; }
        .legend-dot { width: 12px; height: 12px; border-radius: 50%; }
        .table-card { background: rgba(255,255,255,0.05); border-radius: 20px; padding: 20px; grid-column: 1 / -1; }
        .table-card h3 { color: #fff; margin-bottom: 15px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }
        th { color: #888; font-weight: normal; }
        td { color: #fff; }
        .score-bar { height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden; }
        .score-bar-fill { height: 100%; background: linear-gradient(90deg, #1890ff, #52c41a); border-radius: 4px; }
        .rating { color: #faad14; }
        @media (max-width: 768px) { .content { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>股票对比分析</h1>
            <p style="color: #888;">''' + str(len(results)) + ''' 只股票对比</p>
        </div>

        <div class="legend">
            ''' + legend_html + '''
        </div>

        <div class="content">
            <div class="chart-card">
                <h3>雷达图对比</h3>
                <div id="radarChart"></div>
            </div>

            <div class="chart-card">
                <h3>总分对比</h3>
                <div id="barChart"></div>
            </div>

            <div class="table-card">
                <h3>详细对比</h3>
                <table>
                    <thead>
                        <tr>
                            <th>股票</th>
                            <th>行业</th>
                            <th>评分</th>
                            <th>等级</th>
                            <th>通过检查</th>
                        </tr>
                    </thead>
                    <tbody>
                        ''' + table_rows + '''
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        // Radar Chart
        var radarChart = echarts.init(document.getElementById('radarChart'));
        var radarOption = {
            backgroundColor: 'transparent',
            tooltip: {},
            legend: {
                data: ''' + radar_legend + ''',
                bottom: 0,
                textStyle: { color: '#fff' }
            },
            radar: {
                indicator: ''' + indicators_json + ''',
                shape: 'polygon',
                splitNumber: 5,
                axisName: { color: '#fff', fontSize: 12 },
                splitLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
                splitArea: { show: true, areaStyle: { color: ['rgba(255,255,255,0.02)', 'rgba(255,255,255,0.05)'] } },
                axisLine: { lineStyle: { color: 'rgba(255,255,255,0.2)' } }
            },
            series: [{
                name: '对比',
                type: 'radar',
                data: [''' + ', '.join(radar_series) + ''']
            }]
        };
        radarChart.setOption(radarOption);

        // Bar Chart
        var barChart = echarts.init(document.getElementById('barChart'));
        var barOption = {
            backgroundColor: 'transparent',
            tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
            grid: { top: '10%', left: '3%', right: '4%', bottom: '10%', containLabel: true },
            xAxis: {
                type: 'category',
                data: ''' + bar_x_data + ''',
                axisLabel: { color: '#fff' },
                axisLine: { lineStyle: { color: 'rgba(255,255,255,0.2)' } }
            },
            yAxis: {
                type: 'value',
                max: 10,
                axisLabel: { color: '#fff' },
                axisLine: { lineStyle: { color: 'rgba(255,255,255,0.2)' } },
                splitLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } }
            },
            series: [{
                name: '得分',
                type: 'bar',
                data: ''' + bar_data + ''',
                barWidth: '50%',
                label: {
                    show: true,
                    position: 'top',
                    color: '#fff',
                    formatter: '{c}'
                }
            }]
        };
        barChart.setOption(barOption);

        window.addEventListener('resize', function() {
            radarChart.resize();
            barChart.resize();
        });
    </script>
</body>
</html>'''

    return html


def main():
    parser = argparse.ArgumentParser(description='ASX股票12刀打分系统')
    parser.add_argument('data_file', help='财务数据JSON文件')
    parser.add_argument('industry', help='行业类型: banks/materials/infrastructure/consumer')
    parser.add_argument('-o', '--output', help='输出HTML报告文件')

    args = parser.parse_args()

    with open(args.data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    scorer = ScoringSystem(data)
    result = scorer.score(args.industry)

    html = generate_html_report(result)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(html)
        logger.info(f"报告已生成: {args.output}")
    else:
        logger.info("HTML output:")
        logger.info(html)


if __name__ == '__main__':
    main()
