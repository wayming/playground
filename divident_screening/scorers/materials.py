"""
Materials Scorecard - 矿业基本面打分系统

根据 docs/score_material.md 实现矿业七维度量化评分:
1. AISC (全维持成本率): < 60% 为目标，> 85% 为预警
2. Reserves Life (储量寿命): > 20年为目标
3. Capex Intensity (资本支出强度): > 15% 为目标
4. Underlying ROE (核心收益率): > 25% 为目标
5. FCF Yield (自由现金流收益率): > 8% 为目标
6. Net Debt/EBITDA (净杠杆率): < 0.5x 为目标
7. Payout Ratio (分红率): 50%-70% 为目标
"""

from typing import Dict, Any, Optional, Tuple


# ==================== 评分函数 ====================

def score_aisc(aisc: Optional[float]) -> Tuple[float, str]:
    """
    AISC (全维持成本率) 评分

    判定逻辑:
        10分: < 60% (全球成本最低的前25%，如RIO铁矿)
        7分: 60% - 75% (行业平均水平)
        4分: 75% - 85% (高成本边际矿)
        0分: > 85% (极度危险，周期下行必死)

    Returns:
        (score, level): 分数和评级
    """
    if aisc is None:
        return 0.0, "N/A"

    if aisc < 60:
        return 10.0, "excellent"
    elif aisc <= 75:
        return 7.0, "good"
    elif aisc <= 85:
        return 4.0, "fair"
    else:
        return 0.0, "poor"


def score_reserves_life(life: Optional[float]) -> Tuple[float, str]:
    """
    Reserves Life (储量寿命) 评分

    判定逻辑:
        10分: > 20年 (如RIO皮尔巴拉铁矿，几乎无穷无尽)
        7分: 12 - 20年 (稳健，有充足时间寻找新矿)
        4分: 7 - 12年 (中规中矩，必须加大勘探投入)
        0分: < 5年 (面临枯竭，资产减值风险极大)

    Returns:
        (score, level): 分数和评级
    """
    if life is None:
        return 0.0, "N/A"

    if life > 20:
        return 10.0, "excellent"
    elif life >= 12:
        return 7.0, "good"
    elif life >= 7:
        return 4.0, "fair"
    else:
        return 0.0, "poor"


def score_capex_intensity(ci: Optional[float]) -> Tuple[float, str]:
    """
    Capex Intensity (资本支出强度) 评分

    判定逻辑:
        10分: > 15% (扩张周期，RIO 19.9% 属于此类)
        7分: 8% - 15% (常规更新与温和扩张)
        4分: 3% - 8% (仅维持现状)
        0分: < 3% (吃老本，产能即将萎缩)

    Returns:
        (score, level): 分数和评级
    """
    if ci is None:
        return 0.0, "N/A"

    if ci > 15:
        return 10.0, "excellent"
    elif ci >= 8:
        return 7.0, "good"
    elif ci >= 3:
        return 4.0, "fair"
    else:
        return 0.0, "poor"


def score_underlying_roe(roe: Optional[float]) -> Tuple[float, str]:
    """
    Underlying ROE (核心收益率) 评分

    判定逻辑:
        10分: > 25% (顶级矿商，资源与管理双优)
        7分: 15% - 25% (矿业优等生)
        4分: 8% - 15% (平庸)
        0分: < 5% (资本浪费)

    Returns:
        (score, level): 分数和评级
    """
    if roe is None:
        return 0.0, "N/A"

    if roe > 25:
        return 10.0, "excellent"
    elif roe >= 15:
        return 7.0, "good"
    elif roe >= 8:
        return 4.0, "fair"
    else:
        return 0.0, "poor"


def score_fcf_yield(fcf_yield: Optional[float]) -> Tuple[float, str]:
    """
    FCF Yield (自由现金流收益率) 评分

    判定逻辑:
        10分: > 10% (疯狂印钞机)
        7分: 6% - 10% (成熟稳健，合理区间)
        4分: 2% - 5% (建设期/投入期，RIO 2.18% 处于此区间)
        0分: < 0 (烧钱模式)

    Returns:
        (score, level): 分数和评级
    """
    if fcf_yield is None:
        return 0.0, "N/A"

    if fcf_yield > 10:
        return 10.0, "excellent"
    elif fcf_yield >= 6:
        return 7.0, "good"
    elif fcf_yield >= 2:
        return 4.0, "fair"
    else:
        return 0.0, "poor"


