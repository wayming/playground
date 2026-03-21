"""
Consumer Staples Scorecard - 必需消费/零售行业基本面打分系统

根据 docs/score_consuming.md 实现零售六维度量化评分:
1. EBIT Margin (息税前利润率): >8% 为顶级
2. ROE (净资产收益率): >30% 为极高效率
3. Inventory Days (库存周转天数): <40天 为快消之王
4. OCF Margin (经营现金流利润率): >10% 为现金流极强
5. Forward PE (远期市盈率): 18-22x 为黄金区间
6. Market Share (市场份额): Top 1 或 >25% 为绝对领先
"""

from typing import Dict, Any, Optional, Tuple


# ==================== 评分函数 ====================

def score_ebit_margin(ebit_margin: Optional[float]) -> Tuple[float, str]:
    """
    EBIT Margin (息税前利润率) 评分

    判定逻辑:
        10分: > 8.0% (顶级零售商)
        7分: 5.0% - 8.0% (优质超市/药房)
        4分: 3.0% - 5.0% (普通零售)
        0分: < 2.5% (增收不增利)

    Returns:
        (score, level): 分数和评级
    """
    if ebit_margin is None:
        return 0.0, "N/A"

    if ebit_margin > 8.0:
        return 10.0, "excellent"
    elif ebit_margin >= 5.0:
        return 7.0, "good"
    elif ebit_margin >= 3.0:
        return 4.0, "fair"
    else:
        return 0.0, "poor"


def score_roe(roe: Optional[float]) -> Tuple[float, str]:
    """
    ROE (净资产收益率) 评分

    判定逻辑:
        10分: > 30% (极高效率)
        7分: 18% - 30% (行业优等生)
        4分: 12% - 18% (中规中矩)
        0分: < 10% (回报太低)

    Returns:
        (score, level): 分数和评级
    """
    if roe is None:
        return 0.0, "N/A"

    if roe > 30:
        return 10.0, "excellent"
    elif roe >= 18:
        return 7.0, "good"
    elif roe >= 12:
        return 4.0, "fair"
    else:
        return 0.0, "poor"


def score_inventory_days(inv_days: Optional[float]) -> Tuple[float, str]:
    """
    Inventory Days (库存周转天数) 评分

    判定逻辑:
        10分: < 40 天 (快消/超市之王)
        7分: 40 - 85 天 (综合零售/百货正常水平)
        4分: 85 - 110 天 (周转缓慢)
        0分: > 120 天 (库存积压风险严重)

    Returns:
        (score, level): 分数和评级
    """
    if inv_days is None:
        return 0.0, "N/A"

    if inv_days < 40:
        return 10.0, "excellent"
    elif inv_days <= 85:
        return 7.0, "good"
    elif inv_days <= 110:
        return 4.0, "fair"
    else:
        return 0.0, "poor"


def score_ocf_margin(ocf_margin: Optional[float]) -> Tuple[float, str]:
    """
    OCF Margin (经营现金流利润率) 评分

    判定逻辑:
        10分: > 10% (现金流极强)
        7分: 7% - 10% (稳健)
        4分: 4% - 7% (一般)
        0分: < 4% (入不敷出)

    Returns:
        (score, level): 分数和评级
    """
    if ocf_margin is None:
        return 0.0, "N/A"

    if ocf_margin > 10:
        return 10.0, "excellent"
    elif ocf_margin >= 7:
        return 7.0, "good"
    elif ocf_margin >= 4:
        return 4.0, "fair"
    else:
        return 0.0, "poor"


def score_forward_pe(fwd_pe: Optional[float]) -> Tuple[float, str]:
    """
    Forward PE (远期市盈率) 评分

    判定逻辑:
        10分: 18x - 22x (防御股黄金区间)
        7分: 22x - 26x (略有溢价)
        4分: 26x - 30x (过贵)
        0分: > 32x (估值泡沫)

    Returns:
        (score, level): 分数和评级
    """
    if fwd_pe is None:
        return 0.0, "N/A"

    if fwd_pe <= 22:
        return 10.0, "excellent"
    elif fwd_pe <= 26:
        return 7.0, "good"
    elif fwd_pe <= 30:
        return 4.0, "fair"
    else:
        return 0.0, "poor"


