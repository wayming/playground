"""
Infrastructure Scorecard - 基建行业基本面打分系统

根据 docs/score_infra.md 实现基建六维度量化评分:
1. EBITDA Margin (运营利润率): >60% 为顶级
2. Interest Cover Ratio (利息覆盖率): >4.0x 为极度安全
3. Cash Conversion (现金转化率): >85% 为现金奶牛
4. EV/EBITDA (企业价值倍数): 10-13x 为低估
5. CPI Linkage (抗通胀能力): >80% 为完全抗通胀
6. WACE (合同剩余期限): >20年 为终身保险
"""

from typing import Dict, Any, Optional, Tuple


# ==================== 评分函数 ====================

def score_ebitda_margin(ebitda_margin: Optional[float]) -> Tuple[float, str]:
    """
    EBITDA Margin (运营利润率) 评分

    判定逻辑:
        10分: > 60% (顶级垄断资产)
        7分: 45% - 60% (优质基建)
        4分: 30% - 45% (竞争性基建/公用事业)
        0分: < 25% (效率极低)

    Returns:
        (score, level): 分数和评级
    """
    if ebitda_margin is None:
        return 0.0, "N/A"

    if ebitda_margin > 60:
        return 10.0, "excellent"
    elif ebitda_margin >= 45:
        return 7.0, "good"
    elif ebitda_margin >= 30:
        return 4.0, "fair"
    else:
        return 0.0, "poor"


def score_interest_cover(interest_cover: Optional[float]) -> Tuple[float, str]:
    """
    Interest Cover Ratio (利息覆盖率) 评分

    判定逻辑:
        10分: > 4.0x (极度安全)
        7分: 2.5x - 4.0x (稳健)
        4分: 1.5x - 2.5x (预警)
        0分: < 1.2x (破产风险)

    Returns:
        (score, level): 分数和评级
    """
    if interest_cover is None:
        return 0.0, "N/A"

    if interest_cover > 4.0:
        return 10.0, "excellent"
    elif interest_cover >= 2.5:
        return 7.0, "good"
    elif interest_cover >= 1.5:
        return 4.0, "fair"
    else:
        return 0.0, "poor"


def score_cash_conversion(cash_conv: Optional[float]) -> Tuple[float, str]:
    """
    Cash Conversion (现金转化率) 评分

    判定逻辑:
        10分: > 85% (现金奶牛)
        7分: 70% - 85% (良好)
        4分: 50% - 70% (一般)
        0分: < 40% (账面富贵)

    Returns:
        (score, level): 分数和评级
    """
    if cash_conv is None:
        return 0.0, "N/A"

    if cash_conv > 85:
        return 10.0, "excellent"
    elif cash_conv >= 70:
        return 7.0, "good"
    elif cash_conv >= 50:
        return 4.0, "fair"
    else:
        return 0.0, "poor"


def score_ev_ebitda(ev_ebitda: Optional[float]) -> Tuple[float, str]:
    """
    EV/EBITDA (企业价值倍数) 评分

    判定逻辑:
        10分: 10x - 13x (低估/合理)
        7分: 13x - 16x (略微溢价)
        4分: 16x - 20x (估值过热)
        0分: > 22x (泡沫严重)

    Returns:
        (score, level): 分数和评级
    """
    if ev_ebitda is None:
        return 0.0, "N/A"

    if ev_ebitda <= 13:
        return 10.0, "excellent"
    elif ev_ebitda <= 16:
        return 7.0, "good"
    elif ev_ebitda <= 20:
        return 4.0, "fair"
    else:
        return 0.0, "poor"


def score_cpi_linkage(cpi_linkage: Optional[float]) -> Tuple[float, str]:
    """
    CPI Linkage (抗通胀能力) 评分

    判定逻辑:
        10分: > 80% (完全抗通胀)
        7分: 50% - 80% (较强对冲)
        4分: 20% - 50% (部分转嫁)
        0分: < 20% (受通胀伤害)

    Returns:
        (score, level): 分数和评级
    """
    if cpi_linkage is None:
        return 0.0, "N/A"

    if cpi_linkage > 80:
        return 10.0, "excellent"
    elif cpi_linkage >= 50:
        return 7.0, "good"
    elif cpi_linkage >= 20:
        return 4.0, "fair"
    else:
        return 0.0, "poor"


def score_wace(wace: Optional[float]) -> Tuple[float, str]:
    """
    WACE (合同剩余期限) 评分

    判定逻辑:
        10分: > 20年 (终身保险)
        7分: 12 - 20年 (非常稳健)
        4分: 7 - 12年 (中规中矩)
        0分: < 5年 (合同到期风险)

    Returns:
        (score, level): 分数和评级
    """
    if wace is None:
        return 0.0, "N/A"

    if wace > 20:
        return 10.0, "excellent"
    elif wace >= 12:
        return 7.0, "good"
    elif wace >= 7:
        return 4.0, "fair"
    else:
        return 0.0, "poor"