def score_leverage(leverage: Optional[float]) -> Tuple[float, str]:
    """
    Net Debt/EBITDA (净杠杆率) 评分

    判定逻辑:
        10分: < 0.5x (财务极度自由)
        7分: 0.5x - 1.2x (安全，RIO 0.71x 属于此列)
        3分: 1.5x - 2.5x (杠杆偏高，注意周期拐点)
        0分: > 3.0x (危险边缘)

    Returns:
        (score, level): 分数和评级
    """
    if leverage is None:
        return 0.0, "N/A"

    if leverage < 0.5:
        return 10.0, "excellent"
    elif leverage <= 1.2:
        return 7.0, "good"
    elif leverage <= 2.5:
        return 3.0, "fair"
    else:
        return 0.0, "poor"


def score_payout(payout: Optional[float]) -> Tuple[float, str]:
    """
    Payout Ratio (分红率) 评分

    判定逻辑:
        10分: 50% - 70% (健康的现金奶牛)
        7分: 40% - 50% (平衡增长与回报)
        4分: < 30% (铁公鸡)
        0分: > 100% (入不敷出，借钱分红，极度危险)

    Returns:
        (score, level): 分数和评级
    """
    if payout is None:
        return 0.0, "N/A"

    if 50 <= payout <= 70:
        return 10.0, "excellent"
    elif 40 <= payout < 50:
        return 7.0, "good"
    elif payout < 30:
        return 4.0, "fair"
    else:
        return 0.0, "poor"


# ==================== 权重配置 ====================

# 评分权重 (根据 score_material.md)
WEIGHTS = {
    'AISC': 0.20,
    'Reserves Life': 0.20,
    'Capex Intensity': 0.15,
    'Underlying ROE': 0.15,
    'FCF Yield': 0.10,
    'Leverage': 0.10,
    'Payout': 0.10
}


# ==================== 数据提取工具 ====================

def get_value(data: Dict[str, Any], *keys: str) -> Optional[float]:
    """
    从数据字典中提取值

    优先级: TTM > Current > FY 2025 > Annual Report 2025

    Args:
        data: 包含财务数据的字典 (ratios/income_statement/balance_sheet/cash_flow)
        *keys: 要查找的键名

    Returns:
        找到的值 (float) 或 None
    """
    # 定义优先级
    periods = ['TTM', 'Current', 'FY 2025', 'Annual Report 2025', 'FY 2024']

    for key in keys:
        for section in ['ratios', 'income_statement', 'balance_sheet', 'cash_flow']:
            if section in data:
                section_data = data[section]
                if key in section_data:
                    val = section_data[key]
                    if isinstance(val, (int, float)):
                        return float(val)
                    elif isinstance(val, dict):
                        for period in periods:
                            if period in val:
                                return float(val[period])
    return None


# ==================== 主评分函数 ====================

