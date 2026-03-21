"""
Banks Scorecard - 银行基本面打分系统

根据 docs/score_bank.md 实现银行七维度量化评分:
1. NIM (净息差): 1.8%-2.1% 区间评分
2. CET1 Ratio (一级资本): > 11.5% 或 >= 6.5%
3. Cost-to-Income (成本收入比): <45% 为目标
4. ROE (净资产收益率): 11%-13% 区间评分
5. Credit Risk (坏账风险): <0.15% 为目标
6. Payout Ratio (分红率): 70%-80% 区间评分
7. LVR (贷款价值比): <50% 为目标，>75% 时总分折半
"""

from typing import Dict, Any, Optional, Tuple


# ==================== 评分函数 ====================

def score_nim(nim: Optional[float]) -> Tuple[float, str]:
    """
    NIM (净息差) 评分

    判定逻辑:
        10分: >= 2.1%
        7分: 1.8% - 2.1%
        4分: 1.6% - 1.8%
        0分: < 1.6%

    Returns:
        (score, level): 分数和评级
    """
    if nim is None:
        return 0.0, "N/A"

    if nim >= 2.1:
        return 10.0, "excellent"
    elif nim >= 1.8:
        return 7.0, "good"
    elif nim >= 1.6:
        return 4.0, "fair"
    else:
        return 0.0, "poor"


def score_cet1(cet1: Optional[float]) -> Tuple[float, str]:
    """
    CET1 Ratio (一级资本充足率) 评分

    判定逻辑:
        - 如果 CET1 >= 11%: 使用官方标准
          - >= 12.5%: 10分
          - 11% - 12.5%: 7分
          - < 10.5%: 0分

        - 如果 CET1 < 11%: 使用澳洲标准
          - >= 6.5%: 10分
          - 5.5% - 6.5%: 7分
          - < 5%: 0分

    Args:
        cet1: CET1 Ratio (百分比，如 12.5 表示 12.5%)

    Returns:
        (score, level): 分数和评级
    """
    if cet1 is None:
        return 0.0, "N/A"

    # CET1 >= 11% 使用官方标准
    if cet1 >= 11.0:
        if cet1 >= 12.5:
            return 10.0, "excellent"
        else:  # 11.0 <= cet1 < 12.5
            return 7.0, "good"
    # CET1 < 11% 使用澳洲标准
    else:
        if cet1 >= 6.5:
            return 10.0, "excellent"
        elif cet1 >= 5.5:
            return 7.0, "good"
        else:
            return 0.0, "poor"


def score_cost_to_income(cti: Optional[float]) -> Tuple[float, str]:
    """
    Cost-to-Income (成本收入比) 评分

    判定逻辑:
        10分: < 43%
        7分: 43% - 47%
        4分: 48% - 52%
        0分: > 55%

    Returns:
        (score, level): 分数和评级
    """
    if cti is None:
        return 0.0, "N/A"

    if cti < 43:
        return 10.0, "excellent"
    elif cti <= 47:
        return 7.0, "good"
    elif cti <= 52:
        return 4.0, "fair"
    else:
        return 0.0, "poor"


def score_roe(roe: Optional[float]) -> Tuple[float, str]:
    """
    ROE (净资产收益率) 评分

    判定逻辑:
        10分: >= 14%
        7分: 11% - 13.9%
        4分: 8% - 10.9%
        0分: < 7%

    Returns:
        (score, level): 分数和评级
    """
    if roe is None:
        return 0.0, "N/A"

    if roe >= 14:
        return 10.0, "excellent"
    elif roe >= 11:
        return 7.0, "good"
    elif roe >= 8:
        return 4.0, "fair"
    else:
        return 0.0, "poor"


def score_credit_risk(provision: Optional[float], gross_loans: Optional[float]) -> Tuple[float, str]:
    """
    Credit Risk (坏账风险) 评分

    公式: Credit Risk = Provision for Loan Losses / Gross Loans * 100

    判定逻辑:
        10分: < 0.10%
        7分: 0.11% - 0.20%
        4分: 0.21% - 0.40%
        0分: > 0.50%

    Returns:
        (score, level): 分数和评级
    """
    if provision is None or gross_loans is None or gross_loans == 0:
        return 0.0, "N/A"

    bad_debt_ratio = (provision / gross_loans) * 100

    if bad_debt_ratio < 0.10:
        return 10.0, "excellent"
    elif bad_debt_ratio <= 0.20:
        return 7.0, "good"
    elif bad_debt_ratio <= 0.40:
        return 4.0, "fair"
    else:
        return 0.0, "poor"


