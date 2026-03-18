"""
Banks Scorecard - Score Normalization Module

根据 score_normalisation.md 实现银行六维度量化评分
- NIM (净息差): 正向指标
- CET1 Ratio: 正向指标
- Cost-to-Income: 逆向指标
- ROE: 正向指标
- Bad Debt Ratio: 逆向指标
- Payout Ratio: 趋中指标 (50%-90% 区间内，75% 最优)
"""

from typing import Dict, Any, Optional


# ==================== 核心标准化公式 ====================

def normalize_positive(value: float, warn: float, target: float) -> float:
    """
    正向指标标准化 (越大越好)

    公式: score = (value - warn) / (target - warn) × 10

    边界处理:
    - 超过目标值 → 10 分
    - 低于预警值 → 0 分

    Args:
        value: 实际值
        warn: 预警线 (0分)
        target: 目标值 (10分)

    Returns:
        标准化分数 (0-10)
    """
    if value is None:
        return 0.0

    if value >= target:
        return 10.0
    elif value <= warn:
        return 0.0
    else:
        return (value - warn) / (target - warn) * 10


def normalize_negative(value: float, warn: float, target: float) -> float:
    """
    逆向指标标准化 (越小越好)

    公式: score = (warn - value) / (warn - target) × 10

    边界处理:
    - 低于目标值 → 10 分
    - 超过预警值 → 0 分

    Args:
        value: 实际值
        warn: 预警线 (0分)
        target: 目标值 (10分)

    Returns:
        标准化分数 (0-10)
    """
    if value is None:
        return 0.0

    if value <= target:
        return 10.0
    elif value >= warn:
        return 0.0
    else:
        return (warn - value) / (warn - target) * 10


def normalize_range(
    value: float,
    warn_low: float,
    target_low: float,
    target_high: float,
    warn_high: float
) -> float:
    """
    趋中指标标准化 (最优值在中间区间)

    公式:
    - 在目标区间内 → 10 分
    - 超过预警边界 → 0 分
    - 在区间之间 → 线性插值

    Args:
        value: 实际值
        warn_low: 低位预警线 (0分)
        target_low: 低位目标值 (10分)
        target_high: 高位目标值 (10分)
        warn_high: 高位预警线 (0分)

    Returns:
        标准化分数 (0-10)
    """
    if value is None:
        return 0.0

    # 在目标区间内 (最优)
    if target_low <= value <= target_high:
        return 10.0

    # 在低位预警和低位目标之间
    if value < target_low:
        if value <= warn_low:
            return 0.0
        else:
            return (value - warn_low) / (target_low - warn_low) * 10

    # 在高位目标和高位预警之间
    if value > target_high:
        if value >= warn_high:
            return 0.0
        else:
            return (warn_high - value) / (warn_high - target_high) * 10

    return 0.0


# ==================== 银行计分卡参数 ====================

# 指标定义: (权重, 预警线, 目标值, 极性)
BANKS_METRICS = {
    'NIM': {
        'weight': 0.20,
        'warn': 1.70,
        'target': 2.10,
        'polarity': 'positive',
        'display_name': 'NIM (净息差)',
        'unit': '%',
        'description': '银行贷出去的款收到的利息与吸收存款付出利息的差额'
    },
    'CET1': {
        'weight': 0.15,
        'warn': 11.0,
        'target': 13.0,
        'polarity': 'positive',
        'display_name': 'CET1 Ratio (一级资本充足率)',
        'unit': '%',
        'description': '银行为应对贷款损失预留的本钱，越高越安全'
    },
    'Cost-to-Income': {
        'weight': 0.15,
        'warn': 50.0,
        'target': 40.0,
        'polarity': 'negative',
        'display_name': 'Cost-to-Income (成本收入比)',
        'unit': '%',
        'description': '每赚100块要花多少钱，越低越好'
    },
    'ROE': {
        'weight': 0.20,
        'warn': 10.0,
        'target': 14.0,
        'polarity': 'positive',
        'display_name': 'ROE (净资产收益率)',
        'unit': '%',
        'description': '股东投入100块能赚多少，越高越好'
    },
    'Bad Debt': {
        'weight': 0.20,
        'warn': 0.15,
        'target': 0.05,
        'polarity': 'negative',
        'display_name': 'Bad Debt Ratio (不良贷款率)',
        'unit': '%',
        'description': '借出去的钱收不回来的比例，越低越好'
    },
    'Payout': {
        'weight': 0.10,
        'warn_low': 50.0,
        'target_low': 75.0,
        'target_high': 75.0,
        'warn_high': 90.0,
        'polarity': 'range',
        'display_name': 'Payout Ratio (股息支付率)',
        'unit': '%',
        'description': '把利润分给股东的比例，75%最优'
    }
}


def calculate_nim_score(nim: Optional[float]) -> float:
    """计算 NIM 分数"""
    return normalize_positive(nim, warn=1.70, target=2.10)


def calculate_cet1_score(cet1: Optional[float]) -> float:
    """计算 CET1 分数"""
    return normalize_positive(cet1, warn=11.0, target=13.0)


def calculate_cost_to_income_score(cti: Optional[float]) -> float:
    """计算 Cost-to-Income 分数"""
    return normalize_negative(cti, warn=50.0, target=40.0)


def calculate_roe_score(roe: Optional[float]) -> float:
    """计算 ROE 分数"""
    return normalize_positive(roe, warn=10.0, target=14.0)