# ==================== 权重配置 ====================

# 评分权重 (根据 score_infra.md)
WEIGHTS = {
    'EBITDA Margin': 0.20,
    'Interest Cover': 0.25,
    'Cash Conversion': 0.15,
    'EV/EBITDA': 0.15,
    'CPI Linkage': 0.15,
    'WACE': 0.10
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

def calculate_infrastructure_score(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    计算基建行业综合评分

    根据 docs/score_infra.md 的公式:
    Score = (EBITDA_Margin * 0.2) + (Interest_Cover * 0.25) + (Cash_Conversion * 0.15) + (EV_EBITDA * 0.15) + (CPI_Link * 0.15) + (WACE * 0.1)

    风险修正: 如果 Interest_Cover < 1.4, Score = Score * 0.5

    Args:
        data: 包含财务数据的字典

    Returns:
        包含各项分数和总分的字典
    """
    # ===== 提取数据 =====
    # EBITDA Margin
    ebitda_margin = get_value(data, 'EBITDA Margin')

    # Interest Cover
    interest_cover = get_value(data, 'Interest Coverage Ratio')
    if not interest_cover:
        # 尝试从组件计算: Interest Cover = EBIT / Interest Expense
        ebit = get_value(data, 'EBIT', 'Operating Income')
        interest_expense = get_value(data, 'Interest Expense')
        if ebit and interest_expense and interest_expense > 0:
            interest_cover = abs(ebit / interest_expense)

    # Cash Conversion = OCF / EBITDA
    ocf = get_value(data, 'Operating Cash Flow')
    ebitda = get_value(data, 'EBITDA')
    cash_conversion = None
    if ocf and ebitda and ebitda != 0:
        cash_conversion = (ocf / ebitda) * 100

    # EV/EBITDA
    ev_ebitda = get_value(data, 'EV/EBITDA Ratio', 'EV / EBITDA Ratio')
    if not ev_ebitda:
        # 尝试从组件计算: (Market Cap + Debt - Cash) / EBITDA
        market_cap = get_value(data, 'Market Capitalization')
        total_debt = get_value(data, 'Total Debt')
        cash = get_value(data, 'Cash & Equivalents')
        if market_cap and total_debt and ebitda and ebitda > 0:
            ev_ebitda = (market_cap + total_debt - (cash or 0)) / ebitda

    # CPI Linkage
    cpi_linkage = get_value(data, 'CPI Linkage', 'CPI Linkage %')

    # WACE
    wace = get_value(data, 'WACE', 'Weighted Average Contract Expiry', 'Contract Expiry (Years)')

    # ===== 计算各项分数 =====
    ebitda_score, ebitda_level = score_ebitda_margin(ebitda_margin)
    interest_score, interest_level = score_interest_cover(interest_cover)
    cash_score, cash_level = score_cash_conversion(cash_conversion)
    ev_score, ev_level = score_ev_ebitda(ev_ebitda)
    cpi_score, cpi_level = score_cpi_linkage(cpi_linkage)
    wace_score, wace_level = score_wace(wace)

    # ===== 计算加权总分 =====
    weighted_score = (
        ebitda_score * WEIGHTS['EBITDA Margin'] +
        interest_score * WEIGHTS['Interest Cover'] +
        cash_score * WEIGHTS['Cash Conversion'] +
        ev_score * WEIGHTS['EV/EBITDA'] +
        cpi_score * WEIGHTS['CPI Linkage'] +
        wace_score * WEIGHTS['WACE']
    )

    # 风险修正: 如果 Interest_Cover < 1.4, 总分折半
    risk_penalty = interest_cover is not None and interest_cover < 1.4
    if risk_penalty:
        weighted_score = weighted_score * 0.5

    # ===== 构建结果 =====
    return {
        'ticker': data.get('ticker', ''),
        'total_score': round(weighted_score, 2),
        'max_score': 10.0,
        'risk_penalty': risk_penalty,
        'metrics': {
            'EBITDA Margin': {
                'value': ebitda_margin,
                'score': ebitda_score,
                'level': ebitda_level,
                'benchmark': '>60% (10pts), 45-60% (7pts), 30-45% (4pts)',
                'weight': WEIGHTS['EBITDA Margin'],
                'description': '剔除折旧和利息后的运营利润率'
            },
            'Interest Cover': {
                'value': interest_cover,
                'score': interest_score,
                'level': interest_level,
                'benchmark': '>4.0x (10pts), 2.5-4.0x (7pts), 1.5-2.5x (4pts)',
                'weight': WEIGHTS['Interest Cover'],
                'description': '赚到的钱够交几次银行利息'
            },
            'Cash Conversion': {
                'value': cash_conversion,
                'score': cash_score,
                'level': cash_level,
                'benchmark': '>85% (10pts), 70-85% (7pts), 50-70% (4pts)',
                'weight': WEIGHTS['Cash Conversion'],
                'description': 'EBITDA有多少能变成现金'
            },
            'EV/EBITDA': {
                'value': ev_ebitda,
                'score': ev_score,
                'level': ev_level,
                'benchmark': '10-13x (10pts), 13-16x (7pts), 16-20x (4pts)',
                'weight': WEIGHTS['EV/EBITDA'],
                'description': '考虑债务后的真实估值'
            },
            'CPI Linkage': {
                'value': cpi_linkage,
                'score': cpi_score,
                'level': cpi_level,
                'benchmark': '>80% (10pts), 50-80% (7pts), 20-50% (4pts)',
                'weight': WEIGHTS['CPI Linkage'],
                'description': '收入与通胀挂钩的比例'
            },
            'WACE': {
                'value': wace,
                'score': wace_score,
                'level': wace_level,
                'benchmark': '>20年 (10pts), 12-20年 (7pts), 7-12年 (4pts)',
                'weight': WEIGHTS['WACE'],
                'description': '加权平均合同剩余期限'
            }
        }
    }


# ==================== 测试入口 ====================

if __name__ == '__main__':
    print("=== 基建计分卡测试 (score_infra.md) ===\n")

    # 测试各指标评分函数
    print("--- EBITDA Margin 评分 ---")
    print(f"EBITDA @ 65%: {score_ebitda_margin(65)}")
    print(f"EBITDA @ 50%: {score_ebitda_margin(50)}")
    print(f"EBITDA @ 35%: {score_ebitda_margin(35)}")
    print(f"EBITDA @ 20%: {score_ebitda_margin(20)}")

    print("\n--- Interest Cover 评分 ---")
    print(f"Interest @ 5.0x: {score_interest_cover(5.0)}")
    print(f"Interest @ 3.0x: {score_interest_cover(3.0)}")
    print(f"Interest @ 2.0x: {score_interest_cover(2.0)}")
    print(f"Interest @ 1.0x: {score_interest_cover(1.0)}")

    print("\n--- Cash Conversion 评分 ---")
    print(f"Cash Conv @ 90%: {score_cash_conversion(90)}")
    print(f"Cash Conv @ 75%: {score_cash_conversion(75)}")
    print(f"Cash Conv @ 60%: {score_cash_conversion(60)}")
    print(f"Cash Conv @ 30%: {score_cash_conversion(30)}")

    print("\n--- EV/EBITDA 评分 ---")
    print(f"EV/EBITDA @ 12x: {score_ev_ebitda(12)}")
    print(f"EV/EBITDA @ 15x: {score_ev_ebitda(15)}")
    print(f"EV/EBITDA @ 18x: {score_ev_ebitda(18)}")
    print(f"EV/EBITDA @ 25x: {score_ev_ebitda(25)}")

    print("\n--- CPI Linkage 评分 ---")
    print(f"CPI @ 85%: {score_cpi_linkage(85)}")
    print(f"CPI @ 65%: {score_cpi_linkage(65)}")
    print(f"CPI @ 35%: {score_cpi_linkage(35)}")
    print(f"CPI @ 10%: {score_cpi_linkage(10)}")

    print("\n--- WACE 评分 ---")
    print(f"WACE @ 25年: {score_wace(25)}")
    print(f"WACE @ 15年: {score_wace(15)}")
    print(f"WACE @ 10年: {score_wace(10)}")
    print(f"WACE @ 3年: {score_wace(3)}")

    print("\n=== 权重 ===")
    print(f"WEIGHTS: {WEIGHTS}")
    print(f"Total weight: {sum(WEIGHTS.values())}")

    # 测试完整计算
    print("\n=== 完整评分测试 (满分案例) ===")
    perfect_data = {
        'ticker': 'APA.AX',
        'income_statement': {
            'EBITDA': {'TTM': 1000},
            'Operating Income': {'TTM': 800},
            'Interest Expense': {'TTM': 100},
        },
        'cash_flow': {
            'Operating Cash Flow': {'TTM': 900},
        },
        'balance_sheet': {
            'Cash & Equivalents': {'TTM': 200},
        },
        'ratios': {
            'EBITDA Margin': {'TTM': 65.0},
            'Interest Coverage Ratio': {'TTM': 5.0},
            'EV/EBITDA Ratio': {'TTM': 12.0},
            'CPI Linkage': {'TTM': 85.0},
            'WACE': {'TTM': 25.0}
        }
    }

    result = calculate_infrastructure_score(perfect_data)
    print(f"Total Score: {result['total_score']}")
    print(f"Risk Penalty: {result['risk_penalty']}")
    for metric, info in result['metrics'].items():
        print(f"  {metric}: {info['value']} -> {info['score']} ({info['level']})")