def score_payout(payout: Optional[float]) -> Tuple[float, str]:
    """
    Payout Ratio (分红率) 评分

    判定逻辑:
        10分: 70% - 75% (黄金平衡点)
        7分: 76% - 85% (慷慨)
        4分: 50% - 69% (保留增长)
        0分: > 95% (不可持续)

    Returns:
        (score, level): 分数和评级
    """
    if payout is None:
        return 0.0, "N/A"

    if 70 <= payout <= 75:
        return 10.0, "excellent"
    elif 76 <= payout <= 85:
        return 7.0, "good"
    elif 50 <= payout <= 69:
        return 4.0, "fair"
    else:
        return 0.0, "poor"


def score_lvr(lvr: Optional[float]) -> Tuple[float, str]:
    """
    LVR (贷款价值比) 评分

    判定逻辑:
        10分: < 50% (极度安全)
        7分: 50% - 60% (标准稳健)
        4分: 60% - 70% (风险敞口增大)
        0分: > 75% (高杠杆，有系统性风险)

    Returns:
        (score, level): 分数和评级
    """
    if lvr is None:
        return 0.0, "N/A"

    if lvr < 50:
        return 10.0, "excellent"
    elif lvr <= 60:
        return 7.0, "good"
    elif lvr <= 70:
        return 4.0, "fair"
    else:
        return 0.0, "poor"


# ==================== 权重配置 ====================

# 评分权重 (根据 score_bank.md)
WEIGHTS = {
    'NIM': 0.20,
    'CET1': 0.20,
    'Cost-to-Income': 0.15,
    'ROE': 0.15,
    'Credit Risk': 0.20,
    'Payout': 0.10
}


# ==================== 数据提取工具 ====================

def get_value(data: Dict[str, Any], *keys: str) -> Optional[float]:
    """
    从数据字典中提取值

    优先级: TTM > Current > FY 2025 > Annual Report 2025

    Args:
        data: 包含财务数据的字典 (ratios/income_statement/balance_sheet/cash_flow/extra)
        *keys: 要查找的键名

    Returns:
        找到的值 (float) 或 None
    """
    # 定义优先级
    periods = ['TTM', 'Current', 'FY 2025', 'Annual Report 2025', 'FY 2024']

    for key in keys:
        for section in ['ratios', 'income_statement', 'balance_sheet', 'cash_flow', 'extra']:
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

