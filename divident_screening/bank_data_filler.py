#!/usr/bin/env python3
"""
Bank Data Filler - 检查并补充银行数据
"""

import json
import os
import sys
from deepseek_filler import fill_missing_data, INDUSTRY_DERIVED_FIELDS

# 银行列表
BANK_FILES = [
    ('CBA', 'data/json/CBA_20260314_073143_839079f8.json'),
    ('NAB', 'data/json/NAB_20260314_080056_4fe61354.json'),
    # 添加更多银行文件...
]

# 银行评分需要的指标
BANK_SCORE_FIELDS = {
    'NIM': '净息差',
    'CET1 Ratio': '一级资本充足率',
    'Cost-to-Income Ratio': '成本收入比',
    'ROE': '净资产收益率',
    'Bad Debt Ratio': '不良贷款率',
    'Payout Ratio': '股息支付率'
}


def check_bank_data_completeness(json_data: dict) -> dict:
    """检查银行数据完整性"""
    completeness = {}

    # 检查基础数据
    income = json_data.get('income_statement', {})
    balance = json_data.get('balance_sheet', {})
    ratios = json_data.get('ratios', {})

    # NIM 计算需要的数据
    nim_data = {
        'Net Interest Income': 'income_statement',
        'Cash & Equivalents': 'balance_sheet',
        'Investment Securities': 'balance_sheet',
        'Net Loans': 'balance_sheet',
        'Gross Loans': 'balance_sheet'
    }
    completeness['NIM'] = all(
        any(k in src for src in [income, balance, ratios])
        for k in nim_data.keys()
    )

    # CET1 Ratio
    cet1_fields = ['CET1 Ratio', 'Common Equity Tier 1 Ratio', 'Risk Weighted Assets', 'Total Common Equity']
    completeness['CET1'] = any(
        any(k in src for src in [income, balance, ratios])
        for k in cet1_fields
    )

    # Cost-to-Income
    cti_fields = ['Cost-to-Income Ratio', 'Cost to Income Ratio', 'Total Non-Interest Expense', 'Revenues Before Loan Losses']
    completeness['Cost-to-Income'] = any(
        any(k in src for src in [income, balance, ratios])
        for k in cti_fields
    )

    # ROE
    roe_fields = ['ROE', 'Return on Equity (ROE)']
    completeness['ROE'] = any(
        any(k in src for src in [income, balance, ratios])
        for k in roe_fields
    )

    # Bad Debt Ratio
    bad_debt_fields = ['Bad Debt Ratio', 'Non-Performing Loan Ratio', 'NPL Ratio', 'Provision for Loan Losses']
    completeness['Bad Debt'] = any(
        any(k in src for src in [income, balance, ratios])
        for k in bad_debt_fields
    )

    # Payout Ratio
    payout_fields = ['Payout Ratio', 'Dividend Payout Ratio']
    completeness['Payout'] = any(
        any(k in src for src in [income, balance, ratios])
        for k in payout_fields
    )

    return completeness


def print_completeness(ticker: str, completeness: dict):
    """打印数据完整性"""
    print(f"\n{'='*50}")
    print(f"数据完整性检查: {ticker}")
    print(f"{'='*50}")

    for field, is_complete in completeness.items():
        status = "✓" if is_complete else "✗"
        print(f"  {status} {field}: {'完整' if is_complete else '缺失'}")

    all_complete = all(completeness.values())
    status = "数据完整" if all_complete else "需要补充"
    print(f"\n总体: {status}")


def process_bank_data(ticker: str, json_path: str, api_key: str = None):
    """处理银行数据"""
    print(f"\n{'#'*60}")
    print(f"# 处理银行数据: {ticker}")
    print(f"# 文件: {json_path}")
    print(f"{'#'*60}")

    # 加载数据
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    # 检查完整性
    completeness = check_bank_data_completeness(json_data)
    print_completeness(ticker, completeness)

    # 如果有 API key，调用 deepseek 补充数据
    if api_key:
        os.environ['DEEPSEEK_API_KEY'] = api_key
        print(f"\n调用 DeepSeek API 补充数据...")

        json_data = fill_missing_data(json_data, 'banks')

        # 保存更新后的数据
        output_path = json_path.replace('.json', '_filled.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        print(f"\n数据已保存到: {output_path}")

    return json_data


def main():
    import argparse

    parser = argparse.ArgumentParser(description='检查并补充银行数据')
    parser.add_argument('--ticker', help='股票代码 (如 CBA)')
    parser.add_argument('--file', help='JSON 文件路径')
    parser.add_argument('--api-key', help='DeepSeek API Key')
    parser.add_argument('--list', action='store_true', help='列出所有银行文件')

    args = parser.parse_args()

    if args.list:
        print("可用银行数据文件:")
        for ticker, path in BANK_FILES:
            exists = "✓" if os.path.exists(path) else "✗"
            print(f"  {exists} {ticker}: {path}")
        return

    if args.ticker and args.file:
        process_bank_data(args.ticker, args.file, args.api_key)
    elif args.ticker:
        # 查找对应的文件
        found = False
        for ticker, path in BANK_FILES:
            if ticker == args.ticker and os.path.exists(path):
                process_bank_data(args.ticker, path, args.api_key)
                found = True
                break
        if not found:
            print(f"未找到 {args.ticker} 的数据文件")
    else:
        # 处理所有已知银行
        for ticker, path in BANK_FILES:
            if os.path.exists(path):
                process_bank_data(ticker, path, args.api_key)


if __name__ == '__main__':
    main()
