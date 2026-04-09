#!/usr/bin/env python3
"""
ASX Stock Financial Data Scraper
从 stockanalysis.com 抓取澳洲股票财务数据
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import sys
import os
import argparse
from typing import Dict, Any, Optional

# 导入日志模块
from logger import logger, set_ticker

# 导入 Gemini 数据补充模块
try:
    from gemini_filler import fill_missing_data as gemini_fill
except ImportError:
    gemini_fill = None
    print("Warning: gemini_filler not available")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

BASE_URL = "https://stockanalysis.com/quote/asx"


def fetch_page(url: str) -> Optional[BeautifulSoup]:
    """获取页面并解析为BeautifulSoup对象"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return None


def parse_financial_table(soup: BeautifulSoup) -> Dict[str, Any]:
    """解析财务表格数据"""
    data = {}

    # 查找所有表格
    tables = soup.find_all('table')

    for table in tables:
        # 获取表头（年份）
        headers = []
        thead = table.find('thead')
        if thead:
            header_rows = thead.find_all('tr')
            for row in header_rows:
                cols = row.find_all(['th', 'td'])
                for col in cols:
                    text = col.get_text(strip=True)
                    if text:
                        headers.append(text)

        # 获取数据行
        tbody = table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            for row in rows:
                cols = row.find_all(['th', 'td'])
                if cols:
                    # 第一列是指标名称
                    metric_name = cols[0].get_text(strip=True)
                    if metric_name:
                        values = {}
                        for i, col in enumerate(cols[1:], start=1):
                            if i < len(headers):
                                value = col.get_text(strip=True)
                                # 清理数值
                                value = clean_value(value)
                                if value is not None:
                                    values[headers[i]] = value

                        if values:
                            data[metric_name] = values

    return data


def parse_ratio_table(soup: BeautifulSoup) -> Dict[str, Any]:
    """解析比率表格数据"""
    data = {}

    tables = soup.find_all('table')

    for table in tables:
        # 获取表头
        headers = []
        thead = table.find('thead')
        if thead:
            header_rows = thead.find_all('tr')
            for row in header_rows:
                cols = row.find_all(['th', 'td'])
                for col in cols:
                    text = col.get_text(strip=True)
                    if text:
                        headers.append(text)

        # 获取数据行
        tbody = table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            for row in rows:
                cols = row.find_all(['th', 'td'])
                if cols:
                    metric_name = cols[0].get_text(strip=True)
                    if metric_name:
                        values = {}
                        for i, col in enumerate(cols[1:], start=1):
                            if i < len(headers):
                                value = col.get_text(strip=True)
                                value = clean_value(value)
                                if value is not None:
                                    values[headers[i]] = value

                        if values:
                            data[metric_name] = values

    return data


def clean_value(value: str) -> Any:
    """清理并转换数值"""
    if not value or value == '-' or value == '':
        return None

    # 移除逗号和美元符号
    value = value.replace(',', '').replace('$', '').replace('%', '')

    # 处理括号（负数）
    is_negative = False
    if value.startswith('(') and value.endswith(')'):
        is_negative = True
        value = value[1:-1]

    # 尝试转换为数字
    try:
        # 处理百万/十亿后缀
        multiplier = 1
        if 'B' in value.upper():
            multiplier = 1_000_000_000
            value = value.upper().replace('B', '')
        elif 'M' in value.upper():
            multiplier = 1_000_000
            value = value.upper().replace('M', '')

        num = float(value) * multiplier
        if is_negative:
            num = -num
        return num
    except ValueError:
        # 如果不是数字，返回原始字符串
        return value


def parse_industry(soup: BeautifulSoup) -> Dict[str, str]:
    """解析股票主页面获取行业和板块信息"""
    industry_info = {'industry': None, 'sector': None}

    # 查找包含 "Industry" 的元素
    # stockanalysis.com 页面结构中，行业信息在特定的链接文本中
    links = soup.find_all('a', href=True)

    for link in links:
        href = link.get('href', '')
        text = link.get_text(strip=True)

        # 查找 Industry 链接
        if '/stocks/industry/' in href and text:
            industry_info['industry'] = text

        # 查找 Sector 链接
        if '/stocks/sector/' in href and text:
            industry_info['sector'] = text

    return industry_info


