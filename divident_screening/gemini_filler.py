#!/usr/bin/env python3
"""
Google Gemini API Integration for Financial Data Filling
当 stockanalysis.com 数据缺失时，使用 Gemini API 补充基础数据

使用 LangChain 实现两步文档搜索:
1. 先搜索相关文档链接
2. 把链接加入 prompt，再提取数据

重构: 使用 LangChain + Google Generative AI
"""

import os
import json
import re
import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from typing import Dict, Any, Optional, List

# 导入日志模块
from logger import logger, set_ticker

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# 行业特定的缺失指标 - 需要通过 Gemini 搜索的基础数据
INDUSTRY_MISSING_FIELDS = {
    'banks': [
        'CET1 Ratio',
        'Common Equity Tier 1 Capital',
        'Risk Weighted Assets',
        'Group Average LVR',
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

# 行业特定的金融文档类型
INDUSTRY_SPECIFIC_FINANCIAL_DOCS = {
    'banks': [
        'most recent annual report',
        'most recent quarter report',
        'Pillar3 report',
        'Stratification Tables Investor Report'
    ],
    'materials': [
        'annual report',
        'quarterly report',
        'production report'
    ],
    'infrastructure': [
        'annual report',
        'quarterly report',
        'investor presentation'
    ],
    'consumer_staples': [
        'annual report',
        'quarterly report'
    ],
}

# 模型配置
MODEL_NAME = 'gemini-flash-latest'

TODAY = datetime.date.today()
THIS_YEAR = TODAY.year
LAST_YEAR = THIS_YEAR - 1

def _get_llm():
    """获取 LangChain LLM 实例"""
    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not set")
        return None

    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=GEMINI_API_KEY,
        temperature=0.1,
        max_output_tokens=4096,
        response_mime_type="application/json",
    )
    # 启用 Google Search
    llm = llm.bind_tools([{"google_search": {}}])
    return llm


def _get_search_fields(industry: str) -> List[str]:
    """获取指定行业需要搜索的基础字段列表"""
    return INDUSTRY_MISSING_FIELDS.get(industry, [])


def _get_doc_types(industry: str) -> List[str]:
    """获取指定行业需要搜索的文档类型"""
    return INDUSTRY_SPECIFIC_FINANCIAL_DOCS.get(industry, [])


def _search_document_links(ticker: str, industry: str, llm: ChatGoogleGenerativeAI) -> List[str]:
    """
    第一步：搜索相关文档链接

    Args:
        ticker: 股票代码
        industry: 行业类型
        llm: LangChain LLM 实例

    Returns:
        文档链接列表
    """
    doc_types = _get_doc_types(industry)
    if not doc_types:
        return []

    doc_types_str = ', '.join(doc_types)

    prompt = f"""
#######################################################
# Role
你是一个精通 ASX (澳洲证券交易所) 披露规则的金融数据专家。

# Context
今天的日期是 {TODAY}。你需要获取 {ticker} 最新的合规披露文件。

# Task
1. 必须使用网络搜索功能查找 {ticker} 投资者关系官网 (Shareholder Center)。
2. 寻找以下四类【最新】文件的有效 PDF 链接：
   - {LAST_YEAR} 或 {THIS_YEAR} 年的 Annual Report (或最近的 Half Year Report)
   - 最近一期的 Trading Update (对应 Quarter Report)
   - 最新的 APS 330 / Pillar 3 Disclosure
   - 最新的 RMBS/Covered Bond Stratification Tables (Investor Report)

# Constraints
- 仅限 {LAST_YEAR} 至 {TODAY} 之间发布的文档。
- 如果找不到直连 PDF，请提供该文件所在的网页 URL。
- 必须验证 URL 的真实性，严禁虚构。

# Output Format
仅返回 URLs 列表，每行一个 URL。
格式：[文件名]: [URL]
找不到则标注为 "NOT FOUND"。
#######################################################
    """

    logger.info(f"Searching document links for {ticker} ({industry})...")

    content = _call_api(prompt, "doc_links", llm)
    if not content:
        return []

    # 解析 URLs
    urls = []
    for line in content.strip().split('\n'):
        line = line.strip()
        if line.startswith('http://') or line.startswith('https://'):
            urls.append(line)
        elif line and line != 'NOT FOUND':
            # 尝试提取 URL
            url_match = re.search(r'https?://[^\s]+', line)
            if url_match:
                urls.append(url_match.group())

    logger.info(f"Found {len(urls)} document links for {ticker}")
    if not urls:
        logger.debug(f"Raw response content: {content}...")
    for url in urls:
        logger.debug(f"  - {url}")

    return urls


def _build_single_field_prompt(ticker: str, industry: str, field: str, doc_links: Optional[List[str]] = None) -> str:
    """
    为单个字段构建查询 Prompt

    Args:
        ticker: 股票代码
        industry: 行业类型
        field: 需要查询的字段名
        doc_links: 可选的文档链接列表
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
        'CET1 Ratio': 'CET1 Ratio (一级资本充足率)，银行的核心一级资本除以风险加权资产',
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

    # 添加文档链接到 prompt
    doc_link_section = ""
    if doc_links:
        doc_link_section = f"""
# Available Documents
请优先从以下文档中查找数据:
{chr(10).join(f'- {url}' for url in doc_links)}
"""

    prompt = f"""
# Role
你是一个专业的金融数据分析师，严谨且只输出机器可读的结构化数据。

# Task
Extract the following required data from financial reports for:
股票代码: {ticker}
行业: {industry_context.get(industry, industry)}

# Data Field
{field}
说明: {context}

{doc_link_section}
# Constraints
1. 缺失处理：如果数据不存在，对应 value 必须填 null。
2. 单位: 转换成百万为单位。对于百分比字段，输出数值(如 45.5 表示 45.5%)。
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

# Hints
{_get_search_hint(field)}

    """
    return prompt


def _call_api(prompt: str, field: str, llm: ChatGoogleGenerativeAI) -> Optional[str]:
    """
    调用 LangChain LLM API

    Args:
        prompt: 查询提示词
        field: 查询的字段名（用于调试）
        llm: LangChain LLM 实例
    """
    if not llm:
        logger.warning("LLM not initialized")
        return None

    try:
        messages = [HumanMessage(content=prompt)]
        logger.debug(f"Prompt: {prompt}...")

        response = llm.invoke(messages)

        # 处理响应 - 可能是字符串或列表
        if hasattr(response, 'content'):
            content = response.content
        else:
            content = str(response)

        # 处理 LangChain 返回的响应格式: [{'type': 'text', 'text': '...'}]
        if isinstance(content, list) and len(content) > 0:
            first_item = content[0]
            if isinstance(first_item, dict) and 'text' in first_item:
                content = first_item['text']
            else:
                content = str(first_item)
        elif isinstance(content, list):
            content = ""

        logger.debug(f"  {field}: response={content if content else 'None'}...")
        return content
    except Exception as e:
        logger.error(f"Error calling Gemini API for field {field}: {e}")
        return None


def _get_search_hint(field: str) -> str:
    """
    根据字段名返回搜索提示，帮助 LLM 找到正确的数据源
    """
    hints = {
        'CET1 Ratio': "search from 'Pillar 3 Disclosure' or 'FY2025 annual report'",
        'Common Equity Tier 1 Capital': "search from 'Pillar 3 Disclosure' or 'FY2025 annual report'",
        'Risk Weighted Assets': "search for 'Risk Weighted Assets' or 'RWA' from 'FY2025 annual report'",
        'Group Average LVR': "search for 'Group Average LVR' or 'mortgage LVR' from 'FY2025 annual report' or 'Stratification Tables Investor Report'",
        'Annual Production Volume': "search for 'FMG annual report 2025 production volume'",
        'Total Proved Reserves': "search for 'BHP proved reserves 2025' or 'RIO Tinto reserves 2025'",
        'Sustaining Capex': "search for 'sustaining capital expenditure' in annual report",
        'CPI Linkage': "search for 'CPI linkage percentage' in infrastructure fund annual report",
        'Weighted Average Contract Expiry': "search for 'WACE' or 'weighted average contract expiry' in annual report",
        'Total Industry Revenue': "search for 'total industry revenue' or 'market size' for the sector",
        'Forward EPS': "search for 'forward EPS 2026' or 'analyst consensus EPS'",
    }
    return hints.get(field, "search the annual report 2025.")


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
            logger.warning(f"JSON parse error for field {field}: {e}")
            logger.debug(f"Raw response: {response}")

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


def _fill_single_field(json_data: Dict, ticker: str, industry: str, field: str, llm: ChatGoogleGenerativeAI, doc_links: Optional[List[str]] = None) -> Dict:
    """
    填充单个字段

    Args:
        json_data: 原始财务数据
        ticker: 股票代码
        industry: 行业类型
        field: 需要填充的字段
        llm: LangChain LLM 实例
        doc_links: 可选的文档链接列表

    Returns:
        更新后的 json_data
    """
    # 再次检查字段是否已存在（可能被其他调用填充）
    if not _is_field_missing(json_data, field):
        logger.debug(f"  {field}: already exists, skip")
        return json_data

    logger.info(f"  {field}: calling Gemini API...")

    if not llm:
        logger.warning(f"  {field}: LLM not available")
        return json_data

    # 构建单个字段的 prompt
    prompt = _build_single_field_prompt(ticker, industry, field, doc_links)

    # 调用 API
    response = _call_api(prompt, field, llm)
    if not response:
        logger.warning(f"  {field}: API call failed")
        return json_data

    # 解析响应
    filled_value = _parse_response(response, field)
    if filled_value is None:
        logger.warning(f"  {field}: failed to parse response")
        return json_data

    logger.info(f"  {field}: successfully filled with value {filled_value}")

    # 初始化 extra
    if 'extra' not in json_data:
        json_data['extra'] = {}

    # 填充数据
    json_data['extra'][field] = filled_value

    return json_data


def fill_missing_data(json_data: Dict, industry: str) -> Dict:
    """
    填充缺失的基础数据 - 唯一的公开接口

    使用两步搜索:
    1. 先搜索相关文档链接
    2. 把链接加入 prompt，再提取数据

    Args:
        json_data: 包含财务数据的字典
        industry: 行业类型 (banks/materials/infrastructure/healthcare/telecom/consumer_staples)

    Returns:
        更新后的 json_data
    """
    ticker = json_data.get('ticker', '').replace('.AX', '')

    # 设置 ticker 用于日志
    set_ticker(ticker)
    logger.info(f"Starting fill_missing_data for {ticker} (industry: {industry})")

    # 获取 LLM 实例
    llm = _get_llm()
    if not llm:
        logger.error("LLM not available, cannot fill missing data")
        return json_data

    # 获取行业需要搜索的字段
    search_fields = _get_search_fields(industry)

    if not search_fields:
        logger.warning(f"No search fields defined for industry {industry}")
        return json_data

    # 识别缺失的字段
    missing_fields = [f for f in search_fields if _is_field_missing(json_data, f)]

    if not missing_fields:
        logger.info(f"No missing fields for industry {industry}")
        return json_data

    logger.info(f"Found {len(missing_fields)} missing fields: {missing_fields}")

    # 第一步：搜索文档链接
    doc_links = _search_document_links(ticker, industry, llm)

    # 第二步：对每个缺失字段独立调用 API
    for field in missing_fields:
        json_data = _fill_single_field(json_data, ticker, industry, field, llm, doc_links)

    logger.info(f"fill_missing_data completed for {ticker}")
    return json_data


def main():
    """测试入口"""
    import argparse

    parser = argparse.ArgumentParser(description='使用 Gemini API 补充财务数据')
    parser.add_argument('ticker', help='股票代码 (如 CBA)')
    parser.add_argument('--industry', default='banks', help='行业类型')
    parser.add_argument('--api-key', help='Gemini API Key (或设置 GEMINI_API_KEY 环境变量)')
    parser.add_argument('-d', '--debug', action='store_true', help='开启调试日志')

    args = parser.parse_args()

    # 如果设置了 --debug，开启调试日志
    if args.debug:
        import logging
        logger.setLevel(logging.DEBUG)
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)

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
