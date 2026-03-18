#!/usr/bin/env python3
"""
DeepSeek API Integration for Financial Data
当 stockanalysis.com 数据缺失时，使用 DeepSeek API 补充数据
"""

import os
import json
import re
import requests
from typing import Dict, Any, Optional, List

DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'


# 行业特定的缺失指标 - 需要的基础数据
# 格式: {指标名: (需要的底层数据字段, 计算公式/说明)}
INDUSTRY_DERIVED_FIELDS = {
    'banks': {
        'CET1 Ratio': {
            'needed': ['Total Common Equity', 'Risk Weighted Assets'],
            'formula': 'lambda equity, rwa: (equity / rwa * 100) if rwa else None',
            'fallback': ['Common Equity Tier 1', 'Tier 1 Capital'],
            'search_fields': ['Total Common Equity', 'Risk Weighted Assets', 'Common Equity Tier 1 Capital']
        }
    },
    'materials': {
        'EBITDA': {
            'needed': ['EBITDA'],
            'formula': '直接取值',
            'fallback': ['Operating Income', 'EBIT'],
            'search_fields': ['EBITDA', 'Operating Income', 'EBIT']
        },
        'EBITDA Margin': {
            'needed': ['EBITDA', 'Revenue'],
            'formula': 'lambda ebitda, rev: (ebitda / rev * 100) if rev else None',
            'fallback': [],
            'search_fields': ['EBITDA']
        },
        'Net Debt / EBITDA Ratio': {
            'needed': ['Net Cash (Debt)', 'EBITDA'],
            'formula': 'lambda debt, ebitda: (abs(debt) / ebitda) if ebitda else None',
            'fallback': [],
            'search_fields': ['Net Debt', 'EBITDA', 'Total Debt', 'Cash & Equivalents']
        },
        'FCF Yield': {
            'needed': ['Free Cash Flow Yield'],
            'formula': '直接取值',
            'fallback': ['Free Cash Flow', 'Market Capitalization'],
            'search_fields': ['Free Cash Flow Yield', 'FCF Yield', 'Free Cash Flow', 'Market Cap']
        },
        'Payout Ratio': {
            'needed': ['Payout Ratio'],
            'formula': '直接取值',
            'fallback': ['Common Dividends Paid', 'Net Income'],
            'search_fields': ['Payout Ratio', 'Dividend Payout Ratio', 'Common Dividends Paid']
        }
    },
    'infrastructure': {
        'EBITDA': {
            'needed': ['EBITDA'],
            'formula': '直接取值',
            'fallback': ['Operating Income', 'EBIT'],
            'search_fields': ['EBITDA', 'Operating Income', 'EBIT']
        },
        'Interest Coverage Ratio': {
            'needed': ['EBITDA', 'Interest Expense'],
            'formula': 'lambda ebitda, interest: (ebitda / interest) if interest else None',
            'fallback': [],
            'search_fields': ['Interest Expense', 'EBITDA']
        },
        'Net Debt / EBITDA Ratio': {
            'needed': ['Net Cash (Debt)', 'EBITDA'],
            'formula': 'lambda debt, ebitda: (abs(debt) / ebitda) if ebitda else None',
            'fallback': [],
            'search_fields': ['Net Debt', 'EBITDA']
        },
        'EV/EBITDA Ratio': {
            'needed': ['Enterprise Value', 'EBITDA'],
            'formula': 'lambda ev, ebitda: (ev / ebitda) if ebitda else None',
            'fallback': ['Market Capitalization', 'Total Debt', 'Cash & Equivalents'],
            'search_fields': ['Enterprise Value', 'Market Capitalization', 'Total Debt', 'Cash']
        },
        'CPI Linkage': {
            'needed': ['CPI Linkage'],
            'formula': '直接取值',
            'fallback': [],
            'search_fields': ['CPI Linkage', 'CPI Linkage %', 'Inflation Linkage']
        },
        'WACE': {
            'needed': ['WACE'],
            'formula': '直接取值',
            'fallback': ['Weighted Average Contract Expiry', 'Contract Expiry (Years)'],
            'search_fields': ['WACE', 'Weighted Average Contract Expiry', 'Contract Expiry']
        }
    },
    'healthcare': {
        'EBITDA Margin': {
            'needed': ['EBITDA', 'Revenue'],
            'formula': 'lambda ebitda, rev: (ebitda / rev * 100) if rev else None',
            'fallback': [],
            'search_fields': ['EBITDA']
        },
        'EV/EBITDA Ratio': {
            'needed': ['Enterprise Value', 'EBITDA'],
            'formula': 'lambda ev, ebitda: (ev / ebitda) if ebitda else None',
            'fallback': [],
            'search_fields': ['Enterprise Value', 'EBITDA']
        }
    },
    'telecom': {
        'EBITDA': {
            'needed': ['EBITDA'],
            'formula': '直接取值',
            'fallback': ['Operating Income', 'EBIT'],
            'search_fields': ['EBITDA', 'Operating Income', 'EBIT']
        },
        'EV/EBITDA Ratio': {
            'needed': ['Enterprise Value', 'EBITDA'],
            'formula': 'lambda ev, ebitda: (ev / ebitda) if ebitda else None',
            'fallback': [],
            'search_fields': ['Enterprise Value', 'EBITDA']
        }
    },
    'consumer_staples': {
        'EBITDA Margin': {
            'needed': ['EBITDA', 'Revenue'],
            'formula': 'lambda ebitda, rev: (ebitda / rev * 100) if rev else None',
            'fallback': [],
            'search_fields': ['EBITDA']
        },
        'Current Ratio': {
            'needed': ['Total Current Assets', 'Total Current Liabilities'],
            'formula': 'lambda assets, liab: (assets / liab) if liab else None',
            'fallback': [],
            'search_fields': ['Total Current Assets', 'Total Current Liabilities']
        },
        'Market Share Change': {
            'needed': ['Market Share', 'Revenue'],
            'formula': 'lambda ms, rev: ms if ms is not None else None',
            'fallback': ['Revenue Growth (YoY)'],
            'search_fields': ['Market Share', 'Market Share Growth', 'Revenue Growth']
        },
        'Franking Credits': {
            'needed': ['Dividend per Share', 'Tax Rate'],
            'formula': 'lambda div, tax: (div * tax / (1 - tax)) if div and tax else None',
            'fallback': [100],  # Default to 100% for Australian companies
            'search_fields': ['Franking Credits', 'Imputation Credits', 'Tax Credit']
        }
    }
}

