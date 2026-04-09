#!/usr/bin/env python3
"""
统一日志模块
为 app.py, asx_scraper.py, gemini_filler.py 提供日志功能
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from contextvars import ContextVar
from datetime import datetime

# Context variable for storing ticker
_ticker_context: ContextVar[str] = ContextVar('ticker', default='')

# Log directory - use workspace/logs
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, 'app.log')


class TickerFilter(logging.Filter):
    """自定义 Filter，将 ticker 添加到日志记录中"""

    def filter(self, record):
        record.ticker = _ticker_context.get() or 'SYSTEM'
        return True


def setup_logger(name: str = 'asx_scraper') -> logging.Logger:
    """
    获取 logger 实例

    Args:
        name: logger 名称

    Returns:
        配置好的 logger
    """
    logger = logging.getLogger(name)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # 文件 handler - 使用 RotatingFileHandler
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)

    # 控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 日志格式
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(ticker)s] %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 添加 ticker filter
    ticker_filter = TickerFilter()
    file_handler.addFilter(ticker_filter)
    console_handler.addFilter(ticker_filter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def set_ticker(ticker: str):
    """设置当前 ticker (用于日志前缀)"""
    _ticker_context.set(ticker.upper())


def get_ticker() -> str:
    """获取当前 ticker"""
    return _ticker_context.get()


# 默认 logger
logger = setup_logger('asx_scraper')
