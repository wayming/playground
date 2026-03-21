#!/usr/bin/env python3
"""
Google Gemini API Integration for Financial Data Filling
当 stockanalysis.com 数据缺失时，使用 Gemini API 补充基础数据

唯一的公开接口: fill_missing_data(json_data, industry)
"""

import os
import json
import re
import requests
from typing import Dict, Any, Optional, List

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent'


# 行业特定的缺失指标 - 需要通过 Gemini 搜索的基础数据
INDUSTRY_MISSING_FIELDS = {
    'banks': [
        'Common Equity Tier 1 Capital',
        'Risk Weighted Assets',
        'Group Average LVR',
    ],
    'materials': [       
        'Annual Production Volume'
        'Total Proved Reserves',
        'Sustaining Capex',
    ],
    'infrastructure': [
        'CPI Linkage',
        'Weighted Average Contract Expiry',
    ],
    'consumer_staples': [
        "Total Industry Revenue"
        'Forward EPS',
    ],
}


def _get_search_fields(industry: str) -> List[str]:
    """获取指定行业需要搜索的基础字段列表"""
    return INDUSTRY_MISSING_FIELDS.get(industry, [])


def _build_search_prompt(ticker: str, industry: str, fields: List[str]) -> str:
    """构建 Gemini 查询 Prompt"""
    industry_context = {
        'banks': '银行',
        'materials': '矿业/材料',
        'infrastructure': '基础设施/公用事业',
        'healthcare': '医疗健康',
        'telecom': '电信/通信',
        'consumer_staples': '必需消费品'
    }

    fields_list = '\n'.join([f"- {field}" for field in fields])

    prompt = f"""
# Role
你是一个专业的金融数据分析师，严谨且只输出机器可读的结构化数据。

# Task
Search the latest 2025/2026 financial reports for 
股票代码: {ticker}
行业: {industry}

Then, extract the following required data

# Data Fields
{fields_list}

# Banking Specific Search Guide
1. Search for "{ticker} Latest Pillar 3 Disclosure" or "{ticker} Investor Discussion Pack FY2025".
2. "Group Average LVR": Look for "Average LVR" or "LVR at origination" within the Residential/Home Lending portfolio section.
3. "CET1" and "RWA": These are regulatory capital figures found in the Capital Adequacy table.


# Constraints (必须严格遵守)
1. 输出格式：必须是合法的 JSON 格式。
2. 禁止行为：严禁输出任何开场白（如“好的”、“这是你要的数据”）、结尾总结或解释性文字。
3. 缺失处理：如果数据不存在，对应 value 必须填 null。
4. 单位:M=百万, B=十亿。
5. 周期：仅限 "FY 2025" 或 "FY 2026"。

# Output Example (必须模仿此格式)dd
{{
  "EBITDA": {{"FY 2025" : 5000, "FY 2026" : 5500}},
  "Free Cash Flow": {{"FY 2025" : null, "FY 2026" : null}},
}}

# Execution
请立即从 ASX {ticker} 的年报中提取数据，不要输出任何 JSON 代码块标记之外的文字：
    """

    return prompt