def calculate_banks_score(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    计算银行综合评分

    根据 docs/score_bank.md 的公式:
    Score = (NIM_Score * 0.2) + (CET1_Score * 0.2) + (CIR_Score * 0.15) + (ROE_Score * 0.15) + (Credit_Score * 0.2) + (Payout_Score * 0.1)

    如果 LVR > 75%: Score = Score * 0.5

    Args:
        data: 包含财务数据的字典

    Returns:
        包含各项分数和总分的字典
    """
    # ===== 提取数据 =====
    # NIM 相关
    net_interest_income = get_value(data, 'Net Interest Income')
    cash = get_value(data, 'Cash & Equivalents')
    investment_securities = get_value(data, 'Investment Securities')
    trading_securities = get_value(data, 'Trading Asset Securities')
    net_loans = get_value(data, 'Net Loans')

    # 计算 IEA (Interest Earning Assets)
    iea = 0
    if cash:
        iea += cash
    if investment_securities:
        iea += investment_securities
    if trading_securities:
        iea += trading_securities
    if net_loans:
        iea += net_loans

    # 计算 NIM
    nim = None
    if net_interest_income and iea > 0:
        nim = (net_interest_income / iea) * 100

    # 其他指标
    cet1 = get_value(data, 'CET1 Ratio', 'Common Equity Tier 1 Ratio')
    # 如果没有 CET1 Ratio，尝试从 CET1 Capital 和 RWA 计算
    if not cet1:
        cet1_capital = get_value(data, 'Common Equity Tier 1 Capital')
        rwa = get_value(data, 'Risk Weighted Assets')
        if cet1_capital and rwa and rwa > 0:
            cet1 = (cet1_capital / rwa) * 100

    # Cost-to-Income: 如果没有直接数据，尝试计算
    cost_to_income = get_value(data, 'Cost-to-Income Ratio', 'Cost to Income Ratio', 'Operating Efficiency Ratio')
    if not cost_to_income:
        # Cost-to-Income = Total Non-Interest Expense / Revenue * 100
        total_expense = get_value(data, 'Total Non-Interest Expense', 'Operating Expenses', 'Cost of Operations')
        revenue = get_value(data, 'Revenues Before Loan Losses', 'Total Income', 'Revenue', 'Total Revenue', 'Operating Revenue')
        if total_expense and revenue and revenue > 0:
            cost_to_income = (total_expense / revenue) * 100

    roe = get_value(data, 'Return on Equity (ROE)', 'ROE')
    provision = get_value(data, 'Provision for Loan Losses', 'Loan Loss Provision', 'Credit Loss Provision')
    gross_loans = get_value(data, 'Gross Loans')
    payout = get_value(data, 'Payout Ratio', 'Dividend Payout Ratio')

    # LVR: 优先使用 Group Average LVR
    lvr = get_value(data, 'LVR', 'Loan to Value Ratio', 'Group Average LVR')

    # ===== 计算各项分数 =====
    nim_score, nim_level = score_nim(nim)
    cet1_score, cet1_level = score_cet1(cet1)
    cti_score, cti_level = score_cost_to_income(cost_to_income)
    roe_score, roe_level = score_roe(roe)
    credit_score, credit_level = score_credit_risk(provision, gross_loans)
    payout_score, payout_level = score_payout(payout)
    lvr_score, lvr_level = score_lvr(lvr)

    # ===== 计算加权总分 =====
    weighted_score = (
        nim_score * WEIGHTS['NIM'] +
        cet1_score * WEIGHTS['CET1'] +
        cti_score * WEIGHTS['Cost-to-Income'] +
        roe_score * WEIGHTS['ROE'] +
        credit_score * WEIGHTS['Credit Risk'] +
        payout_score * WEIGHTS['Payout']
    )

    # LVR 惩罚: 如果 LVR > 75%, 总分折半
    if lvr is not None and lvr > 75:
        weighted_score = weighted_score * 0.5

    # ===== 构建结果 =====
    return {
        'ticker': data.get('ticker', ''),
        'total_score': round(weighted_score, 2),
        'max_score': 10.0,
        'lvr_penalty': lvr is not None and lvr > 75,
        'metrics': {
            'NIM': {
                'value': nim,
                'score': nim_score,
                'level': nim_level,
                'benchmark': '1.8%-2.1%',
                'weight': WEIGHTS['NIM'],
                'description': '银行的"进销差价"，越高说明吃利差的能力越强'
            },
            'CET1': {
                'value': cet1,
                'score': cet1_score,
                'level': cet1_level,
                'benchmark': '>11.5% 或 >=6.5%',
                'weight': WEIGHTS['CET1'],
                'description': '压箱底的保命钱，应对金融危机的底气'
            },
            'Cost-to-Income': {
                'value': cost_to_income,
                'score': cti_score,
                'level': cti_level,
                'benchmark': '<45%',
                'weight': WEIGHTS['Cost-to-Income'],
                'description': '赚100块钱要花多少水电费和人工，越低越精简高效'
            },
            'ROE': {
                'value': roe,
                'score': roe_score,
                'level': roe_level,
                'benchmark': '11%-13%',
                'weight': WEIGHTS['ROE'],
                'description': '股东投入1块钱，一年能收回多少钱'
            },
            'Credit Risk': {
                'value': (provision / gross_loans * 100) if provision and gross_loans else None,
                'score': credit_score,
                'level': credit_level,
                'benchmark': '<0.15%',
                'weight': WEIGHTS['Credit Risk'],
                'description': '每借出去100块钱，有多少是预计收不回来的'
            },
            'Payout': {
                'value': payout,
                'score': payout_score,
                'level': payout_level,
                'benchmark': '70%-80%',
                'weight': WEIGHTS['Payout'],
                'description': '赚到的钱里有多少是真金白银发给股东的'
            },
            'LVR': {
                'value': lvr,
                'score': lvr_score,
                'level': lvr_level,
                'benchmark': '<50%',
                'weight': 0,  # LVR 不直接参与加权，只做惩罚
                'description': '房子值100万，银行借出去多少。>75%有系统性风险'
            }
        }
    }


# ==================== 测试入口 ====================

if __name__ == '__main__':
    print("=== 银行计分卡测试 (score_bank.md) ===\n")

    # 测试各指标评分函数
    print("--- NIM 评分 ---")
    print(f"NIM @ 2.2%: {score_nim(2.2)}")
    print(f"NIM @ 1.9%: {score_nim(1.9)}")
    print(f"NIM @ 1.7%: {score_nim(1.7)}")
    print(f"NIM @ 1.5%: {score_nim(1.5)}")
    print(f"NIM @ None: {score_nim(None)}")

    print("\n--- CET1 评分 ---")
    print(f"CET1 @ 13%: {score_cet1(13.0)}")
    print(f"CET1 @ 6.0%: {score_cet1(6.0)}")
    print(f"CET1 @ 5.0%: {score_cet1(5.0)}")

    print("\n--- Cost-to-Income 评分 ---")
    print(f"CTI @ 40%: {score_cost_to_income(40.0)}")
    print(f"CTI @ 45%: {score_cost_to_income(45.0)}")
    print(f"CTI @ 50%: {score_cost_to_income(50.0)}")
    print(f"CTI @ 56%: {score_cost_to_income(56.0)}")

    print("\n--- ROE 评分 ---")
    print(f"ROE @ 15%: {score_roe(15.0)}")
    print(f"ROE @ 12%: {score_roe(12.0)}")
    print(f"ROE @ 9%: {score_roe(9.0)}")
    print(f"ROE @ 5%: {score_roe(5.0)}")

    print("\n--- Credit Risk 评分 ---")
    print(f"Credit @ 0.05%/100000: {score_credit_risk(50, 100000)}")
    print(f"Credit @ 0.15%/100000: {score_credit_risk(150, 100000)}")
    print(f"Credit @ 0.30%/100000: {score_credit_risk(300, 100000)}")
    print(f"Credit @ 0.60%/100000: {score_credit_risk(600, 100000)}")

    print("\n--- Payout 评分 ---")
    print(f"Payout @ 72%: {score_payout(72.0)}")
    print(f"Payout @ 80%: {score_payout(80.0)}")
    print(f"Payout @ 60%: {score_payout(60.0)}")
    print(f"Payout @ 96%: {score_payout(96.0)}")

    print("\n--- LVR 评分 ---")
    print(f"LVR @ 45%: {score_lvr(45.0)}")
    print(f"LVR @ 55%: {score_lvr(55.0)}")
    print(f"LVR @ 65%: {score_lvr(65.0)}")
    print(f"LVR @ 80%: {score_lvr(80.0)}")

    print("\n=== 权重 ===")
    print(f"WEIGHTS: {WEIGHTS}")

    # 测试完整计算
    print("\n=== 完整评分测试 (满分案例) ===")
    perfect_data = {
        'ticker': 'TEST.AX',
        'income_statement': {
            'Net Interest Income': {'TTM': 5000},
            'Provision for Loan Losses': {'TTM': 50},
            'Revenue': {'TTM': 20000}
        },
        'balance_sheet': {
            'Cash & Equivalents': {'TTM': 10000},
            'Net Loans': {'TTM': 100000},
            'Gross Loans': {'TTM': 100000}
        },
        'ratios': {
            'CET1 Ratio': {'TTM': 13.0},
            'Cost-to-Income Ratio': {'TTM': 40.0},
            'Return on Equity (ROE)': {'TTM': 14.0},
            'Payout Ratio': {'TTM': 72.0},
            'LVR': {'TTM': 45.0}
        }
    }

    result = calculate_banks_score(perfect_data)
    print(f"Total Score: {result['total_score']}")
    print(f"LVR Penalty: {result['lvr_penalty']}")
    for metric, info in result['metrics'].items():
        print(f"  {metric}: {info['value']} -> {info['score']} ({info['level']})")