# 旧版本兼容
INDUSTRY_MISSING_FIELDS = {
    'banks': ['CET1 Ratio', 'Risk Weighted Assets', 'Tier 1 Capital', 'Common Equity Tier 1', 'Interest Coverage Ratio'],
    'materials': ['EBITDA', 'EBITDA Margin', 'Net Debt / EBITDA Ratio'],
    'infrastructure': ['EBITDA', 'Interest Coverage Ratio', 'Net Debt / EBITDA Ratio'],
    'healthcare': ['EBITDA Margin', 'EV/EBITDA Ratio'],
    'telecom': ['EBITDA', 'EV/EBITDA Ratio'],
    'consumer_staples': ['EBITDA Margin', 'Current Ratio', 'Market Share Change', 'Franking Credits']
}


def build_prompt(ticker: str, industry: str, missing_fields: List[str]) -> str:
    """构建查询 Prompt - 旧版本，保留兼容"""
    return build_prompt_for_base_data(ticker, industry, missing_fields)


def build_prompt_for_base_data(ticker: str, industry: str, base_fields: List[str]) -> str:
    """构建查询 Prompt - 搜索底层基础数据"""
    industry_context = {
        'banks': '银行',
        'materials': '矿业/材料',
        'infrastructure': '基础设施/公用事业',
        'healthcare': '医疗健康',
        'telecom': '电信/通信',
        'consumer_staples': '必需消费品'
    }

    fields_list = '\n'.join([f"{i+1}. {field}" for i, field in enumerate(base_fields)])

    prompt = f"""你是一个专业的金融数据分析师。你的任务是从澳大利亚证券交易所(ASX)上市公司的公开财务报告/年报中查找具体的底层财务数据。

股票代码: {ticker}
行业: {industry} ({industry_context.get(industry, industry)})

请查找以下底层数据（不要查找比率指标，如CET1 Ratio，只需要原始数据）:
{fields_list}

请以JSON格式返回，格式如下:
{{
  "Total Common Equity": {{"value": 50000, "unit": "M", "period": "FY 2025"}},
  "Risk Weighted Assets": {{"value": 416700, "unit": "M", "period": "FY 2025"}},
  "EBITDA": {{"value": 5000, "unit": "M", "period": "FY 2025"}}
}}

重要要求:
1. 只返回JSON，不要其他文字说明
2. 如果某个数据找不到，用null表示
3. 数值单位说明: M=百万, B=十亿, 金额通常用M
4. period格式: FY 2025 或 H1 2025
5. 请务必从ASX{ticker}的年报或半年报中查找真实数据
6. 确保JSON格式正确，可以被python json.loads()解析"""

    return prompt


