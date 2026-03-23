#!/usr/bin/env python3
"""
Google Gemini API Integration for Financial Data Filling
当 stockanalysis.com 数据缺失时，使用 Gemini API 补充基础数据

唯一的公开接口: fill_missing_data(json_data, industry)

重构: 使用 Native SDK 调用
"""

import os
import json
import re
from google import genai
from google.genai import types

from typing import Dict, Any, Optional, List

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# 行业特定的缺失指标 - 需要通过 Gemini 搜索的基础数据
INDUSTRY_MISSING_FIELDS = {
    'banks': [
        # 'Common Equity Tier 1 Capital',
        # 'Risk Weighted Assets',
        # 'Group Average LVR',
        'Dynamic LVR'
    ],
    'materials': [
        'Annual Production Volume',
        'Total Proved Reserves',
        'Sustaining Capex',
    ],
    'infrastructure': [
        'CPI Linkage',
        'Weighted Average Contract Expiry',
    ],
    'consumer_staples': [
        'Total Industry Revenue',
        'Forward EPS',
    ],
}

# 模型配置
MODEL_NAME = 'gemini-3.1-flash-lite-preview'

GENERATION_CONFIG = {
    'temperature': 0.1,
    'max_output_tokens': 2048,
    'response_mime_type': 'application/json',
}


def _get_search_fields(industry: str) -> List[str]:
    """获取指定行业需要搜索的基础字段列表"""
    return INDUSTRY_MISSING_FIELDS.get(industry, [])


def _build_single_field_prompt(ticker: str, industry: str, field: str) -> str:
    """
    为单个字段构建查询 Prompt

    Args:
        ticker: 股票代码
        industry: 行业类型
        field: 需要查询的字段名
    """
    industry_context = {
        'banks': '银行',
        'materials': '矿业/材料',
        'infrastructure': '基础设施/公用事业',
        'healthcare': '医疗健康',
        'telecom': '电信/通信',
        'consumer_staples': '必需消费品'
    }

    # 为不同字段定制不同的查询上下文
    field_contexts = {
        'Common Equity Tier 1 Capital': 'CET1 Capital (一级资本)，银行的核心一级资本',
        'Risk Weighted Assets': 'RWA (风险加权资产)，银行的风险加权资产总额',
        'Group Average LVR': 'LVR (贷款价值比)，银行房贷的平均贷款价值比',
        'Annual Production Volume': '年度产量，矿业公司的年产量',
        'Total Proved Reserves': '总证实储量，矿业公司的证实储量',
        'Sustaining Capex': '维持性资本支出，维持现有产能的资本支出',
        'CPI Linkage': 'CPI 挂钩率，收入与通胀挂钩的比例',
        'Weighted Average Contract Expiry': 'WACE，合同加权平均到期年限',
        'Total Industry Revenue': '行业总收入，市场份额计算用',
        'Forward EPS': '前瞻每股收益，分析师预测的未来EPS',
    }

    context = field_contexts.get(field, field)

    prompt = f"""
# Role
你是一个专业的金融数据分析师，严谨且只输出机器可读的结构化数据。

# Task
Search the latest 2025/2026 financial reports for
股票代码: {ticker}
行业: {industry_context.get(industry, industry)}

Then, extract the following required data:

# Data Field
{field}
说明: {context}

# Constraints
1. 缺失处理：如果数据不存在，对应 value 必须填 null。
2. 单位: M=百万, B=十亿。对于百分比字段，输出数值(如 45.5 表示 45.5%)。
3. 优先提取 "Full Year" 的数值,如果没有full year,则提取half year。
4. 如果有多个时期的记录，返回所有记录。

# Output Example
{{
  "{field}" : {{"FY 2025" : 5000}}
}}

# Execution
第一步：搜索 {ticker} shareholder center, 寻找financial results reports。
第二步：在 report的pdf或者html页面中寻找 {field}。
第三步：如果找到多个时期的记录，先提取所有时间段的数据，并且返回所有记录。
第四步：仅以 JSON 格式输出最终数值，确保数值准确。

    """

    return prompt


def _call_api(prompt: str, field: str) -> Optional[str]:
    """
    调用 Gemini API (Native SDK)

    Args:
        prompt: 查询提示词
        field: 查询的字段名（用于调试）
    """
    if not GEMINI_API_KEY:
        print(f"Warning: GEMINI_API_KEY not set")
        return None

    # 确保客户端已配置
    client = genai.Client(api_key=GEMINI_API_KEY)


    try:
        # 构建完整的 prompt，包含搜索提示
        full_prompt = f"{prompt}\n\n{_get_search_hint(field)}"

        # 发起对话（支持 Google Search 工具调用）
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        google_search=types.GoogleSearch() 
                    )
                ],
                response_mime_type="application/json"
            )
        )

        try:
            return response.text
        except Exception as e:
            print(f"Error extracting text from response for field {field}: {e}")
            return None
    except Exception as e:
        print(f"Error calling Gemini API for field {field}: {e}")
        return None


