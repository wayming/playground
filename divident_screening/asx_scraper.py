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
import argparse
from typing import Dict, Any, Optional

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


def scrape_stock(ticker: str) -> Dict[str, Any]:
    """抓取单个股票的所有财务数据"""
    ticker = ticker.upper().replace('.AX', '')
    url_ticker = ticker

    result = {
        'ticker': f"{ticker}.AX",
        'source': 'stockanalysis.com',
        'income_statement': {},
        'balance_sheet': {},
        'cash_flow': {},
        'ratios': {}
    }

    # 1. 损益表
    url = f"{BASE_URL}/{url_ticker}/financials/"
    soup = fetch_page(url)
    if soup:
        result['income_statement'] = parse_financial_table(soup)

    # 2. 资产负债表
    url = f"{BASE_URL}/{url_ticker}/financials/balance-sheet/"
    soup = fetch_page(url)
    if soup:
        result['balance_sheet'] = parse_financial_table(soup)

    # 3. 现金流表
    url = f"{BASE_URL}/{url_ticker}/financials/cash-flow-statement/"
    soup = fetch_page(url)
    if soup:
        result['cash_flow'] = parse_financial_table(soup)

    # 4. 财务比率
    url = f"{BASE_URL}/{url_ticker}/financials/ratios/"
    soup = fetch_page(url)
    if soup:
        result['ratios'] = parse_ratio_table(soup)

    return result


def main():
    parser = argparse.ArgumentParser(description='抓取ASX股票财务数据')
    parser.add_argument('ticker', help='股票代码 (如 FMG)')
    parser.add_argument('-o', '--output', help='输出文件路径 (JSON格式)')
    parser.add_argument('-p', '--pretty', action='store_true', help='格式化输出JSON')

    args = parser.parse_args()

    print(f"抓取 {args.ticker} 的财务数据...")
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
    print(f"  - 损益表指标: {len(data.get('income_statement', {}))}")
    print(f"  - 资产负债表指标: {len(data.get('balance_sheet', {}))}")
    print(f"  - 现金流表指标: {len(data.get('cash_flow', {}))}")
    print(f"  - 财务比率指标: {len(data.get('ratios', {}))}")


if __name__ == '__main__':
    main()