def call_deepseek_api(prompt: str) -> Optional[str]:
    """调用 DeepSeek API"""
    if not DEEPSEEK_API_KEY:
        print("Warning: DEEPSEEK_API_KEY not set")
        return None

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}'
    }

    data = {
        'model': 'deepseek-chat',
        'messages': [
            {'role': 'user', 'content': prompt}
        ],
        'temperature': 0.3
    }

    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error calling DeepSeek API: {e}")
        return None


def parse_json_response(response: str) -> Dict[str, Any]:
    """解析 API 返回的 JSON 响应"""
    if not response:
        return {}

    # 尝试提取 JSON 块
    json_match = re.search(r'\{[\s\S]*\}', response)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print(f"Response: {response}")

    return {}


def find_data_in_sources(json_data: Dict, field_name: str) -> Optional[float]:
    """在各个数据源中查找指定字段"""
    # 检查 ratios
    if field_name in json_data.get('ratios', {}):
        val = json_data['ratios'][field_name].get('Current') or json_data['ratios'][field_name].get('TTM')
        if val and isinstance(val, (int, float)):
            return float(val)

    # 检查 income_statement
    if field_name in json_data.get('income_statement', {}):
        val = json_data['income_statement'][field_name].get('Current') or json_data['income_statement'][field_name].get('TTM')
        if val and isinstance(val, (int, float)):
            return float(val)

    # 检查 balance_sheet
    if field_name in json_data.get('balance_sheet', {}):
        val = json_data['balance_sheet'][field_name].get('Current') or json_data['balance_sheet'][field_name].get('TTM')
        if val and isinstance(val, (int, float)):
            return float(val)

    # 检查 cash_flow
    if field_name in json_data.get('cash_flow', {}):
        val = json_data['cash_flow'][field_name].get('Current') or json_data['cash_flow'][field_name].get('TTM')
        if val and isinstance(val, (int, float)):
            return float(val)

    return None