def calculate_bad_debt_score(bad_debt: Optional[float]) -> float:
    """计算 Bad Debt 分数"""
    return normalize_negative(bad_debt, warn=0.15, target=0.05)


def calculate_payout_score(payout: Optional[float]) -> float:
    """计算 Payout 分数 (趋中指标)"""
    return normalize_range(
        payout,
        warn_low=50.0,
        target_low=75.0,
        target_high=75.0,
        warn_high=90.0
    )


def calculate_banks_score(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    计算银行综合评分

    Args:
        data: 包含财务数据的字典

    Returns:
        包含各项分数和总分的字典
    """
    # 提取数据
    ratios = data.get('ratios', {})
    income = data.get('income_statement', {})
    balance = data.get('balance_sheet', {})

    # 兼容不同数据格式
    def get_value(*keys):
        for key in keys:
            # 先检查 ratios
            if key in ratios:
                val = ratios[key]
                if isinstance(val, dict):
                    for period in ['TTM', 'Current', 'FY 2025', 'Annual Report 2025']:
                        if period in val:
                            return float(val[period])
                elif isinstance(val, (int, float)):
                    return float(val)
            # 再检查 income_statement
            if key in income:
                val = income[key]
                if isinstance(val, dict):
                    for period in ['TTM', 'Current', 'FY 2025', 'Annual Report 2025']:
                        if period in val:
                            return float(val[period])
                elif isinstance(val, (int, float)):
                    return float(val)
            # 最后检查 balance_sheet
            if key in balance:
                val = balance[key]
                if isinstance(val, dict):
                    for period in ['TTM', 'Current', 'FY 2025', 'Annual Report 2025']:
                        if period in val:
                            return float(val[period])
                elif isinstance(val, (int, float)):
                    return float(val)
        return None

    # 计算各指标分数
    nim = get_value('NIM', 'Net Interest Margin')
    cet1 = get_value('CET1 Ratio', 'Common Equity Tier 1 Ratio')
    cti = get_value('Cost-to-Income Ratio', 'Cost to Income Ratio')
    roe = get_value('ROE', 'Return on Equity (ROE)')
    bad_debt = get_value('Bad Debt Ratio', 'Non-Performing Loan Ratio', 'NPL Ratio')
    payout = get_value('Payout Ratio', 'Dividend Payout Ratio')

    scores = {
        'NIM': calculate_nim_score(nim),
        'CET1': calculate_cet1_score(cet1),
        'Cost-to-Income': calculate_cost_to_income_score(cti),
        'ROE': calculate_roe_score(roe),
        'Bad Debt': calculate_bad_debt_score(bad_debt),
        'Payout': calculate_payout_score(payout)
    }

    # 计算加权总分
    total_score = sum(
        scores[metric] * BANKS_METRICS[metric]['weight']
        for metric in BANKS_METRICS
    )

    return {
        'total_score': total_score,
        'max_score': 10.0,
        'metrics': {
            'NIM': {
                'value': nim,
                'score': scores['NIM'],
                **BANKS_METRICS['NIM']
            },
            'CET1': {
                'value': cet1,
                'score': scores['CET1'],
                **BANKS_METRICS['CET1']
            },
            'Cost-to-Income': {
                'value': cti,
                'score': scores['Cost-to-Income'],
                **BANKS_METRICS['Cost-to-Income']
            },
            'ROE': {
                'value': roe,
                'score': scores['ROE'],
                **BANKS_METRICS['ROE']
            },
            'Bad Debt': {
                'value': bad_debt,
                'score': scores['Bad Debt'],
                **BANKS_METRICS['Bad Debt']
            },
            'Payout': {
                'value': payout,
                'score': scores['Payout'],
                **BANKS_METRICS['Payout']
            }
        }
    }


# ==================== 测试入口 ====================

if __name__ == '__main__':
    # 简单测试
    print("=== 银行计分卡测试 ===")
    print(f"NIM @ 2.10 (目标): {calculate_nim_score(2.10)}")
    print(f"NIM @ 1.70 (预警): {calculate_nim_score(1.70)}")
    print(f"NIM @ 1.90 (中间): {calculate_nim_score(1.90)}")
    print(f"NIM @ 2.50 (超出): {calculate_nim_score(2.50)}")
    print(f"NIM @ 1.50 (低于): {calculate_nim_score(1.50)}")
    print()
    print(f"CTI @ 40% (目标): {calculate_cost_to_income_score(40.0)}")
    print(f"CTI @ 50% (预警): {calculate_cost_to_income_score(50.0)}")
    print(f"CTI @ 55% (超出): {calculate_cost_to_income_score(55.0)}")
    print()
    print(f"Payout @ 75% (最优): {calculate_payout_score(75.0)}")
    print(f"Payout @ 50% (低位): {calculate_payout_score(50.0)}")
    print(f"Payout @ 90% (高位): {calculate_payout_score(90.0)}")
    print()
    print("=== 全部满分测试 ===")
    # 全部满分
    test_data = {
        'ratios': {
            'NIM': {'FY 2025': 2.10},
            'CET1 Ratio': {'FY 2025': 13.0},
            'Cost-to-Income Ratio': {'FY 2025': 40.0},
            'ROE': {'FY 2025': 14.0},
            'Bad Debt Ratio': {'FY 2025': 0.05},
            'Payout Ratio': {'FY 2025': 75.0}
        }
    }
    result = calculate_banks_score(test_data)
    print(f"Total Score: {result['total_score']}")
    for metric, info in result['metrics'].items():
        print(f"  {metric}: {info['value']} -> {info['score']:.2f}")
