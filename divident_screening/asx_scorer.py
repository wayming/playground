#!/usr/bin/env python3
"""
ASX Stock Scoring System - 12刀打分体系
生成带雷达图的HTML报告
"""

import json
import argparse
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


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
        print(f"[DEBUG] {self.ticker}: {message}")


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
        # 由于数据中可能没有RWA，使用 Total Common Equity / Total Assets 作为代理 (>5%)
        cet1 = self._get_value('CET1 Ratio', 'Common Equity Tier 1 Ratio')
        result.log(f"CET1 - Direct value: {cet1}")

        # 尝试通过 Total Common Equity / Total Assets 计算
        if not cet1:
            common_equity = self._get_value('Total Common Equity', 'Shareholders Equity')
            total_assets = self._get_value('Total Assets')
            if common_equity and total_assets and total_assets > 0:
                cet1 = (common_equity / total_assets) * 100
                result.log(f"CET1 - Calculated via Equity/Assets: {cet1:.2f}%")

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
        """矿企六维度量化模型 - 根据 score_system.md 重构"""
        result = ScoreResult(ticker=self.ticker, industry="Materials")

        # ===== 1. Operating Cost Ratio (运营成本率) - 替代AISC =====
        # 公式: Operating Cost Ratio = Revenue / (Cost of Revenue + Sustaining Capex)
        revenue = self._get_value('Revenue', 'Total Revenue')
        cost_revenue = self._get_value('Cost of Revenue', 'Cost of Goods Sold')
        capex = self._get_value('Capital Expenditures', 'CapEx', 'Sustaining Capex')
        result.log(f"Materials - Revenue: {revenue}, Cost: {cost_revenue}, Capex: {capex}")

        if revenue and cost_revenue and capex:
            # 运营成本率越低越好
            operating_cost_ratio = revenue / (cost_revenue + capex) if (cost_revenue + capex) > 0 else 0
            # 比率应该越高越好(表示成本控制好)
            score = min(1, operating_cost_ratio / 1.5) * 10  # 假设1.5为基准
            result.details.append({
                'metric': 'Operating Cost Ratio (运营成本率)',
                'value': f"{operating_cost_ratio:.2f}x",
                'score': score,
                'max': 10,
                'unit': 'x',
                'benchmark': '>1.0x',
                'description': '矿企的成本控制能力。相当于"卖矿收入 vs 挖矿成本"，>1表示挖矿还能赚钱，即使矿价下跌也有安全边际。'
            })
            if operating_cost_ratio > 1.0:
                result.passed_checks.append('Operating Cost')

        # ===== 2. Production Guidance (产量指引) - Revenue Growth + 在建工程 =====
        # 观察 Revenue Growth (YoY) 与 Construction In Progress
        prod_growth = self._get_value('Revenue Growth (YoY)', 'Revenue Growth')
        const_in_progress = self._get_value('Construction In Progress', 'Capital Work in Progress')
        result.log(f"Production - Growth: {prod_growth}, Construction in Progress: {const_in_progress}")

        if prod_growth:
            score = max(0, min(1, prod_growth / 5)) * 10
            result.details.append({
                'metric': 'Revenue Growth (产量指引)',
                'value': f"{prod_growth:.2f}%",
                'score': score,
                'max': 10,
                'unit': '%',
                'benchmark': '>0%',
                'description': '矿企的收入增长。相当于"产量增长"，正增长说明有新矿投产或扩产，未来赚钱能力有保障。'
            })
            if prod_growth >= 0:
                result.passed_checks.append('Production Growth')

        # ===== 3. Underlying NPAT (核心净利润) =====
        # 公式: Underlying NPAT = Net Income - Asset Writedown (after tax)
        net_income = self._get_value('Net Income', 'Net Income to Common')
        asset_writedown = self._get_value('Asset Writedown', 'Impairment of Assets', 'Asset Impairment')
        result.log(f"Underlying NPAT - Net Income: {net_income}, Writedown: {asset_writedown}")

        underlying_npat = net_income
        if asset_writedown and net_income:
            # writedown 是负数，需要加回
            underlying_npat = net_income - asset_writedown  # asset_writedown 已经是负数

        if underlying_npat and underlying_npat > 0:
            score = 10
            result.details.append({
                'metric': 'Underlying NPAT (核心净利润)',
                'value': f"${underlying_npat:.0f}M",
                'score': score,
                'max': 10,
                'unit': '$M',
                'benchmark': '>0',
                'description': '剔除资产减值后的真实利润。相当于"卖矿真赚了多少钱"，排除了卖资产等一次性损失，更反映经营能力。'
            })
            result.passed_checks.append('Underlying NPAT')

        # ===== 4. FCF Yield - >8% =====
        fcf_yield = self._get_value('FCF Yield')
        if fcf_yield:
            score = min(1, fcf_yield / 8) * 10
            result.details.append({
                'metric': 'FCF Yield (自由现金流收益率)',
                'value': f"{fcf_yield:.2f}%",
                'score': score,
                'max': 10,
                'unit': '%',
                'benchmark': '>8%',
                'description': '矿企真金白银赚到的现金收益率。相当于"牛市含金量"，>8%表示每年赚的现金足以覆盖高分红和资本开支。'
            })
            if fcf_yield > 8:
                result.passed_checks.append('FCF Yield')

        # ===== 5. Net Debt/EBITDA - <1.0x =====
        net_debt_ebitda = self._get_value('Net Debt / EBITDA Ratio')
        if net_debt_ebitda:
            score = max(0, (1.0 - net_debt_ebitda) / 1.0) * 10
            result.details.append({
                'metric': 'Net Debt/EBITDA (净杠杆率)',
                'value': f"{net_debt_ebitda:.2f}x",
                'score': score,
                'max': 10,
                'unit': 'x',
                'benchmark': '<1.0x',
                'description': '矿企债务压力。相当于"几年能还清债务"，<1x说明即使不赚钱也能1年内还清，极端行情下也能活下来。'
            })
            if net_debt_ebitda < 1.0:
                result.passed_checks.append('Net Debt/EBITDA')

        # ===== 6. Dividend Policy - >50% =====
        payout = self._get_value('Payout Ratio')
        if payout:
            score = min(1, payout / 50) * 10
            result.details.append({
                'metric': 'Dividend Policy (分红政策)',
                'value': f"{payout:.2f}%",
                'score': score,
                'max': 10,
                'unit': '%',
                'benchmark': '>50%',
                'description': '矿企派息比例。相当于"现金奶牛"程度，>50%说明赚的钱一半以上分给股东，是矿业公司的核心竞争力。'
            })
            if payout > 50:
                result.passed_checks.append('Dividend Policy')

        result.total_score = sum(d['score'] for d in result.details)
        result.max_score = 60
        return result

    def score_infrastructure(self) -> ScoreResult:
        """基建六维度量化模型 - 根据 score_system.md 重构"""
        result = ScoreResult(ticker=self.ticker, industry="Infrastructure")

        # ===== 1. EBITDA Margin (运营利润率) - >55% =====
        ebitda_margin = self._get_value('EBITDA Margin')
        if ebitda_margin:
            score = min(1, ebitda_margin / 55) * 10
            result.details.append({
                'metric': 'EBITDA Margin (运营利润率)',
                'value': f"{ebitda_margin:.2f}%",
                'score': score,
                'max': 10,
                'unit': '%',
                'benchmark': '>55%',
                'description': '基建股的"毛利率"。相当于"收租毛利率"，>55%说明管道/收费公路等资产盈利性很强。'
            })
            if ebitda_margin > 55:
                result.passed_checks.append('EBITDA Margin')

        # ===== 2. Cash Conversion (现金转化率) - >95% =====
        # 公式: Cash Conversion = Operating Cash Flow / EBITDA * 100
        # 基建优等生要求 OCF 紧贴 EBITDA
        ocf = self._get_value('Operating Cash Flow')
        ebitda = self._get_value('EBITDA')
        result.log(f"Cash Conv - OCF: {ocf}, EBITDA: {ebitda}")

        if ocf and ebitda and ebitda != 0:
            cash_conv = (ocf / ebitda) * 100
            score = min(1, cash_conv / 95) * 10
            result.details.append({
                'metric': 'Cash Conversion (现金转化率)',
                'value': f"{cash_conv:.2f}%",
                'score': score,
                'max': 10,
                'unit': '%',
                'benchmark': '>95%',
                'description': '利润变成真钱的能力。相当于"到账率"，>95%说明赚的利润基本都能收回现金，假利润少。'
            })
            if cash_conv > 95:
                result.passed_checks.append('Cash Conv')

        # ===== 3. Interest Cover Ratio (利息覆盖率) - >3x =====
        # 公式: Interest Cover = EBIT / Interest Expense
        # 基建安全线要求 >3x
        interest_cov = self._get_value('Interest Coverage Ratio')
        if interest_cov:
            score = min(1, interest_cov / 3) * 10
            result.details.append({
                'metric': 'Interest Cover (利息覆盖率)',
                'value': f"{interest_cov:.2f}x",
                'score': score,
                'max': 10,
                'unit': 'x',
                'benchmark': '>3x',
                'description': '基建的安全带。相当于"赚的钱够还几次利息"，>3x说明加息也不怕，安全垫厚。'
            })
            if interest_cov > 3:
                result.passed_checks.append('Interest Cover')

        # ===== 4. EV/EBITDA (企业价值倍数) - 12-15x =====
        ev_ebitda = self._get_value('EV/EBITDA Ratio', 'EV / EBITDA Ratio')
        if ev_ebitda:
            score = self._check_range(ev_ebitda, 12, 15) * 10
            result.details.append({
                'metric': 'EV/EBITDA (企业价值倍数)',
                'value': f"{ev_ebitda:.2f}x",
                'score': score,
                'max': 10,
                'unit': 'x',
                'benchmark': '12-15x',
                'description': '基建估值指标。相当于"买下公司几年能回本"，12-15x是合理区间，太贵要小心。'
            })
            if 12 <= ev_ebitda <= 15:
                result.passed_checks.append('EV/EBITDA')

        # ===== 5. Debt/Equity (债务权益比) - <2.0x =====
        debt_eq = self._get_value('Debt / Equity Ratio')
        if debt_eq:
            score = max(0, (2.0 - debt_eq) / 2.0) * 10
            result.details.append({
                'metric': 'Debt/Equity (债务权益比)',
                'value': f"{debt_eq:.2f}x",
                'score': score,
                'max': 10,
                'unit': 'x',
                'benchmark': '<2.0x',
                'description': '基建杠杆率。相当于"借了股东多少钱"，<2x说明债务不算高，极端行情下不会资不抵债。'
            })
            if debt_eq < 2.0:
                result.passed_checks.append('Debt/Equity')

        # ===== 6. Current Ratio (流动比率) - >1.5x =====
        current = self._get_value('Current Ratio')
        if current:
            score = min(1, current / 1.5) * 10
            result.details.append({
                'metric': 'Current Ratio (流动比率)',
                'value': f"{current:.2f}x",
                'score': score,
                'max': 10,
                'unit': 'x',
                'benchmark': '>1.5x',
                'description': '短期偿债能力。相当于"有没有钱还短期债"，>1.5x说明流动性好，不会突然资金链断裂。'
            })
            if current > 1.5:
                result.passed_checks.append('Current Ratio')

        result.total_score = sum(d['score'] for d in result.details)
        result.max_score = 60
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
        """必需消费六维度量化模型 - 根据 score_system.md 重构"""
        result = ScoreResult(ticker=self.ticker, industry="Consumer Staples")

        # ===== 1. EBIT Margin (息税前利润率) - 4.5%-6% =====
        ebit_margin = self._get_value('EBIT Margin', 'Operating Margin')
        if ebit_margin:
            score = self._check_range(ebit_margin, 4.5, 6) * 10
            result.details.append({
                'metric': 'EBIT Margin (息税前利润率)',
                'value': f"{ebit_margin:.2f}%",
                'score': score,
                'max': 10,
                'unit': '%',
                'benchmark': '4.5%-6%',
                'description': '零售业的"毛利率"。相当于"卖100块能赚多少"，4.5%-6%是超市/百货的正常水平。'
            })
            if 4.5 <= ebit_margin <= 6:
                result.passed_checks.append('EBIT Margin')

        # ===== 2. ROE (净资产收益率) - >25% =====
        roe = self._get_value('ROE', 'Return on Equity (ROE)')
        if roe:
            score = min(1, roe / 25) * 10
            result.details.append({
                'metric': 'ROE (净资产收益率)',
                'value': f"{roe:.2f}%",
                'score': score,
                'max': 10,
                'unit': '%',
                'benchmark': '>25%',
                'description': '股东投入的回报率。相当于"WES/Bunnings赚钱能力"，>25%说明用很少的本金就能赚大钱，是零售巨头的标志。'
            })
            if roe > 25:
                result.passed_checks.append('ROE')

        # ===== 3. Inventory Days (库存周转天数) =====
        # 公式: Inventory Days = (Inventory / Cost of Revenue) * 365
        # 超市基准是 25-30 天, 百货可适当放宽
        inventory = self._get_value('Inventory', 'Inventories')
        cost_revenue = self._get_value('Cost of Revenue', 'Cost of Goods Sold')
        result.log(f"Inventory Days - Inventory: {inventory}, Cost: {cost_revenue}")

        inv_days = None
        if inventory and cost_revenue and cost_revenue > 0:
            inv_days = (inventory / cost_revenue) * 365
            result.log(f"Inventory Days - Calculated: {inv_days:.1f}")

        if inv_days:
            # 越低越好, 30天以内为优秀
            score = max(0, (60 - inv_days) / 60) * 10 if inv_days <= 60 else 0
            result.details.append({
                'metric': 'Inventory Days (库存周转天数)',
                'value': f"{inv_days:.1f} 天",
                'score': score,
                'max': 10,
                'unit': 'days',
                'benchmark': '<30天(超市)/<90天(百货)',
                'description': '零售的生死线。相当于"货在仓库放几天能卖掉"，越短越好，货放越久钱亏越多。'
            })
            if inv_days < 30:
                result.passed_checks.append('Inventory Days')

        # ===== 4. Forward PE (远期市盈率) - 20x-24x =====
        fwd_pe = self._get_value('Forward PE')
        if fwd_pe:
            score = self._check_range(fwd_pe, 20, 24) * 10
            result.details.append({
                'metric': 'Forward PE (远期市盈率)',
                'value': f"{fwd_pe:.2f}x",
                'score': score,
                'max': 10,
                'unit': 'x',
                'benchmark': '20-24x',
                'description': '估值锚点。相当于"多少年能回本"，20-24x是防守型资产的正常估值，太贵要小心。'
            })
            if 20 <= fwd_pe <= 24:
                result.passed_checks.append('Forward PE')

        # ===== 5. Dividend Yield (股息收益率) - >4% =====
        div_yield = self._get_value('Dividend Yield')
        if div_yield:
            score = min(1, div_yield / 4) * 10
            result.details.append({
                'metric': 'Dividend Yield (股息收益率)',
                'value': f"{div_yield:.2f}%",
                'score': score,
                'max': 10,
                'unit': '%',
                'benchmark': '>4%',
                'description': '相当于"每年发多少红包"。>4%说明股价便宜或分红慷慨，是必需消费股的核心吸引力。'
            })
            if div_yield > 4:
                result.passed_checks.append('Div Yield')

        # ===== 6. Payout Ratio (股息支付率) - <80% =====
        payout = self._get_value('Payout Ratio')
        if payout:
            score = max(0, (80 - payout) / 80) * 10
            result.details.append({
                'metric': 'Payout Ratio (股息支付率)',
                'value': f"{payout:.2f}%",
                'score': score,
                'max': 10,
                'unit': '%',
                'benchmark': '<80%',
                'description': '分红可持续性。相当于"赚100块分多少"，<80%说明留了钱用于扩张，不是"吃光花尽"。'
            })
            if payout < 80:
                result.passed_checks.append('Payout')

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
        print(f"报告已生成: {args.output}")
    else:
        print(html)


if __name__ == '__main__':
    main()