def _get_search_hint(field: str) -> str:
    """
    根据字段名返回搜索提示，帮助 LLM 找到正确的数据源
    """
    hints = {
        'Common Equity Tier 1 Capital': "Please search for 'NAB Pillar 3 Disclosure' or 'CBA CET1 Capital' FY2025 annual report.",
        'Risk Weighted Assets': "Please search for 'NAB Risk Weighted Assets' or 'CBA RWA' FY2025 annual report.",
        'Group Average LVR': "Please search for 'NAB Group Average LVR' or 'CBA mortgage LVR' FY2025 annual report.",
        'Annual Production Volume': "Please search for 'FMG annual report 2025 production volume'.",
        'Total Proved Reserves': "Please search for 'BHP proved reserves 2025' or 'RIO Tinto reserves 2025'.",
        'Sustaining Capex': "Please search for 'sustaining capital expenditure' in annual report.",
        'CPI Linkage': "Please search for 'CPI linkage percentage' in infrastructure fund annual report.",
        'Weighted Average Contract Expiry': "Please search for 'WACE' or 'weighted average contract expiry' in annual report.",
        'Total Industry Revenue': "Please search for 'total industry revenue' or 'market size' for the sector.",
        'Forward EPS': "Please search for 'forward EPS 2026' or 'analyst consensus EPS'.",
    }
    return hints.get(field, "Please search the annual report 2025.")


def _parse_response(response: str, field: str) -> Optional[Dict]:
    """
    解析 API 返回的 JSON 响应

    Args:
        response: API 原始响应
        field: 查询的字段名

    Returns:
        解析后的字典，如 {"FY 2025": value} 或 None
    """
    if not response:
        return None

    # 尝试提取 JSON 块
    json_match = re.search(r'\{[\s\S]*\}', response)
    if json_match:
        try:
            data = json.loads(json_match.group())
            # 确保返回的是包含该字段的字典
            if field in data:
                return data[field]
            # 如果 LLM 返回了整个对象，检查是否有匹配字段(不区分大小写)
            for k, v in data.items():
                if k.lower().replace(' ', '') == field.lower().replace(' ', ''):
                    return v
        except json.JSONDecodeError as e:
            print(f"JSON parse error for field {field}: {e}")
            print(f"Raw response: {response}")

    return None


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

    # 检查 extra
    if field in json_data.get('extra', {}):
        val = json_data['extra'][field]
        if val and isinstance(val, (int, float)):
            return False
        if isinstance(val, dict):
            if val.get('Current') or val.get('TTM'):
                return False

    return True


def _fill_single_field(json_data: Dict, ticker: str, industry: str, field: str) -> Dict:
    """
    填充单个字段

    Args:
        json_data: 原始财务数据
        ticker: 股票代码
        industry: 行业类型
        field: 需要填充的字段

    Returns:
        更新后的 json_data
    """
    # 再次检查字段是否已存在（可能被其他调用填充）
    if not _is_field_missing(json_data, field):
        print(f"  {field}: already exists, skip")
        return json_data

    print(f"  {field}: calling API...")

    # 构建单个字段的 prompt
    prompt = _build_single_field_prompt(ticker, industry, field)
    print(f"  {field}: prompt={prompt}")

    # 调用 API
    response = _call_api(prompt, field)
    print(f"  {field}: response={response[:200] if response else 'None'}...")
    if not response:
        print(f"  {field}: API call failed")
        return json_data

    # 解析响应
    filled_value = _parse_response(response, field)
    if filled_value is None:
        print(f"  {field}: failed to parse response")
        return json_data

    print(f"  {field}: got value {filled_value}")

    # 初始化 extra
    if 'extra' not in json_data:
        json_data['extra'] = {}

    # 填充数据
    json_data['extra'][field] = filled_value

    return json_data


def fill_missing_data(json_data: Dict, industry: str) -> Dict:
    """
    填充缺失的基础数据 - 唯一的公开接口

    对每个缺失字段进行独立的 API 调用，提高准确性。

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

    print(f"{ticker}: Found {len(missing_fields)} missing fields: {missing_fields}")

    # 对每个缺失字段独立调用 API
    for field in missing_fields:
        json_data = _fill_single_field(json_data, ticker, industry, field)

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