def scrape_stock(ticker: str) -> Dict[str, Any]:
    """抓取单个股票的所有财务数据"""
    ticker = ticker.upper().replace('.AX', '')
    url_ticker = ticker

    # 设置 ticker 用于日志
    set_ticker(ticker)
    logger.info(f"Starting scrape for {ticker}")

    result = {
        'ticker': f"{ticker}.AX",
        'source': 'stockanalysis.com',
        'industry': {},
        'income_statement': {},
        'balance_sheet': {},
        'cash_flow': {},
        'ratios': {}
    }

    # 0. 股票主页面 - 获取行业信息
    url = f"{BASE_URL}/{url_ticker}/"
    soup = fetch_page(url)
    if soup:
        result['industry'] = parse_industry(soup)
        logger.info(f"Scraped industry info: {result['industry']}")

    # 1. 损益表
    url = f"{BASE_URL}/{url_ticker}/financials/"
    soup = fetch_page(url)
    if soup:
        result['income_statement'] = parse_financial_table(soup)
        logger.info(f"Scraped income_statement: {len(result['income_statement'])} items")

    # 2. 资产负债表
    url = f"{BASE_URL}/{url_ticker}/financials/balance-sheet/"
    soup = fetch_page(url)
    if soup:
        result['balance_sheet'] = parse_financial_table(soup)
        logger.info(f"Scraped balance_sheet: {len(result['balance_sheet'])} items")

    # 3. 现金流表
    url = f"{BASE_URL}/{url_ticker}/financials/cash-flow-statement/"
    soup = fetch_page(url)
    if soup:
        result['cash_flow'] = parse_financial_table(soup)
        logger.info(f"Scraped cash_flow: {len(result['cash_flow'])} items")

    # 4. 财务比率
    url = f"{BASE_URL}/{url_ticker}/financials/ratios/"
    soup = fetch_page(url)
    if soup:
        result['ratios'] = parse_ratio_table(soup)
        logger.info(f"Scraped ratios: {len(result['ratios'])} items")

    # 5. 尝试使用 Gemini API 补充缺失数据
    industry_info = result.get('industry', {})
    industry_name = industry_info.get('industry', '')
    sector = industry_info.get('sector', '')

    # 根据行业名称映射到内部类型
    internal_industry = map_industry_for_filler(industry_name, sector)

    if gemini_fill and os.environ.get('GEMINI_API_KEY') and internal_industry:
        logger.info(f"Calling Gemini to fill missing data for {ticker}")
        result = gemini_fill(result, internal_industry)
        logger.info(f"Gemini fill completed for {ticker}")

    logger.info(f"Scraping completed for {ticker}")
    return result


def map_industry_for_filler(industry_name: str, sector: str) -> Optional[str]:
    """将行业名称映射到内部行业类型 (用于 Gemini 数据补充)"""
    text = f"{industry_name} {sector}".lower()

    if any(kw in text for kw in ['bank', 'financial']):
        return 'banks'
    if any(kw in text for kw in ['basic materials', 'metal', 'mining', 'gold', 'coal', 'material']):
        return 'materials'
    if any(kw in text for kw in ['utilities', 'energy', 'oil', 'gas', 'infrastructure']):
        return 'infrastructure'
    if any(kw in text for kw in ['healthcare', 'biotechnology', 'pharmaceutical', 'medical']):
        return 'healthcare'
    if any(kw in text for kw in ['telecom', 'communication']):
        return 'telecom'
    if 'consumer' in text:
        return 'consumer_staples'

    return None


def main():
    global gemini_fill

    parser = argparse.ArgumentParser(description='抓取ASX股票财务数据')
    parser.add_argument('ticker', help='股票代码 (如 FMG)')
    parser.add_argument('-o', '--output', help='输出文件路径 (JSON格式)')
    parser.add_argument('-p', '--pretty', action='store_true', help='格式化输出JSON')
    parser.add_argument('--no-ai', action='store_true', help='禁用所有 AI 数据补充')
    parser.add_argument('-d', '--debug', action='store_true', help='开启调试日志')

    args = parser.parse_args()

    # 如果设置了 --debug，开启调试日志
    if args.debug:
        import logging
        logger.setLevel(logging.DEBUG)
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)

    # 如果设置了 --no-ai，禁用 AI
    if args.no_ai:
        # 临时清除环境变量，让 scrape_stock 中的检查失败
        os.environ.pop('GEMINI_API_KEY', None)

    print(f"抓取 {args.ticker} 的财务数据...")

    # 显示 AI 补充状态
    if gemini_fill and os.environ.get('GEMINI_API_KEY'):
        print("Gemini AI 数据补充: 启用")
    else:
        print("Gemini AI 数据补充: 禁用 (需要设置 GEMINI_API_KEY)")

    data = scrape_stock(args.ticker)

    # 输出
    indent = 2 if args.pretty else None
    json_str = json.dumps(data, indent=indent, ensure_ascii=False)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(json_str)
        print(f"数据已保存到 {args.output}")
    else:
        print(json_str)

    # 打印摘要
    print(f"\n摘要:")
    industry_info = data.get('industry', {})
    if industry_info.get('industry'):
        print(f"  - 行业: {industry_info['industry']}")
        print(f"  - 板块: {industry_info['sector']}")
    print(f"  - 损益表指标: {len(data.get('income_statement', {}))}")
    print(f"  - 资产负债表指标: {len(data.get('balance_sheet', {}))}")
    print(f"  - 现金流表指标: {len(data.get('cash_flow', {}))}")
    print(f"  - 财务比率指标: {len(data.get('ratios', {}))}")


if __name__ == '__main__':
    main()