def derive_indicator(json_data: Dict, indicator_config: Dict) -> Optional[float]:
    """尝试从基础数据推导指标"""
    needed = indicator_config.get('needed', [])

    # 收集需要的底层数据
    values = {}
    for field in needed:
        val = find_data_in_sources(json_data, field)
        if val is not None:
            values[field] = val

    # 如果所有基础数据都找到了，尝试计算
    if len(values) == len(needed):
        try:
            # CET1 Ratio = Total Common Equity / Risk Weighted Assets * 100
            if 'Total Common Equity' in values and 'Risk Weighted Assets' in values:
                equity = values['Total Common Equity']
                rwa = values['Risk Weighted Assets']
                # 如果 RWA 是十亿单位，转换为百万
                if rwa > 100000:  # 假设大于 100000 的是原始单位（百万）
                    pass
                elif rwa > 100:  # 十亿转百万
                    rwa = rwa * 1000
                return (equity / rwa * 100) if rwa else None

            # EBITDA Margin = EBITDA / Revenue * 100
            if 'EBITDA' in values and 'Revenue' in values:
                ebitda = values['EBITDA']
                rev = values['Revenue']
                return (ebitda / rev * 100) if rev else None

            # Net Debt / EBITDA = abs(Net Debt) / EBITDA
            if 'Net Cash (Debt)' in values and 'EBITDA' in values:
                debt = values['Net Cash (Debt)']
                ebitda = values['EBITDA']
                return (abs(debt) / ebitda) if ebitda else None

            # Interest Coverage = EBITDA / Interest Expense
            if 'EBITDA' in values and 'Interest Expense' in values:
                ebitda = values['EBITDA']
                interest = values['Interest Expense']
                return (ebitda / interest) if interest else None

            # Current Ratio = Current Assets / Current Liabilities
            if 'Total Current Assets' in values and 'Total Current Liabilities' in values:
                assets = values['Total Current Assets']
                liab = values['Total Current Liabilities']
                return (assets / liab) if liab else None

            # FCF Yield = Free Cash Flow / Market Capitalization * 100
            if 'Free Cash Flow' in values and 'Market Capitalization' in values:
                fcf = values['Free Cash Flow']
                market_cap = values['Market Capitalization']
                return (fcf / market_cap * 100) if market_cap else None

            # Payout Ratio = Common Dividends / Net Income * 100
            if 'Common Dividends Paid' in values and 'Net Income' in values:
                dividends = abs(values['Common Dividends Paid'])
                net_income = values['Net Income']
                return (dividends / net_income * 100) if net_income else None

            # EV/EBITDA = Enterprise Value / EBITDA
            if 'Enterprise Value' in values and 'EBITDA' in values:
                ev = values['Enterprise Value']
                ebitda = values['EBITDA']
                return (ev / ebitda) if ebitda else None

            # EV/EBITDA from components = (Market Cap + Debt - Cash) / EBITDA
            if 'Market Capitalization' in values and 'EBITDA' in values:
                market_cap = values['Market Capitalization']
                ebitda = values['EBITDA']
                # Try to get debt and cash
                debt = find_data_in_sources(json_data, 'Total Debt') or 0
                cash = find_data_in_sources(json_data, 'Cash & Equivalents') or 0
                ev = market_cap + (debt or 0) - (cash or 0)
                return (ev / ebitda) if ebitda else None

        except Exception as e:
            print(f"  Derive error: {e}")

    return None


def detect_missing_derived_fields(json_data: Dict, industry: str) -> Dict:
    """
    检测缺失的指标，并返回需要通过 AI 搜索的底层字段
    返回: {指标名: 需要搜索的底层字段列表}
    """
    derived_fields = INDUSTRY_DERIVED_FIELDS.get(industry, {})
    result = {}

    for indicator, config in derived_fields.items():
        # 先尝试从现有数据推导
        derived_value = derive_indicator(json_data, config)

        if derived_value is None:
            # 推导失败，需要搜索底层数据
            search_fields = config.get('search_fields', [])
            if search_fields:
                result[indicator] = search_fields
                print(f"  {indicator}: 需要底层数据 {search_fields}")

    return result