def _call_api(prompt: str) -> Optional[str]:
    """调用 Gemini API"""
    if not GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY not set")
        return None

    url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"

    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        'contents': [
            {
                'parts': [
                    {'text': prompt},
                    {'text': "Please use Google Search to find specifically: 'NAB Full Year 2025 Investor Discussion Pack PDF' and 'NAB Pillar 3 Disclosure September 2025'."}
                ]
            }
        ],
        "tools": [{
            "google_search": {}
        }],
        'generationConfig': {
            'temperature': 0.0,
            'maxOutputTokens': 2048,
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()

        # Gemini 返回格式: result['candidates'][0]['content']['parts'][0]['text']
        if 'candidates' in result and len(result['candidates']) > 0:
            candidate = result['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content']:
                return candidate['content']['parts'][0].get('text')

        return None
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return None


def _parse_response(response: str) -> Dict[str, Any]:
    """解析 API 返回的 JSON 响应"""
    if not response:
        return {}

    print(f"Raw API response: {response}")
    # 尝试提取 JSON 块
    json_match = re.search(r'\{[\s\S]*\}', response)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")

    return {}


def _is_field_missing(json_data: Dict, field: str) -> bool:
    """检查字段是否在 json_data 中缺失"""
    # 检查 ratios
    if field in json_data.get('ratios', {}):
        val = json_data['ratios'][field]
        if val and isinstance(val, (int, float)):
            return False
        if isinstance(val, dict):
            if val.get('Current') or val.get('TTM'):
                return False

    # 检查 income_statement
    if field in json_data.get('income_statement', {}):
        val = json_data['income_statement'][field]
        if val and isinstance(val, (int, float)):
            return False
        if isinstance(val, dict):
            if val.get('Current') or val.get('TTM'):
                return False

    # 检查 balance_sheet
    if field in json_data.get('balance_sheet', {}):
        val = json_data['balance_sheet'][field]
        if val and isinstance(val, (int, float)):
            return False
        if isinstance(val, dict):
            if val.get('Current') or val.get('TTM'):
                return False

    # 检查 cash_flow
    if field in json_data.get('cash_flow', {}):
        val = json_data['cash_flow'][field]
        if val and isinstance(val, (int, float)):
            return False
        if isinstance(val, dict):
            if val.get('Current') or val.get('TTM'):
                return False

    return True


def fill_missing_data(json_data: Dict, industry: str) -> Dict:
    """
    填充缺失的基础数据 - 唯一的公开接口

    1. 识别 json_data 中缺失的字段
    2. 调用 Gemini API 搜索这些字段
    3. 将搜索结果填充到 json_data

    Args:
        json_data: 包含财务数据的字典
        industry: 行业类型 (banks/materials/infrastructure/healthcare/telecom/consumer_staples)

    Returns:
        更新后的 json_data
    """
    ticker = json_data.get('ticker', '').replace('.AX', '')

    # 获取行业需要搜索的字段
    search_fields = _get_search_fields(industry)

    if not search_fields:
        print(f"{ticker}: No search fields defined for industry {industry}")
        return json_data

    # 识别缺失的字段
    missing_fields = [f for f in search_fields if _is_field_missing(json_data, f)]

    if not missing_fields:
        print(f"{ticker}: No missing fields for industry {industry}")
        return json_data

    print(f"{ticker}: Searching for missing fields: {missing_fields}")

    # 构建 Prompt 并调用 API
    prompt = _build_search_prompt(ticker, industry, missing_fields)
    response = _call_api(prompt)
    print(f"{ticker} prompt: {prompt}")
    if not response:
        print(f"{ticker}: Failed to get response from Gemini API")
        return json_data

    # 解析响应
    filled_data = _parse_response(response)
    print(f"{ticker}: Filling data from Gemini API: {filled_data}")

    if not filled_data:
        print(f"{ticker}: No valid data from API")
        return json_data

    # 将搜索结果填充到 json_data
    # 默认添加到 extra
    if 'extra' not in json_data:
        json_data['extra'] = {}

    json_data['extra'] = filled_data

    return json_data


def main():
    """测试入口"""
    import argparse

    parser = argparse.ArgumentParser(description='使用 Gemini API 补充财务数据')
    parser.add_argument('ticker', help='股票代码 (如 CBA)')
    parser.add_argument('--industry', default='banks', help='行业类型')
    parser.add_argument('--api-key', help='Gemini API Key (或设置 GEMINI_API_KEY 环境变量)')

    args = parser.parse_args()

    # 设置 API Key
    global GEMINI_API_KEY
    if args.api_key:
        GEMINI_API_KEY = args.api_key

    if not GEMINI_API_KEY:
        print("Error: Please set GEMINI_API_KEY environment variable or use --api-key")
        return

    # 构建测试数据
    json_data = {'ticker': args.ticker}

    print(f"Filling missing data for {args.ticker} ({args.industry})...")
    result = fill_missing_data(json_data, args.industry)

    print(f"\nResult:\n{json.dumps(result, indent=2)}")


if __name__ == '__main__':
    main()