def score_market_share(market_share: Optional[float], rank: Optional[int] = None) -> Tuple[float, str]:
    """
    Market Share (市场份额) 评分

    判定逻辑:
        10分: 绝对领先 (Top 1 或份额 > 25%)
        7分: 行业前三 (头部效应明显)
        4分: 处于中游 (受巨头挤压)
        0分: 份额持续下滑 (护城河崩塌)

    Args:
        market_share: 市场份额百分比 (如 25.0 表示 25%)
        rank: 行业排名

    Returns:
        (score, level): 分数和评级
    """
    if market_share is None and rank is None:
        return 0.0, "N/A"

    # 绝对领先: Top 1 或 > 25%
    if rank == 1 or (market_share is not None and market_share > 25):
        return 10.0, "excellent"

    # 行业前三
    if rank is not None and rank <= 3:
        return 7.0, "good"

    # 处于中游
    if rank is not None and rank > 3:
        return 4.0, "fair"

    # 默认返回中游
    return 4.0, "fair"


# ==================== 权重配置 ====================

# 评分权重 (根据 score_consuming.md)
WEIGHTS = {
    'EBIT Margin': 0.20,
    'ROE': 0.20,
    'Inventory Days': 0.15,
    'OCF Margin': 0.15,
    'Forward PE': 0.20,
    'Market Share': 0.10
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


def get_value_by_period(data: Dict[str, Any], key: str, period: str = 'TTM') -> Optional[float]:
    """
    从数据字典中提取指定期间的值

    Args:
        data: 包含财务数据的字典
        key: 要查找的键名
        period: 期间 (TTM, FY 2025, FY 2024, etc.)

    Returns:
        找到的值 (float) 或 None
    """
    for section in ['ratios', 'income_statement', 'balance_sheet', 'cash_flow']:
        if section in data:
            section_data = data[section]
            if key in section_data:
                val = section_data[key]
                if isinstance(val, dict) and period in val:
                    return float(val[period])
    return None


# ==================== 主评分函数 ====================

def calculate_consumer_score(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    计算必需消费行业综合评分

    根据 docs/score_consuming.md 的公式:
    Score = (EBIT_Margin * 0.2) + (ROE * 0.2) + (Inventory_Days * 0.15) + (OCF_Margin * 0.15) + (Forward_PE * 0.2) + (Market_Share * 0.1)

    风险修正: 如果 Inventory_Days_Growth > 15%, Score = Score * 0.8

    Args:
        data: 包含财务数据的字典

    Returns:
        包含各项分数和总分的字典
    """
    # ===== 提取数据 =====
    # EBIT Margin
    ebit_margin = get_value(data, 'EBIT Margin', 'Operating Margin', 'EBIT Margin %')

    # ROE
    roe = get_value(data, 'ROE', 'Return on Equity (ROE)')

    # Inventory Days = (Inventory / Cost of Revenue) * 365
    inventory = get_value(data, 'Inventory', 'Inventories')
    cost_revenue = get_value(data, 'Cost of Revenue', 'Cost of Goods Sold')
    inv_days = None
    if inventory and cost_revenue and cost_revenue > 0:
        inv_days = (inventory / cost_revenue) * 365

    # Inventory Days Growth (用于风险修正)
    inv_days_ttm = get_value_by_period(data, 'Inventory', 'TTM')
    inv_days_fy2024 = get_value_by_period(data, 'Inventory', 'FY 2024')
    cost_ttm = get_value_by_period(data, 'Cost of Revenue', 'TTM')
    cost_fy2024 = get_value_by_period(data, 'Cost of Revenue', 'FY 2024')

    inv_days_growth = None
    if inv_days_ttm and cost_ttm and inv_days_fy2024 and cost_fy2024 and cost_ttm > 0 and cost_fy2024 > 0:
        inv_days_current = (inv_days_ttm / cost_ttm) * 365
        inv_days_prev = (inv_days_fy2024 / cost_fy2024) * 365
        if inv_days_prev > 0:
            inv_days_growth = ((inv_days_current - inv_days_prev) / inv_days_prev) * 100

    # OCF Margin = Operating Cash Flow / Revenue
    ocf = get_value(data, 'Operating Cash Flow')
    revenue = get_value(data, 'Revenue', 'Total Revenue', 'Operating Revenue')
    ocf_margin = None
    if ocf and revenue and revenue > 0:
        ocf_margin = (ocf / revenue) * 100

    # Forward PE
    fwd_pe = get_value(data, 'Forward PE', 'Forward Price to Earnings')

    # Market Share
    market_share = get_value(data, 'Market Share', 'Market Share %')
    market_rank = get_value(data, 'Market Rank', 'Rank')

    # ===== 计算各项分数 =====
    ebit_score, ebit_level = score_ebit_margin(ebit_margin)
    roe_score, roe_level = score_roe(roe)
    inv_score, inv_level = score_inventory_days(inv_days)
    ocf_score, ocf_level = score_ocf_margin(ocf_margin)
    fwd_score, fwd_level = score_forward_pe(fwd_pe)
    mkt_score, mkt_level = score_market_share(market_share, market_rank)

    # ===== 计算加权总分 =====
    weighted_score = (
        ebit_score * WEIGHTS['EBIT Margin'] +
        roe_score * WEIGHTS['ROE'] +
        inv_score * WEIGHTS['Inventory Days'] +
        ocf_score * WEIGHTS['OCF Margin'] +
        fwd_score * WEIGHTS['Forward PE'] +
        mkt_score * WEIGHTS['Market Share']
    )

    # 风险修正: 如果 Inventory_Days_Growth > 15%, 总分打 8 折
    risk_penalty = inv_days_growth is not None and inv_days_growth > 15
    if risk_penalty:
        weighted_score = weighted_score * 0.8

    # ===== 构建结果 =====
    return {
        'ticker': data.get('ticker', ''),
        'total_score': round(weighted_score, 2),
        'max_score': 10.0,
        'risk_penalty': risk_penalty,
        'metrics': {
            'EBIT Margin': {
                'value': ebit_margin,
                'score': ebit_score,
                'level': ebit_level,
                'benchmark': '>8% (10pts), 5-8% (7pts), 3-5% (4pts)',
                'weight': WEIGHTS['EBIT Margin'],
                'description': '息税前利润率，零售业盈利能力'
            },
            'ROE': {
                'value': roe,
                'score': roe_score,
                'level': roe_level,
                'benchmark': '>30% (10pts), 18-30% (7pts), 12-18% (4pts)',
                'weight': WEIGHTS['ROE'],
                'description': '股东投入的回报率'
            },
            'Inventory Days': {
                'value': inv_days,
                'score': inv_score,
                'level': inv_level,
                'benchmark': '<40天 (10pts), 40-85天 (7pts), 85-110天 (4pts)',
                'weight': WEIGHTS['Inventory Days'],
                'description': '库存周转天数，现金回笼速度'
            },
            'OCF Margin': {
                'value': ocf_margin,
                'score': ocf_score,
                'level': ocf_level,
                'benchmark': '>10% (10pts), 7-10% (7pts), 4-7% (4pts)',
                'weight': WEIGHTS['OCF Margin'],
                'description': '经营现金流利润率'
            },
            'Forward PE': {
                'value': fwd_pe,
                'score': fwd_score,
                'level': fwd_level,
                'benchmark': '18-22x (10pts), 22-26x (7pts), 26-30x (4pts)',
                'weight': WEIGHTS['Forward PE'],
                'description': '远期市盈率，估值性价比'
            },
            'Market Share': {
                'value': market_share,
                'score': mkt_score,
                'level': mkt_level,
                'benchmark': 'Top 1/>25% (10pts), Top 3 (7pts), Middle (4pts)',
                'weight': WEIGHTS['Market Share'],
                'description': '市场份额，行业定价权'
            }
        }
    }


# ==================== 测试入口 ====================

if __name__ == '__main__':
    print("=== 必需消费计分卡测试 (score_consuming.md) ===\n")

    # 测试各指标评分函数
    print("--- EBIT Margin 评分 ---")
    print(f"EBIT @ 10%: {score_ebit_margin(10)}")
    print(f"EBIT @ 6%: {score_ebit_margin(6)}")
    print(f"EBIT @ 4%: {score_ebit_margin(4)}")
    print(f"EBIT @ 2%: {score_ebit_margin(2)}")

    print("\n--- ROE 评分 ---")
    print(f"ROE @ 35%: {score_roe(35)}")
    print(f"ROE @ 25%: {score_roe(25)}")
    print(f"ROE @ 15%: {score_roe(15)}")
    print(f"ROE @ 8%: {score_roe(8)}")

    print("\n--- Inventory Days 评分 ---")
    print(f"Inv @ 30天: {score_inventory_days(30)}")
    print(f"Inv @ 60天: {score_inventory_days(60)}")
    print(f"Inv @ 100天: {score_inventory_days(100)}")
    print(f"Inv @ 130天: {score_inventory_days(130)}")

    print("\n--- OCF Margin 评分 ---")
    print(f"OCF @ 12%: {score_ocf_margin(12)}")
    print(f"OCF @ 8%: {score_ocf_margin(8)}")
    print(f"OCF @ 5%: {score_ocf_margin(5)}")
    print(f"OCF @ 2%: {score_ocf_margin(2)}")

    print("\n--- Forward PE 评分 ---")
    print(f"PE @ 20x: {score_forward_pe(20)}")
    print(f"PE @ 24x: {score_forward_pe(24)}")
    print(f"PE @ 28x: {score_forward_pe(28)}")
    print(f"PE @ 35x: {score_forward_pe(35)}")

    print("\n--- Market Share 评分 ---")
    print(f"Share @ 30% (Rank 1): {score_market_share(30, 1)}")
    print(f"Share @ 15% (Rank 2): {score_market_share(15, 2)}")
    print(f"Share @ 8% (Rank 5): {score_market_share(8, 5)}")

    print("\n=== 权重 ===")
    print(f"WEIGHTS: {WEIGHTS}")
    print(f"Total weight: {sum(WEIGHTS.values())}")

    # 测试完整计算
    print("\n=== 完整评分测试 (满分案例) ===")
    perfect_data = {
        'ticker': 'WES.AX',
        'income_statement': {
            'Operating Income': {'TTM': 1200},
            'Revenue': {'TTM': 10000},
            'Cost of Revenue': {'TTM': 8000},
        },
        'cash_flow': {
            'Operating Cash Flow': {'TTM': 1200},
        },
        'balance_sheet': {
            'Inventory': {'TTM': 800},
            'Total Common Equity': {'TTM': 3000},
            'Net Income to Common': {'TTM': 1000},
        },
        'ratios': {
            'EBIT Margin': {'TTM': 12.0},
            'ROE': {'TTM': 33.0},
            'Forward PE': {'TTM': 20.0},
            'Market Share': {'TTM': 30.0},
            'Market Rank': {'TTM': 1},
        }
    }

    result = calculate_consumer_score(perfect_data)
    print(f"Total Score: {result['total_score']}")
    print(f"Risk Penalty: {result['risk_penalty']}")
    for metric, info in result['metrics'].items():
        print(f"  {metric}: {info['value']} -> {info['score']} ({info['level']})")