def fill_missing_data(json_data: Dict, industry: str) -> Dict:
    """
    1. 首先尝试用现有基础数据推导指标
    2. 只有当基础数据也缺失时才调用 AI 搜索
    """
    ticker = json_data.get('ticker', '').replace('.AX', '')

    # 获取行业配置
    derived_fields = INDUSTRY_DERIVED_FIELDS.get(industry, {})

    if not derived_fields:
        print(f"{ticker}: No derived fields config for industry {industry}")
        return json_data

    print(f"{ticker}: Checking derived fields for industry {industry}...")

    # 初始化 ratios
    if 'ratios' not in json_data:
        json_data['ratios'] = {}

    # 第一步：尝试推导指标
    for indicator, config in derived_fields.items():
        # 先尝试推导
        derived_value = derive_indicator(json_data, config)

        if derived_value is not None:
            json_data['ratios'][indicator] = {
                'Current': derived_value,
                'derived': True,
                'source': 'calculated'
            }
            print(f"  {indicator}: derived from base data = {derived_value}")
        else:
            print(f"  {indicator}: needs base data")

    # 第二步：检测哪些底层数据缺失，需要 AI 搜索
    missing_base_data = detect_missing_derived_fields(json_data, industry)

    if not missing_base_data:
        print(f"{ticker}: All indicators derived or available")
        return json_data

    # 收集所有需要搜索的字段
    all_search_fields = []
    for indicator, fields in missing_base_data.items():
        for field in fields:
            if field not in all_search_fields:
                all_search_fields.append(field)

    if not all_search_fields:
        return json_data

    # 第三步：调用 AI 搜索缺失的底层数据
    print(f"{ticker}: Requesting AI to search for: {all_search_fields}")

    prompt = build_prompt_for_base_data(ticker, industry, all_search_fields)
    response = call_deepseek_api(prompt)

    if not response:
        print(f"{ticker}: Failed to get response from DeepSeek API")
        return json_data

    # 解析响应
    filled_data = parse_json_response(response)

    if not filled_data:
        print(f"{ticker}: No valid data from API")
        return json_data

    # 将 AI 返回的数据添加到相应的数据源
    for field, value in filled_data.items():
        if value is None:
            continue

        # 尝试识别应该添加到哪个数据源
        # 默认添加到 ratios，用户工调整
        json_data['ratios'][field] = {
            'Current': value.get('value') if isinstance(value, dict) else value,
            'source': 'deepseek-api'
        }
        print(f"  Added {field} from AI: {value}")

    # 第四步：重新尝试推导指标
    for indicator, config in derived_fields.items():
        # 检查是否已经有值
        if indicator in json_data.get('ratios', {}) and json_data['ratios'][indicator].get('derived'):
            continue

        # 尝试推导
        derived_value = derive_indicator(json_data, config)

        if derived_value is not None:
            json_data['ratios'][indicator] = {
                'Current': derived_value,
                'derived': True,
                'source': 'calculated'
            }
            print(f"  {indicator}: derived after AI update = {derived_value}")

    return json_data


def main():
    """测试入口"""
    import argparse

    parser = argparse.ArgumentParser(description='使用 DeepSeek API 补充财务数据')
    parser.add_argument('ticker', help='股票代码 (如 CBA)')
    parser.add_argument('--industry', default='banks', help='行业类型')
    parser.add_argument('--api-key', help='DeepSeek API Key (或设置 DEEPSEEK_API_KEY 环境变量)')

    args = parser.parse_args()

    # 设置 API Key
    global DEEPSEEK_API_KEY
    if args.api_key:
        DEEPSEEK_API_KEY = args.api_key

    if not DEEPSEEK_API_KEY:
        print("Error: Please set DEEPSEEK_API_KEY environment variable or use --api-key")
        return

    # 测试 API 调用
    missing_fields = INDUSTRY_MISSING_FIELDS.get(args.industry, [])
    prompt = build_prompt(args.ticker, args.industry, missing_fields)

    print(f"Querying {args.ticker} ({args.industry})...")
    print(f"Missing fields: {missing_fields}")

    response = call_deepseek_api(prompt)
    if response:
        print(f"\nAPI Response:\n{response}")

        parsed = parse_json_response(response)
        print(f"\nParsed JSON:\n{json.dumps(parsed, indent=2)}")
    else:
        print("Failed to get response")


if __name__ == '__main__':
    main()
