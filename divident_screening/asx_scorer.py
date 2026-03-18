#!/usr/bin/env python3
"""
ASX Stock Scoring System - 12刀打分体系
生成带雷达图的HTML报告
"""

import json
import argparse
import logging
import pprint
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


# ============== Normalization Functions ==============

def normalize_positive(value: float, warn: float, target: float) -> float:
    """
    正向指标评分函数 (越大越好).

    得分 = (实际值 - 预警值) / (目标值 - 预警值) × 10
    - 超过目标值 → 10 分
    - 低于预警值 → 0 分
    """
    if value >= target:
        return 10.0
    if value <= warn:
        return 0.0
    return (value - warn) / (target - warn) * 10


def normalize_negative(value: float, warn: float, target: float) -> float:
    """
    逆向指标评分函数 (越小越好).

    得分 = (预警值 - 实际值) / (预警值 - 目标值) × 10
    - 低于目标值 → 10 分
    - 超过预警值 → 0 分
    """
    if value <= target:
        return 10.0
    if value >= warn:
        return 0.0
    return (warn - value) / (warn - target) * 10


def normalize_range(value: float, warn_low: float, target_low: float,
                   target_high: float, warn_high: float) -> float:
    """
    趋中指标评分函数 (中间最优).

    目标值区间内 → 10 分
    预警边界 → 0 分
    """
    # 如果在目标区间内，得满分
    if target_low <= value <= target_high:
        return 10.0
    # 如果低于低预警线
    if value <= warn_low:
        return 0.0
    # 如果高于高预警线
    if value >= warn_high:
        return 0.0
    # 在低预警线和目标低值之间
    if value < target_low:
        return (value - warn_low) / (target_low - warn_low) * 10
    # 在目标高值和高预警线之间
    if value > target_high:
        return (warn_high - value) / (warn_high - target_high) * 10
    return 0.0


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
        self.ratios = data.get('ratios', {})
        self.income = data.get('income_statement', {})
        self.balance = data.get('balance_sheet', {})
        self.cash_flow = data.get('cash_flow', {})
        self.ttm = self._get_latest_data()

    def _get_latest_data(self) -> Dict[str, Any]:
        result = {}
        for source in [self.ratios, self.income, self.balance, self.cash_flow]:
            for key, value in source.items():
                if isinstance(value, dict):
                    # 优先级: TTM > Current > FY 2025 > Annual Report
                    if 'TTM' in value:
                        result[key] = value['TTM']
                    elif 'Current' in value:
                        result[key] = value['Current']
                    elif 'FY 2025' in value:
                        result[key] = value['FY 2025']
                    elif 'Annual Report 2025' in value:
                        result[key] = value['Annual Report 2025']
        return result

    def _get_value(self, *keys: str) -> Optional[float]:
        for key in keys:
            if key in self.ttm:
                val = self.ttm[key]
                if isinstance(val, (int, float)):
                    # print(f"[DEBUG] Found {key}: {val}")
                    return float(val)
            # else:
            #     print(f"[DEBUG] Not found: {key}")
        return None

    def _check_range(self, value: float, min_val: float, max_val: float) -> float:
        if value < min_val:
            return max(0, 1 - (min_val - value) / min_val)
        elif value > max_val:
            return max(0, 1 - (value - max_val) / max_val)
        return 1.0

    def score_banks(self) -> ScoreResult:
        """银行六维度量化模型 - 根据 score_system.md 重构"""
        result = ScoreResult(ticker=self.ticker, industry="Banks")
        result.log(f"Starting banks scoring for {self.ticker}")

        # ===== 1. NIM (净息差) - 1.8%-2.1% =====
        # 计算 NIM = Net Interest Income / IEA
        # 公式: IEA = Cash & Equivalents + Investment Securities + Trading Asset Securities + Net Loans
        net_interest_income = self._get_value('Net Interest Income')
        result.log(f"NIM - Net Interest Income: {net_interest_income}")

        # 计算完整的生息资产 (IEA)
        cash = self._get_value('Cash & Equivalents')
        investment_securities = self._get_value('Investment Securities')
        trading_securities = self._get_value('Trading Asset Securities')
        net_loans = self._get_value('Net Loans')

        result.log(f"NIM - Cash: {cash}, Investment: {investment_securities}, Trading: {trading_securities}, Net Loans: {net_loans}")

        interest_earnings = 0
        if cash:
            interest_earnings += cash
        if investment_securities:
            interest_earnings += investment_securities
        if trading_securities:
            interest_earnings += trading_securities
        if net_loans:
            interest_earnings += net_loans

        if interest_earnings == 0:
            # Fallback: 使用 Gross Loans
            interest_earnings = self._get_value('Gross Loans')
            result.log(f"NIM - Fallback to Gross Loans: {interest_earnings}")

        result.log(f"NIM - Total IEA: {interest_earnings}")

        nim = None
        if net_interest_income and interest_earnings and interest_earnings > 0:
            nim = (net_interest_income / interest_earnings) * 100
            result.log(f"NIM - Calculated: {nim:.2f}%")

        if nim:
            score = self._check_range(nim, 1.8, 2.1) * 10
            result.details.append({
                'metric': 'NIM (净息差)',
                'value': f"{nim:.2f}%",
                'score': score,
                'max': 10,
                'unit': '%',
                'benchmark': '1.8%-2.1%',
                'description': '银行贷出去的款收到的利息与吸收存款付出利息的差额。相当于银行的"毛利率"，越高说明银行赚钱能力越强。'
            })
            if 1.8 <= nim <= 2.1:
                result.passed_checks.append('NIM')
                result.log(f"NIM - PASSED (score: {score})")
        else:
            result.log(f"NIM - NOT CALCULATED (NII: {net_interest_income}, IEA: {interest_earnings})")

        # ===== 2. CET1 Ratio (一级资本充足率) - >11.5% =====
        # 公式: CET1 Ratio = Common Equity Tier 1 Capital / Risk Weighted Assets
        cet1 = self._get_value('CET1 Ratio', 'Common Equity Tier 1 Ratio')
        result.log(f"CET1 - Direct value: {cet1}")

        # 尝试通过 RWA 计算 (优先使用 AI 补充的 RWA 数据)
        if not cet1:
            common_equity = self._get_value('Total Common Equity', 'Shareholders Equity')
            rwa = self._get_value('Risk Weighted Assets')
            if common_equity and rwa and rwa > 0:
                cet1 = (common_equity / rwa) * 100
                result.log(f"CET1 - Calculated via Equity/RWA: {cet1:.2f}%")

        # Fallback: 通过 Total Common Equity / Total Assets 计算 (代理 >5%)
        if not cet1:
            common_equity = self._get_value('Total Common Equity', 'Shareholders Equity')
            total_assets = self._get_value('Total Assets')
            if common_equity and total_assets and total_assets > 0:
                cet1 = (common_equity / total_assets) * 100
                result.log(f"CET1 - Calculated via Equity/Assets (proxy): {cet1:.2f}%")

        if cet1:
            score = min(1, cet1 / 11.5) * 10
            result.details.append({
                'metric': 'CET1 Ratio (资本充足率)',
                'value': f"{cet1:.2f}%",
                'score': score,
                'max': 10,
                'unit': '%',
                'benchmark': '>11.5%',
                'description': '银行的"安全垫"。相当于银行为应对贷款损失预留的本钱，越高越安全，金融危机时越不容易倒闭。'
            })
            if cet1 > 11.5:
                result.passed_checks.append('CET1')
                result.log(f"CET1 - PASSED (score: {score})")

        # ===== 3. Cost-to-Income Ratio (成本收入比) - <45% =====
        # 公式: Cost-to-Income = Total Non-Interest Expense / Revenues Before Loan Losses * 100
        total_expense = self._get_value('Total Non-Interest Expense', 'Operating Expenses', 'Cost of Operations')
        revenue = self._get_value('Revenues Before Loan Losses', 'Total Income', 'Revenue', 'Total Revenue', 'Operating Revenue')
        result.log(f"Cost-to-Income - Expense: {total_expense}, Revenue (Revenues Before Loan Losses): {revenue}")

        cost_income = None
        if total_expense and revenue and revenue > 0:
            cost_income = (total_expense / revenue) * 100
            result.log(f"Cost-to-Income - Calculated: {cost_income:.2f}%")

        if cost_income:
            # 越低越好
            score = max(0, (45 - cost_income) / 45) * 10 if cost_income <= 45 else 0
            result.details.append({
                'metric': 'Cost-to-Income (成本收入比)',
                'value': f"{cost_income:.2f}%",
                'score': score,
                'max': 10,
                'unit': '%',
                'benchmark': '<45%',
                'description': '银行运营效率指标。相当于"每赚100块要花多少钱"，越低说明银行成本控制越好，越赚钱。'
            })
            if cost_income < 45:
                result.passed_checks.append('Cost-to-Income')

        # ===== 4. ROE (净资产收益率) - 11%-13% =====
        roe = self._get_value('Return on Equity (ROE)', 'ROE')
        if roe:
            score = self._check_range(roe, 11, 13) * 10
            result.details.append({
                'metric': 'ROE (净资产收益率)',
                'value': f"{roe:.2f}%",
                'score': score,
                'max': 10,
                'unit': '%',
                'benchmark': '11%-13%',
                'description': '银行用股东的钱赚钱的效率。相当于"股东投入100块能赚多少"，越高说明银行盈利能力越强。'
            })
            if 11 <= roe <= 13:
                result.passed_checks.append('ROE')

        # ===== 5. Bad Debt / Gross Loans (不良贷款率) - <0.15% =====
        # 公式: Credit Risk Metric = Provision for Loan Losses / Gross Loans * 100
        provision = self._get_value('Provision for Loan Losses', 'Loan Loss Provision', 'Credit Loss Provision')
        gross_loans = self._get_value('Gross Loans')
        result.log(f"Bad Debt - Provision: {provision}, Gross Loans: {gross_loans}")

        bad_debt_ratio = None
        if provision and gross_loans and gross_loans > 0:
            bad_debt_ratio = (provision / gross_loans) * 100
            result.log(f"Bad Debt Ratio - Calculated: {bad_debt_ratio:.3f}%")

        if bad_debt_ratio:
            score = max(0, (0.15 - bad_debt_ratio) / 0.15) * 10 if bad_debt_ratio <= 0.15 else 0
            result.details.append({
                'metric': 'Bad Debt Ratio (不良贷款率)',
                'value': f"{bad_debt_ratio:.3f}%",
                'score': score,
                'max': 10,
                'unit': '%',
                'benchmark': '<0.15%',
                'description': '银行借出去的钱收不回来的比例。相当于"坏账率"，越低说明风控越好，资产质量越高。'
            })
            if bad_debt_ratio < 0.15:
                result.passed_checks.append('Bad Debt Ratio')

        # ===== 6. Payout Ratio (股息支付率) - 70%-80% =====
        payout = self._get_value('Payout Ratio')
        if payout:
            score = self._check_range(payout, 70, 80) * 10
            result.details.append({
                'metric': 'Payout Ratio (股息支付率)',
                'value': f"{payout:.2f}%",
                'score': score,
                'max': 10,
                'unit': '%',
                'benchmark': '70%-80%',
                'description': '银行把利润分给股东的比例。相当于"慷慨度"，70%-80%表示既给股东高分红，又留20%用于发展。'
            })
            if 70 <= payout <= 80:
                result.passed_checks.append('Payout')

        result.total_score = sum(d['score'] for d in result.details)
        result.max_score = 60
        return result

    def score_materials(self) -> ScoreResult:
        """矿企六维度量化模型 - 根据 score_normalisation.md 标准化评分

        根据设计文档:
        - AISC (运营成本率): 逆向, warn=85%, target=60%, 权重=25%
        - CIP (在建工程增速): 正向, warn=0%, target=30%, 权重=15%
        - Underlying NPAT: 正向, warn=减值>20%, target=无减值, 权重=15%
        - FCF Yield: 正向, warn=0%, target=8%, 权重=20%
        - Net Debt/EBITDA: 逆向, warn=1.5x, target=0.5x, 权重=15%
        - Dividend Payout: 正向, warn=40%, target=60%, 权重=10%
        """
        result = ScoreResult(ticker=self.ticker, industry="Materials")

        # ===== 1. AISC (运营成本率) - 逆向指标 =====
        # 预警线: 85%, 目标值: 60%, 权重: 25%
        revenue = self._get_value('Revenue', 'Total Revenue')
        cost_revenue = self._get_value('Cost of Revenue', 'Cost of Goods Sold')
        capex = self._get_value('Capital Expenditures', 'CapEx', 'Sustaining Capex')

        aisc = None
        if revenue and cost_revenue and revenue > 0:
            # AISC = (Cost + Capex) / Revenue * 100 (运营成本率，越低越好)
            total_cost = cost_revenue + abs(capex) if capex else cost_revenue
            aisc = (total_cost / revenue) * 100

        if aisc:
            score = normalize_negative(aisc, warn=85, target=60)
            result.details.append({
                'metric': 'AISC (运营成本率)',
                'value': f"{aisc:.2f}%",
                'score': score,
                'max': 10,
                'unit': '%',
                'benchmark': '60%-85%',
                'description': '矿企的全成本指标。相当于"挖矿成本占收入比例"，60%为优秀(赚40%)，85%为预警(赚15%)。',
                'weight': 0.25
            })
            result.log(f"AISC: {aisc:.2f}%, Score: {score:.2f}")
            if aisc <= 85:
                result.passed_checks.append('AISC')

        # ===== 2. CIP (在建工程增速) - 正向指标 =====
        # 预警线: 0%, 目标值: 30%, 权重: 15%
        prod_growth = self._get_value('Revenue Growth (YoY)', 'Revenue Growth')

        if prod_growth is not None:
            score = normalize_positive(prod_growth, warn=0, target=30)
            result.details.append({
                'metric': 'CIP (在建工程增速)',
                'value': f"{prod_growth:.2f}%",
                'score': score,
                'max': 10,
                'unit': '%',
                'benchmark': '0%-30%',
                'description': '矿企的扩张能力。相当于"产量增长"，30%为优秀(高速扩张)，0%为预警(停滞)。',
                'weight': 0.15
            })
            result.log(f"CIP/Growth: {prod_growth:.2f}%, Score: {score:.2f}")
            if prod_growth > 0:
                result.passed_checks.append('CIP')

        # ===== 3. Underlying NPAT (核心净利润) - 正向指标 =====
        # 预警线: 减值>20%, 目标值: 无减值, 权重: 15%
        net_income = self._get_value('Net Income', 'Net Income to Common')
        asset_writedown = self._get_value('Asset Writedown', 'Impairment of Assets')

        underlying_npat = net_income
        writedown_ratio = 0
        if asset_writedown and net_income and net_income > 0:
            # 减值率 = abs(Asset Writedown) / Net Income
            writedown_ratio = abs(asset_writedown) / net_income * 100
            # Underlying NPAT = Net Income - Asset Writedown (writedown is negative)
            underlying_npat = net_income - asset_writedown

        if underlying_npat is not None:
            # 如果没有减值，得10分；如果减值率>20%，得0分
            score = normalize_positive(100 - writedown_ratio, warn=80, target=100)
            result.details.append({
                'metric': 'Underlying NPAT (核心净利润)',
                'value': f"${underlying_npat:.0f}M",
                'score': score,
                'max': 10,
                'unit': '$M',
                'benchmark': '无减值',
                'description': '剔除资产减值后的真实利润。相当于"卖矿真赚了多少钱"，无减值为优秀。',
                'weight': 0.15
            })
            result.log(f"Underlying NPAT: {underlying_npat:.0f}, Writedown: {writedown_ratio:.2f}%, Score: {score:.2f}")
            if writedown_ratio < 20:
                result.passed_checks.append('Underlying NPAT')

        # ===== 4. FCF Yield - 正向指标 =====
        # 预警线: 0%, 目标值: 8%, 权重: 20%
        fcf_yield = self._get_value('FCF Yield', 'Free Cash Flow Yield')
        if not fcf_yield:
            # 尝试计算: FCF / Market Cap
            fcf = self._get_value('Free Cash Flow')
            market_cap = self._get_value('Market Capitalization')
            if fcf and market_cap and market_cap > 0:
                fcf_yield = (fcf / market_cap) * 100

        if fcf_yield:
            score = normalize_positive(fcf_yield, warn=0, target=8)
            result.details.append({
                'metric': 'FCF Yield (自由现金流收益率)',
                'value': f"{fcf_yield:.2f}%",
                'score': score,
                'max': 10,
                'unit': '%',
                'benchmark': '0%-8%',
                'description': '矿企真金白银赚到的现金收益率。相当于"牛市含金量"，8%为优秀。',
                'weight': 0.20
            })
            result.log(f"FCF Yield: {fcf_yield:.2f}%, Score: {score:.2f}")
            if fcf_yield > 0:
                result.passed_checks.append('FCF Yield')

        # ===== 5. Net Debt/EBITDA - 逆向指标 =====
        # 预警线: 1.5x, 目标值: 0.5x, 权重: 15%
        net_debt_ebitda = self._get_value('Net Debt / EBITDA Ratio')
        if not net_debt_ebitda:
            # 尝试计算: (Total Debt - Cash) / EBITDA
            total_debt = self._get_value('Total Debt')
            cash = self._get_value('Cash & Equivalents')
            ebitda = self._get_value('EBITDA')
            if total_debt and cash is not None and ebitda and ebitda > 0:
                net_debt_ebitda = (total_debt - cash) / ebitda

        if net_debt_ebitda:
            score = normalize_negative(net_debt_ebitda, warn=1.5, target=0.5)
            result.details.append({
                'metric': 'Net Debt/EBITDA (净杠杆率)',
                'value': f"{net_debt_ebitda:.2f}x",
                'score': score,
                'max': 10,
                'unit': 'x',
                'benchmark': '0.5x-1.5x',
                'description': '矿企债务压力。相当于"几年能还清债务"，0.5x为优秀，1.5x为预警。',
                'weight': 0.15
            })
            result.log(f"Net Debt/EBITDA: {net_debt_ebitda:.2f}x, Score: {score:.2f}")
            if net_debt_ebitda < 1.5:
                result.passed_checks.append('Net Debt/EBITDA')

        # ===== 6. Dividend Payout - 正向指标 =====
        # 预警线: 40%, 目标值: 60%, 权重: 10%
        payout = self._get_value('Payout Ratio')
        if not payout:
            # 尝试计算: Dividends / Net Income
            dividends = self._get_value('Common Dividends Paid')
            net_income = self._get_value('Net Income to Common')
            if dividends and net_income and net_income > 0:
                payout = (abs(dividends) / net_income) * 100

        if payout:
            score = normalize_positive(payout, warn=40, target=60)
            result.details.append({
                'metric': 'Dividend Payout (分红率)',
                'value': f"{payout:.2f}%",
                'score': score,
                'max': 10,
                'unit': '%',
                'benchmark': '40%-60%',
                'description': '矿企派息比例。相当于"现金奶牛"程度，60%为优秀。',
                'weight': 0.10
            })
            result.log(f"Dividend Payout: {payout:.2f}%, Score: {score:.2f}")
            if payout >= 40:
                result.passed_checks.append('Dividend Payout')

        # 计算总分 (加权)
        total_weight = 0
        weighted_score = 0
        for d in result.details:
            weight = d.get('weight', 0)
            total_weight += weight
            weighted_score += d['score'] * weight

        # 归一化到 0-10 分
        if total_weight > 0:
            result.total_score = (weighted_score / total_weight)
        else:
            result.total_score = sum(d['score'] for d in result.details)

        result.max_score = 10
        return result

    def score_infrastructure(self) -> ScoreResult:
        """基建六维度量化模型 - 使用标准化评分 (0-10分制)

        根据 score_normalisation.md 设计:
        - EBITDA Margin: 正向, warn=45%, target=65%
        - Cash Conversion: 正向, warn=50%, target=95%
        - Interest Cover: 正向, warn=1.5x, target=4.0x
        - EV/EBITDA: 逆向, warn=18x, target=10x
        - CPI Linkage: 正向, warn=50%, target=100%
        - WACE: 正向, warn=5年, target=20年
        """
        result = ScoreResult(ticker=self.ticker, industry="Infrastructure")

        # ===== 1. EBITDA Margin (运营利润率) - 正向指标 =====
        # 权重: 15%, 预警线: 45%, 目标: 65%
        ebitda_margin = self._get_value('EBITDA Margin')
        if ebitda_margin:
            score = normalize_positive(ebitda_margin, warn=45, target=65)
            result.details.append({
                'metric': 'EBITDA Margin (运营利润率)',
                'value': f"{ebitda_margin:.2f}%",
                'score': score,
                'max': 10,
                'weight': 0.15,
                'unit': '%',
                'benchmark': '45%-65%',
                'description': '基建股的"毛利率"。相当于"收租毛利率"，45%-65%是合理区间。'
            })
            if score >= 7:  # 70%以上为通过
                result.passed_checks.append('EBITDA Margin')

        # ===== 2. Cash Conversion (现金转化率) - 正向指标 =====
        # 权重: 15%, 预警线: 50%, 目标: 95%
        # 公式: Cash Conversion = Operating Cash Flow / EBITDA * 100
        ocf = self._get_value('Operating Cash Flow')
        ebitda = self._get_value('EBITDA')
        result.log(f"Cash Conv - OCF: {ocf}, EBITDA: {ebitda}")

        if ocf and ebitda and ebitda != 0:
            cash_conv = (ocf / ebitda) * 100
            score = normalize_positive(cash_conv, warn=50, target=95)
            result.details.append({
                'metric': 'Cash Conversion (现金转化率)',
                'value': f"{cash_conv:.2f}%",
                'score': score,
                'max': 10,
                'weight': 0.15,
                'unit': '%',
                'benchmark': '50%-95%',
                'description': '利润变成真钱的能力。相当于"到账率"，50%-95%是合理区间。'
            })
            if score >= 7:
                result.passed_checks.append('Cash Conv')

        # ===== 3. Interest Cover Ratio (利息覆盖率) - 正向指标 =====
        # 权重: 25%, 预警线: 1.5x, 目标: 4.0x
        # 公式: Interest Cover = EBIT / Interest Expense
        interest_cov = self._get_value('Interest Coverage Ratio')
        if not interest_cov:
            # 尝试从组件计算
            ebit = self._get_value('EBIT', 'Operating Income')
            interest_expense = self._get_value('Interest Expense')
            if ebit and interest_expense and interest_expense > 0:
                interest_cov = ebit / interest_expense

        if interest_cov:
            score = normalize_positive(interest_cov, warn=1.5, target=4.0)
            result.details.append({
                'metric': 'Interest Cover (利息覆盖率)',
                'value': f"{interest_cov:.2f}x",
                'score': score,
                'max': 10,
                'weight': 0.25,
                'unit': 'x',
                'benchmark': '1.5x-4.0x',
                'description': '基建的安全带。相当于"赚的钱够还几次利息"，1.5x-4.0x是合理区间。'
            })
            if score >= 7:
                result.passed_checks.append('Interest Cover')

        # ===== 4. EV/EBITDA (企业价值倍数) - 逆向指标 =====
        # 权重: 15%, 预警线: 18x, 目标: 10x (越低越好)
        ev_ebitda = self._get_value('EV/EBITDA Ratio', 'EV / EBITDA Ratio')
        if not ev_ebitda:
            # 尝试从组件计算: (Market Cap + Debt - Cash) / EBITDA
            market_cap = self._get_value('Market Capitalization')
            total_debt = self._get_value('Total Debt')
            cash = self._get_value('Cash & Equivalents')
            if market_cap and total_debt and ebitda and ebitda > 0:
                ev_ebitda = (market_cap + total_debt - (cash or 0)) / ebitda

        if ev_ebitda:
            score = normalize_negative(ev_ebitda, warn=18, target=10)
            result.details.append({
                'metric': 'EV/EBITDA (企业价值倍数)',
                'value': f"{ev_ebitda:.2f}x",
                'score': score,
                'max': 10,
                'weight': 0.15,
                'unit': 'x',
                'benchmark': '10x-18x',
                'description': '基建估值指标。相当于"买下公司几年能回本"，10x-18x是合理区间。'
            })
            if score >= 7:
                result.passed_checks.append('EV/EBITDA')

        # ===== 5. CPI Linkage (CPI挂钩率) - 正向指标 =====
        # 权重: 15%, 预警线: 50%, 目标: 100%
        # 衡量收入与通胀挂钩的比例
        cpi_linkage = self._get_value('CPI Linkage', 'CPI Linkage %')
        if cpi_linkage:
            score = normalize_positive(cpi_linkage, warn=50, target=100)
            result.details.append({
                'metric': 'CPI Linkage (抗通胀能力)',
                'value': f"{cpi_linkage:.2f}%",
                'score': score,
                'max': 10,
                'weight': 0.15,
                'unit': '%',
                'benchmark': '50%-100%',
                'description': '收入与通胀挂钩的比例。50%-100%说明有良好的通胀保护。'
            })
            if score >= 7:
                result.passed_checks.append('CPI Linkage')

        # ===== 6. WACE (加权平均合同到期年限) - 正向指标 =====
        # 权重: 15%, 预警线: 5年, 目标: 20年
        wace = self._get_value('WACE', 'Weighted Average Contract Expiry', 'Contract Expiry (Years)')
        if wace:
            score = normalize_positive(wace, warn=5, target=20)
            result.details.append({
                'metric': 'WACE (合同稳定性)',
                'value': f"{wace:.1f} 年",
                'score': score,
                'max': 10,
                'weight': 0.15,
                'unit': 'years',
                'benchmark': '5-20年',
                'description': '加权平均合同到期年限。5-20年说明收入稳定性好。'
            })
            if score >= 7:
                result.passed_checks.append('WACE')

        # 计算总分 (加权)
        total_weight = 0
        weighted_score = 0
        for d in result.details:
            weight = d.get('weight', 0)
            total_weight += weight
            weighted_score += d['score'] * weight

        # 归一化到 0-10 分
        if total_weight > 0:
            result.total_score = (weighted_score / total_weight)
        else:
            result.total_score = sum(d['score'] for d in result.details)

        result.max_score = 10
        return result

    def score_healthcare(self) -> ScoreResult:
        result = ScoreResult(ticker=self.ticker, industry="Healthcare")

        # EBITDA Margin - > 25%
        ebitda_margin = self._get_value('EBITDA Margin')
        if ebitda_margin:
            score = min(1, ebitda_margin / 25) * 10
            result.details.append({'metric': 'EBITDA Margin', 'value': ebitda_margin, 'score': score, 'max': 10, 'unit': '%', 'benchmark': '>25%'})
            if ebitda_margin >= 25:
                result.passed_checks.append('EBITDA Margin')

        # ROE - > 15%
        roe = self._get_value('Return on Equity (ROE)', 'ROE')
        if roe:
            score = min(1, roe / 15) * 10
            result.details.append({'metric': 'ROE', 'value': roe, 'score': score, 'max': 10, 'unit': '%', 'benchmark': '>15%'})
            if roe >= 15:
                result.passed_checks.append('ROE')

        # FCF Yield - > 2%
        fcf_yield = self._get_value('FCF Yield')
        if fcf_yield:
            score = max(0, min(1, fcf_yield / 2)) * 10
            result.details.append({'metric': 'FCF Yield', 'value': f"{fcf_yield:.2f}%", 'score': score, 'max': 10, 'unit': '%', 'benchmark': '>2%'})
            if fcf_yield >= 2:
                result.passed_checks.append('FCF Yield')

        # Net Debt/EBITDA - < 2.5
        net_debt_ebitda = self._get_value('Net Debt / EBITDA Ratio')
        if net_debt_ebitda:
            score = max(0, (2.5 - net_debt_ebitda) / 2.5) * 10
            result.details.append({'metric': 'Net Debt/EBITDA', 'value': net_debt_ebitda, 'score': score, 'max': 10, 'unit': 'x', 'benchmark': '<2.5x'})
            if net_debt_ebitda <= 2.5:
                result.passed_checks.append('Net Debt/EBITDA')

        # Dividend Policy - 40% - 70%
        payout = self._get_value('Payout Ratio')
        if payout:
            score = self._check_range(payout, 40, 70) * 10
            result.details.append({'metric': 'Dividend Policy', 'value': payout, 'score': score, 'max': 10, 'unit': '%', 'benchmark': '40%-70%'})
            if 40 <= payout <= 70:
                result.passed_checks.append('Dividend Policy')

        # EV/EBITDA - 10x - 20x
        ev_ebitda = self._get_value('EV / EBITDA Ratio')
        if ev_ebitda:
            score = self._check_range(ev_ebitda, 10, 20) * 10
            result.details.append({'metric': 'EV/EBITDA', 'value': ev_ebitda, 'score': score, 'max': 10, 'unit': 'x', 'benchmark': '10-20x'})
            if 10 <= ev_ebitda <= 20:
                result.passed_checks.append('EV/EBITDA')

        result.total_score = sum(d['score'] for d in result.details)
        result.max_score = 60
        return result

    def score_telecom(self) -> ScoreResult:
        result = ScoreResult(ticker=self.ticker, industry="Telecom")

        # EBITDA Margin - > 35%
        ebitda_margin = self._get_value('EBITDA Margin')
        if ebitda_margin:
            score = min(1, ebitda_margin / 35) * 10
            result.details.append({'metric': 'EBITDA Margin', 'value': ebitda_margin, 'score': score, 'max': 10, 'unit': '%', 'benchmark': '>35%'})
            if ebitda_margin >= 35:
                result.passed_checks.append('EBITDA Margin')

        # FCF Yield - > 5%
        fcf_yield = self._get_value('FCF Yield')
        if fcf_yield:
            score = max(0, min(1, fcf_yield / 5)) * 10
            result.details.append({'metric': 'FCF Yield', 'value': f"{fcf_yield:.2f}%", 'score': score, 'max': 10, 'unit': '%', 'benchmark': '>5%'})
            if fcf_yield >= 5:
                result.passed_checks.append('FCF Yield')

        # Net Debt/EBITDA - < 2.5
        net_debt_ebitda = self._get_value('Net Debt / EBITDA Ratio')
        if net_debt_ebitda:
            score = max(0, (2.5 - net_debt_ebitda) / 2.5) * 10
            result.details.append({'metric': 'Net Debt/EBITDA', 'value': net_debt_ebitda, 'score': score, 'max': 10, 'unit': 'x', 'benchmark': '<2.5x'})
            if net_debt_ebitda <= 2.5:
                result.passed_checks.append('Net Debt/EBITDA')

        # Dividend Policy - 60% - 90%
        payout = self._get_value('Payout Ratio')
        if payout:
            score = self._check_range(payout, 60, 90) * 10
            result.details.append({'metric': 'Dividend Policy', 'value': payout, 'score': score, 'max': 10, 'unit': '%', 'benchmark': '60%-90%'})
            if 60 <= payout <= 90:
                result.passed_checks.append('Dividend Policy')

        # EV/EBITDA - 6x - 10x
        ev_ebitda = self._get_value('EV / EBITDA Ratio')
        if ev_ebitda:
            score = self._check_range(ev_ebitda, 6, 10) * 10
            result.details.append({'metric': 'EV/EBITDA', 'value': ev_ebitda, 'score': score, 'max': 10, 'unit': 'x', 'benchmark': '6-10x'})
            if 6 <= ev_ebitda <= 10:
                result.passed_checks.append('EV/EBITDA')

        # Current Ratio - > 0.8
        current_ratio = self._get_value('Current Ratio')
        if current_ratio:
            score = min(1, current_ratio / 0.8) * 10
            result.details.append({'metric': 'Current Ratio', 'value': current_ratio, 'score': score, 'max': 10, 'unit': 'x', 'benchmark': '>0.8x'})
            if current_ratio >= 0.8:
                result.passed_checks.append('Current Ratio')

        result.total_score = sum(d['score'] for d in result.details)
        result.max_score = 60
        return result

    def score_consumer_staples(self) -> ScoreResult:
        """
        必需消费六维度量化模型 - 根据 score_normalisation.md 重构

        指标定义:
        | 维度 | 指标 | 权重 | 预警线 (0分) | 目标值 (10分) | 极性 |
        |------|------|------|--------------|---------------|------|
        | 地位 | Market Share (趋势) | 15% | 下滑 | 增长 | 正向 |
        | 盈利 | EBIT Margin | 20% | 4% | 9% | 正向 |
        | 效率 | ROE | 20% | 15% | 35% | 正向 |
        | 生死线 | Inventory Days | 20% | 100天 | 30天 | 逆向 |
        | 税务 | Franking Credits | 10% | 0% | 100% | 正向 |
        | 价格 | Forward PE | 15% | 30x | 18x | 逆向 |
        """
        result = ScoreResult(ticker=self.ticker, industry="Consumer Staples")
        result.log(f"Starting consumer staples scoring for {self.ticker}")

        # ===== 1. Market Share (趋势) - 15% =====
        # 正向指标: 增长=10分, 下滑=0分
        market_share_change = self._get_value('Market Share Change', 'Market Share Growth')
        if market_share_change is not None:
            score = normalize_positive(market_share_change, warn=0, target=5)
            result.details.append({
                'metric': 'Market Share (趋势)',
                'value': f"{market_share_change:.1f}%",
                'score': score,
                'weight': 0.15,
                'max': 10,
                'unit': '%',
                'benchmark': '增长=10分, 下滑=0分',
                'description': '市场份额趋势。增长表示竞争力提升，下滑需警惕。'
            })
            if market_share_change > 0:
                result.passed_checks.append('Market Share')

        # ===== 2. EBIT Margin - 20% =====
        # 正向指标: 预警4%, 目标9%
        ebit_margin = self._get_value('EBIT Margin', 'Operating Margin')
        if ebit_margin:
            score = normalize_positive(ebit_margin, warn=4, target=9)
            result.details.append({
                'metric': 'EBIT Margin (息税前利润率)',
                'value': f"{ebit_margin:.2f}%",
                'score': score,
                'weight': 0.20,
                'max': 10,
                'unit': '%',
                'benchmark': '预警4%, 目标9%',
                'description': '零售业的"毛利率"。4%-9%区间，9%以上为优秀。'
            })
            if ebit_margin >= 9:
                result.passed_checks.append('EBIT Margin')

        # ===== 3. ROE - 20% =====
        # 正向指标: 预警15%, 目标35%
        roe = self._get_value('ROE', 'Return on Equity (ROE)')
        if roe:
            score = normalize_positive(roe, warn=15, target=35)
            result.details.append({
                'metric': 'ROE (净资产收益率)',
                'value': f"{roe:.2f}%",
                'score': score,
                'weight': 0.20,
                'max': 10,
                'unit': '%',
                'benchmark': '预警15%, 目标35%',
                'description': '股东投入的回报率。15%-35%区间，35%以上为优秀。'
            })
            if roe >= 35:
                result.passed_checks.append('ROE')

        # ===== 4. Inventory Days - 20% =====
        # 逆向指标: 预警100天, 目标30天
        # 公式: Inventory Days = (Inventory / Cost of Revenue) * 365
        inventory = self._get_value('Inventory', 'Inventories')
        cost_revenue = self._get_value('Cost of Revenue', 'Cost of Goods Sold')
        result.log(f"Inventory Days - Inventory: {inventory}, Cost: {cost_revenue}")

        inv_days = None
        if inventory and cost_revenue and cost_revenue > 0:
            inv_days = (inventory / cost_revenue) * 365
            result.log(f"Inventory Days - Calculated: {inv_days:.1f}")

        if inv_days:
            score = normalize_negative(inv_days, warn=100, target=30)
            result.details.append({
                'metric': 'Inventory Days (库存周转天数)',
                'value': f"{inv_days:.1f} 天",
                'score': score,
                'weight': 0.20,
                'max': 10,
                'unit': 'days',
                'benchmark': '预警100天, 目标30天',
                'description': '零售的生死线。30天以内为优秀，100天以上为风险。'
            })
            if inv_days <= 30:
                result.passed_checks.append('Inventory Days')

        # ===== 5. Franking Credits - 10% =====
        # 正向指标: 预警0%, 目标100%
        franking = self._get_value('Franking Credits', 'Imputation Credits', 'Tax Credit')
        if franking:
            score = normalize_positive(franking, warn=0, target=100)
            result.details.append({
                'metric': 'Franking Credits (税务抵扣)',
                'value': f"{franking:.0f}%",
                'score': score,
                'weight': 0.10,
                'max': 10,
                'unit': '%',
                'benchmark': '预警0%, 目标100%',
                'description': '澳大利亚税务抵扣。100%表示完全抵税。'
            })
            if franking >= 100:
                result.passed_checks.append('Franking')

        # ===== 6. Forward PE - 15% =====
        # 逆向指标: 预警30x, 目标18x (越低越好)
        fwd_pe = self._get_value('Forward PE')
        if fwd_pe:
            score = normalize_negative(fwd_pe, warn=30, target=18)
            result.details.append({
                'metric': 'Forward PE (远期市盈率)',
                'value': f"{fwd_pe:.2f}x",
                'score': score,
                'weight': 0.15,
                'max': 10,
                'unit': 'x',
                'benchmark': '预警30x, 目标18x',
                'description': '估值锚点。18x以下为低估，30x以上为高估。'
            })
            if fwd_pe <= 18:
                result.passed_checks.append('Forward PE')

        # 计算加权总分
        result.total_score = sum(d['score'] for d in result.details)
        result.max_score = 60
        return result

    def score_common_checks(self, result: ScoreResult) -> ScoreResult:
        # FCF Coverage
        fcf = self._get_value('Free Cash Flow')
        div_paid = self._get_value('Common Dividends Paid')
        if fcf and div_paid and div_paid > 0:
            fcf_coverage = fcf / abs(div_paid)
            score = 10 if fcf_coverage > 1.0 else 0
            result.details.append({'metric': 'FCF Coverage', 'value': f"{fcf_coverage:.2f}x", 'score': score, 'max': 10, 'unit': 'x', 'benchmark': '>1.0x', 'is_common': True})
            if fcf_coverage > 1.0:
                result.passed_checks.append('FCF Coverage')
            result.max_score += 10
            result.total_score += score

        # Interest Cover
        interest_cov = self._get_value('Interest Coverage Ratio')
        if interest_cov:
            score = 10 if interest_cov > 3.0 else 0
            result.details.append({'metric': 'Interest Cover', 'value': interest_cov, 'score': score, 'max': 10, 'unit': 'x', 'benchmark': '>3.0x', 'is_common': True})
            if interest_cov > 3.0:
                result.passed_checks.append('Interest Cover')
            result.max_score += 10
            result.total_score += score

        return result

    def score(self, industry: str) -> ScoreResult:
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
            result = self.score_healthcare()
        elif 'tele' in industry or '通信' in industry:
            result = self.score_telecom()
        else:
            raise ValueError(f"未知行业: {industry}")
        logging.info(f"Completed industry-specific scoring for {self.ticker} in {industry}")
        logging.debug(f"Industry-specific details: {pprint.pformat(result.details)}")
        return self.score_common_checks(result)


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