def calculate_materials_score(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    计算矿业综合评分

    根据 docs/score_material.md 的公式:
    Total Score = (AISC * 0.2) + (Life * 0.2) + (Capex * 0.15) + (ROE * 0.15) + (FCF * 0.1) + (Leverage * 0.1) + (Payout * 0.1)

    Args:
        data: 包含财务数据的字典

    Returns:
        包含各项分数和总分的字典
    """
    # ===== 提取数据 =====
    # AISC 相关
    revenue = get_value(data, 'Revenue', 'Total Revenue')
    cost_revenue = get_value(data, 'Cost of Revenue', 'Cost of Goods Sold')
    capex = get_value(data, 'Capital Expenditures', 'CapEx', 'Sustaining Capex')

    # 计算 AISC
    aisc = None
    if revenue and cost_revenue and revenue > 0:
        total_cost = cost_revenue + abs(capex) if capex else cost_revenue
        aisc = (total_cost / revenue) * 100

    # Reserves Life 相关
    reserves = get_value(data, 'Total Proved Reserves', 'Reserves')
    production = get_value(data, 'Annual Production Volume', 'Production Volume')

    reserves_life = None
    if reserves and production and production > 0:
        reserves_life = reserves / production

    # Capex Intensity 相关
    cip = get_value(data, 'Construction in Progress', 'CIP')
    ppe = get_value(data, 'Total PPE', 'Property Plant and Equipment')

    capex_intensity = None
    if cip and ppe and ppe > 0:
        capex_intensity = (cip / ppe) * 100

    # Underlying ROE 相关
    net_income = get_value(data, 'Net Income', 'Net Income to Common')
    asset_writedown = get_value(data, 'Asset Writedown', 'Impairment of Assets')
    equity = get_value(data, 'Total Common Equity', 'Shareholders Equity')

    underlying_roe = None
    if equity and equity > 0:
        underlying_npat = net_income
        if asset_writedown and net_income:
            underlying_npat = net_income - asset_writedown
        if underlying_npat:
            underlying_roe = (underlying_npat / equity) * 100

    # FCF Yield
    fcf_yield = get_value(data, 'FCF Yield', 'Free Cash Flow Yield')
    if not fcf_yield:
        fcf = get_value(data, 'Free Cash Flow')
        market_cap = get_value(data, 'Market Capitalization')
        if fcf and market_cap and market_cap > 0:
            fcf_yield = (fcf / market_cap) * 100

    # Net Debt/EBITDA
    net_debt_ebitda = get_value(data, 'Net Debt / EBITDA Ratio')
    if not net_debt_ebitda:
        total_debt = get_value(data, 'Total Debt')
        cash = get_value(data, 'Cash & Equivalents')
        ebitda = get_value(data, 'EBITDA')
        if total_debt and cash is not None and ebitda and ebitda > 0:
            net_debt_ebitda = (total_debt - cash) / ebitda

    # Payout Ratio
    payout = get_value(data, 'Payout Ratio', 'Dividend Payout Ratio')
    if not payout:
        dividends = get_value(data, 'Common Dividends Paid', 'Dividends Paid')
        if dividends and net_income and net_income > 0:
            payout = (abs(dividends) / net_income) * 100

    # ===== 计算各项分数 =====
    aisc_score, aisc_level = score_aisc(aisc)
    life_score, life_level = score_reserves_life(reserves_life)
    capex_score, capex_level = score_capex_intensity(capex_intensity)
    roe_score, roe_level = score_underlying_roe(underlying_roe)
    fcf_score, fcf_level = score_fcf_yield(fcf_yield)
    leverage_score, leverage_level = score_leverage(net_debt_ebitda)
    payout_score, payout_level = score_payout(payout)

    # ===== 计算加权总分 =====
    weighted_score = (
        aisc_score * WEIGHTS['AISC'] +
        life_score * WEIGHTS['Reserves Life'] +
        capex_score * WEIGHTS['Capex Intensity'] +
        roe_score * WEIGHTS['Underlying ROE'] +
        fcf_score * WEIGHTS['FCF Yield'] +
        leverage_score * WEIGHTS['Leverage'] +
        payout_score * WEIGHTS['Payout']
    )

    # ===== 构建结果 =====
    return {
        'ticker': data.get('ticker', ''),
        'total_score': round(weighted_score, 2),
        'max_score': 10.0,
        'metrics': {
            'AISC': {
                'value': aisc,
                'score': aisc_score,
                'level': aisc_level,
                'benchmark': '60%-85%',
                'weight': WEIGHTS['AISC'],
                'description': '矿企的全成本指标。相当于"挖矿成本占收入比例"，60%为优秀(赚40%)，85%为预警(赚15%)'
            },
            'Reserves Life': {
                'value': reserves_life,
                'score': life_score,
                'level': life_level,
                'benchmark': '>20年',
                'weight': WEIGHTS['Reserves Life'],
                'description': '矿企的"保质期"，家里有矿能挖多久'
            },
            'Capex Intensity': {
                'value': capex_intensity,
                'score': capex_score,
                'level': capex_level,
                'benchmark': '8%-15%',
                'weight': WEIGHTS['Capex Intensity'],
                'description': '衡量扩张野心，钱是用来修补旧机器还是盖新厂房'
            },
            'Underlying ROE': {
                'value': underlying_roe,
                'score': roe_score,
                'level': roe_level,
                'benchmark': '15%-25%',
                'weight': WEIGHTS['Underlying ROE'],
                'description': '剔除资产减值后的真实赚钱效率'
            },
            'FCF Yield': {
                'value': fcf_yield,
                'score': fcf_score,
                'level': fcf_level,
                'benchmark': '6%-10%',
                'weight': WEIGHTS['FCF Yield'],
                'description': '矿企真金白银赚到的现金收益率'
            },
            'Leverage': {
                'value': net_debt_ebitda,
                'score': leverage_score,
                'level': leverage_level,
                'benchmark': '0.5x-1.5x',
                'weight': WEIGHTS['Leverage'],
                'description': '矿企债务压力，几年能还清债务'
            },
            'Payout': {
                'value': payout,
                'score': payout_score,
                'level': payout_level,
                'benchmark': '50%-70%',
                'weight': WEIGHTS['Payout'],
                'description': '愿不愿意把利润分给股东'
            }
        }
    }


# ==================== 测试入口 ====================

if __name__ == '__main__':
    print("=== 矿业计分卡测试 (score_material.md) ===\n")

    # 测试各指标评分函数
    print("--- AISC 评分 ---")
    print(f"AISC @ 50%: {score_aisc(50.0)}")
    print(f"AISC @ 65%: {score_aisc(65.0)}")
    print(f"AISC @ 80%: {score_aisc(80.0)}")
    print(f"AISC @ 90%: {score_aisc(90.0)}")
    print(f"AISC @ None: {score_aisc(None)}")

    print("\n--- Reserves Life 评分 ---")
    print(f"Life @ 25年: {score_reserves_life(25.0)}")
    print(f"Life @ 15年: {score_reserves_life(15.0)}")
    print(f"Life @ 10年: {score_reserves_life(10.0)}")
    print(f"Life @ 3年: {score_reserves_life(3.0)}")

    print("\n--- Capex Intensity 评分 ---")
    print(f"CI @ 20%: {score_capex_intensity(20.0)}")
    print(f"CI @ 12%: {score_capex_intensity(12.0)}")
    print(f"CI @ 5%: {score_capex_intensity(5.0)}")
    print(f"CI @ 1%: {score_capex_intensity(1.0)}")

    print("\n--- Underlying ROE 评分 ---")
    print(f"ROE @ 30%: {score_underlying_roe(30.0)}")
    print(f"ROE @ 20%: {score_underlying_roe(20.0)}")
    print(f"ROE @ 10%: {score_underlying_roe(10.0)}")
    print(f"ROE @ 3%: {score_underlying_roe(3.0)}")

    print("\n--- FCF Yield 评分 ---")
    print(f"FCF @ 12%: {score_fcf_yield(12.0)}")
    print(f"FCF @ 8%: {score_fcf_yield(8.0)}")
    print(f"FCF @ 3%: {score_fcf_yield(3.0)}")
    print(f"FCF @ -5%: {score_fcf_yield(-5.0)}")

    print("\n--- Leverage 评分 ---")
    print(f"Leverage @ 0.3x: {score_leverage(0.3)}")
    print(f"Leverage @ 0.8x: {score_leverage(0.8)}")
    print(f"Leverage @ 2.0x: {score_leverage(2.0)}")
    print(f"Leverage @ 4.0x: {score_leverage(4.0)}")

    print("\n--- Payout 评分 ---")
    print(f"Payout @ 60%: {score_payout(60.0)}")
    print(f"Payout @ 45%: {score_payout(45.0)}")
    print(f"Payout @ 20%: {score_payout(20.0)}")
    print(f"Payout @ 120%: {score_payout(120.0)}")

    print("\n=== 权重 ===")
    print(f"WEIGHTS: {WEIGHTS}")

    # 测试完整计算
    print("\n=== 完整评分测试 (满分案例) ===")
    perfect_data = {
        'ticker': 'RIO.AX',
        'income_statement': {
            'Revenue': {'FY 2025': 100000},
            'Cost of Revenue': {'FY 2025': 40000},
            'Capital Expenditures': {'FY 2025': -20000},
            'Net Income': {'FY 2025': 25000},
            'Asset Writedown': {'FY 2025': 0},
            'Common Dividends Paid': {'FY 2025': 15000}
        },
        'balance_sheet': {
            'Total Proved Reserves': {'FY 2025': 500},
            'Annual Production Volume': {'FY 2025': 20},
            'Construction in Progress': {'FY 2025': 15000},
            'Total PPE': {'FY 2025': 100000},
            'Total Common Equity': {'FY 2025': 80000},
            'Total Debt': {'FY 2025': 10000},
            'Cash & Equivalents': {'FY 2025': 15000},
            'EBITDA': {'FY 2025': 35000}
        },
        'cash_flow': {
            'Free Cash Flow': {'FY 2025': 10000}
        },
        'ratios': {
            'FCF Yield': {'FY 2025': 10.0},
            'Net Debt / EBITDA Ratio': {'FY 2025': -0.14},
            'Payout Ratio': {'FY 2025': 60}
        }
    }

    result = calculate_materials_score(perfect_data)
    print(f"Total Score: {result['total_score']}")
    for metric, info in result['metrics'].items():
        print(f"  {metric}: {info['value']} -> {info['score']} ({info['level']})")
