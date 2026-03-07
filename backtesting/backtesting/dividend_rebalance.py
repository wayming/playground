import dataclasses
import datetime
import pandas as pd
import datetime
import logging
import collections
import matplotlib.pyplot as plt
import numpy as np
import yfinance
import pprint
import os
import warnings
import argparse
from requests.exceptions import RequestsDependencyWarning
import pandas as pd
from . import report
from .portfolio import *

warnings.simplefilter("ignore", RequestsDependencyWarning)

# 设置打印完整 DataFrame
pd.set_option('display.max_rows', None)  # 显示所有行
pd.set_option('display.max_columns', None)  # 显示所有列
pd.set_option('display.width', None)  # 不限制每行的宽度
pd.set_option('display.max_colwidth', None)  # 不限制列的宽度

def month_ranges(start :datetime.datetime, end : datetime.datetime):
    while(start < end):
        yield start
        
        year = start.year
        month = start.month + 1
        if month > 12:
            year += 1
            month = 1
        start = datetime.datetime(year, month, 1)
        
def year_ranges(start :datetime.datetime, end : datetime.datetime):
    while(start <= end):
        yield start
        start = start.replace(year=start.year+1)

def subtract_one_year(dt):
    try:
        return dt.replace(year=dt.year - 1)
    except ValueError:
        first_of_next_month = dt.replace(year=dt.year - 1, month=dt.month + 1, day=1)
        return first_of_next_month - datetime.timedelta(days=1)


def back_testing_yh_finance(star_date:datetime.datetime, symbols:str, initial_fund: int, years: str, config: Portfolio_Conifg = None, enable_rebalance: bool = True):

    # Populating dates
    warm_up_start_backtest_date = datetime.datetime(star_date.year -1, star_date.month, star_date.day)
    end_backtest_date = datetime.datetime(star_date.year + int(years.removesuffix('y')), star_date.month, star_date.day)
    start_of_last_backtest_year = datetime.datetime(end_backtest_date.year - 1, 1, 1)
    today = datetime.datetime.today()
    last_day_of_last_year = datetime.datetime(today.year - 1, 12, 31)

    stock_data = yfinance.Tickers(symbols)
    hist = stock_data.history(start=warm_up_start_backtest_date, end=last_day_of_last_year, interval='1d', auto_adjust=False).fillna(0)
    ma250_all_tickers = hist["Close"].rolling(window=365).mean()
    rolling_div_sum_all_tickers = hist['Dividends'].rolling(window=365).sum()
    yield_all_tickers = rolling_div_sum_all_tickers / hist['Close']

    ma250_all_tickers.columns = pd.MultiIndex.from_product([["MA250"], ma250_all_tickers.columns])
    rolling_div_sum_all_tickers.columns = pd.MultiIndex.from_product([["RollingDivSum250"], rolling_div_sum_all_tickers.columns])
    yield_all_tickers.columns = pd.MultiIndex.from_product([["Yield"], yield_all_tickers.columns])
    hist = pd.concat([hist, ma250_all_tickers, yield_all_tickers, rolling_div_sum_all_tickers], axis=1)
    logging.info("\n" + hist[["Close", "Dividends", "MA250", "Yield", "RollingDivSum250"]].to_string())

    end_of_years_market_data = hist[["Close", "Yield"]].ffill().loc[start_of_last_backtest_year:].resample('YE').last()
    end_of_years_makert_data_map = {}
    for date, row in end_of_years_market_data.iterrows():
        end_of_years_makert_data_map[date] = {
            ticker: {
                "Close": row["Close"][ticker],
                "Yield": row["Yield"][ticker]
            }
            for ticker in row["Close"].index
            if pd.notna(row["Close"][ticker]) and pd.notna(row["Yield"][ticker])
        }
    logging.info(f"End of years market data: \n{end_of_years_market_data}")
    logging.info(f"End of years market data: \n{pprint.pformat(end_of_years_makert_data_map)}")
    
    if config is None:
        config = Portfolio_Conifg()
    config.initial_fund = initial_fund
    portfolio = Portfolio(config)
    portfolio.add_cash(star_date, initial_fund)
    portfolio.add_balance_strategy(AverageDownByMA250Strategy(stock_data.symbols))
    portfolio.add_balance_strategy(TakeProfitPercentageStrategy(config.take_profit_ratio, config.take_profit_sell_ratio))

    # 历史记录 DataFrame
    history = []
    prev_equity_total = None

    for date, row in hist[["Close", "Dividends", "MA250", "Yield"]].loc[star_date:end_backtest_date].iterrows():

        market_data_map = (
            pd.DataFrame({
                "Close": row["Close"],
                "MA250": row["MA250"],
                "Yield": row["Yield"]
            })
            .to_dict("index")
        )
        logging.debug(f"Market data for {date}: {market_data_map}")
        dividend_map = row["Dividends"].fillna(0).to_dict()
        logging.debug(f"Dividend data for {date}: {dividend_map}")
        if initial_fund > 0:
            portfolio.initial_equity(date, initial_fund, market_data_map)
            portfolio.rebalance(date, market_data_map)
            initial_fund = 0
            # 记录初始状态
            position_value = sum(h.position_value for _, h in portfolio.stock_holding.items())
            equity_total = position_value + portfolio.cash
            history.append({
                "date": date,
                "position_value": position_value,
                "cash": portfolio.cash,
                "equity_total": equity_total,
                "dividend_received": 0,
                "exposure": position_value / equity_total if equity_total > 0 else 0
            })
            prev_equity_total = equity_total
            continue
            
        # 分红
        dividend_received = 0
        for sym, divid in dividend_map.items():
            if divid > 0:
                portfolio.dividend(date, sym, divid, market_data_map)
                dividend_received += portfolio.stock_holding.get(sym, Holding(sym)).shares * divid

        # 根据enable_rebalance参数决定是否进行rebalance（止盈、场外加购等）
        extra_fund_required = 0
        if enable_rebalance:
            # 如果启用rebalance，则调用rebalance（止盈和场外加购）
            extra_fund_required = portfolio.rebalance(date, market_data_map)
        
        if extra_fund_required > 0:
            portfolio.add_cash(date, extra_fund_required)
            portfolio.rebalance(date, market_data_map)

        # 记录每日状态
        position_value = sum(h.position_value for sym, h in portfolio.stock_holding.items())
        equity_total = position_value + portfolio.cash
        drawdown = 0
        if prev_equity_total and equity_total < prev_equity_total:
            drawdown = (prev_equity_total - equity_total) / prev_equity_total
        history.append({
            "date": date,
            "position_value": position_value,
            "cash": portfolio.cash,
            "equity_total": equity_total,
            "dividend_received": dividend_received,
            "exposure": position_value / equity_total if equity_total > 0 else 0,
            "drawdown": drawdown
        })
        prev_equity_total = max(prev_equity_total, equity_total)  # 历史高点用于计算回撤

    portfolio.show()

    # Populate end stats
    portfolio.stats(end_of_years_makert_data_map)

    return pd.DataFrame(history).set_index("date"), portfolio

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Stock Backtesting with Dividend Reinvestment')
    parser.add_argument('-debug', action='store_true', help='Enable debug logging')
    parser.add_argument('-start', type=int, default=2005, help='Rolling backtest start year (default: 2005)')
    parser.add_argument('-end', type=int, default=2016, help='Rolling backtest end year (default: 2016)')
    parser.add_argument('-period', type=str, default='10y', help='Single backtest period (default: 10y)')
    parser.add_argument('-rebalance', action='store_true', help='Enable take profit and average down (default: False)')
    parser.add_argument('-output', type=str, default='output', help='Output directory (default: output)')
    parser.add_argument('-symbols', type=str, default='BHP.AX CBA.AX WES.AX WDS.AX TCL.AX', help='Stock symbols separated by space (default: "BHP.AX CBA.AX WES.AX WDS.AX TCL.AX")')
    parser.add_argument('-initial_fund', type=int, default=100000, help='Initial fund amount (default: 100000)')
    args = parser.parse_args()
    
    # 根据debug参数调整日志级别
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.info("Debug logging enabled")
    
    # 设置输出目录
    output_dir = os.path.join(os.getcwd(), args.output)
    os.makedirs(output_dir, exist_ok=True)
    
    # 设置日志文件路径
    log_file = os.path.join(output_dir, f"{args.start}_{args.end}_{args.period}_rollingbacktest.log")
    # 重新配置日志（因为之前可能已经配置过了）
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(filename=log_file, level=logging.DEBUG if args.debug else logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # 从start年到end年，每月一个起点，每个测试period
    start = datetime.datetime(args.start, 1, 1)
    end = datetime.datetime(args.end, 1, 1)
    period = args.period
    
    today = datetime.datetime.today()
    first_day_of_current_year = datetime.datetime(today.year, 1, 1)
    last_year_of_today = today.year - 1
    end_year = end.year

    logging.info(f"Configuration: debug={args.debug}, start={args.start}, end={args.end}, period={period}, rebalance={args.rebalance}, output={args.output}, symbols='{args.symbols}', initial_fund={args.initial_fund}")
    
    rolling_results = []
    
    # 预加载所有年份的分红数据（用于预测）
    all_symbols = args.symbols
    stock_data = yfinance.Tickers(all_symbols)
    full_hist = stock_data.history(start=start, end=first_day_of_current_year, interval='1d')
    
    # 计算每年的分红总额
    yearly_div = {}
    for date, row in full_hist["Dividends"].iterrows():
        year = date.year
        if year not in yearly_div:
            yearly_div[year] = {}
        for sym, divid in row.items():
            if pd.notna(divid) and divid > 0:
                if sym not in yearly_div[year]:
                    yearly_div[year][sym] = 0
                yearly_div[year][sym] += divid
    
    for d in year_ranges(start, end):
        logging.info(f"\n=== Running backtest for start date: {d.strftime('%Y-%m-%d')} ===")
        # 使用默认配置，将rebalance参数传递给back_testing_yh_finance
        config = Portfolio_Conifg()
        logging.info(f"Configuration: \n{config.export()}")
        if not args.rebalance:
            logging.info("Rebalancing disabled: only dividend reinvestment")
        else:
            logging.info("Rebalancing enabled: take profit and average down")
        
        history, portfolio = back_testing_yh_finance(d, all_symbols, args.initial_fund, period, config, args.rebalance)
        
        # 为每个起点生成单独的 backtest_report（不覆盖）
        output = os.path.join(output_dir, f"backtest_{d.strftime('%Y%m%d')}.png")
        report.plot_report(history, title=f"Backtest: Start {d.strftime('%Y-%m-%d')}, {period}", output=output)
        
        # 计算关键指标
        if not history.empty:
            initial_equity = history["equity_total"].iloc[0]
            final_equity = history["equity_total"].iloc[-1]
            total_return = (final_equity - initial_equity) / initial_equity
            
            # 计算 CAGR（使用实际总投资额）
            years = (history.index[-1] - history.index[0]).days / 365.25
            total_invest = portfolio.total_invest
            cagr = (final_equity / total_invest) ** (1/years) - 1 if years > 0 and total_invest > 0 else 0
            
            # 计算 Max Drawdown
            rolling_max = history["equity_total"].cummax()
            drawdown = (history["equity_total"] - rolling_max) / rolling_max
            max_drawdown = drawdown.min()
            
            # 累计分红
            total_dividend = history["dividend_received"].sum()
            
            # 预测分红：期末 shares × last year 年分红（最新的完整年份分红数据）
            predicted_div = 0
            if last_year_of_today in yearly_div:
                for sym, h in portfolio.stock_holding.items():
                    if sym in yearly_div[last_year_of_today]:
                        predicted_div += h.shares * yearly_div[last_year_of_today][sym]

            # Dividend yield of the end year
            last_year_dividend = 0
            if end_year in yearly_div:
                for sym, h in portfolio.stock_holding.items():
                    if sym in yearly_div[end_year]:
                        last_year_dividend += h.shares * yearly_div[end_year][sym]

            rolling_results.append({
                "start_date": d,
                "initial_equity": initial_equity,
                "final_equity": final_equity,
                "total_return": total_return,
                "cagr": cagr,
                "max_drawdown": max_drawdown,
                "total_dividend": total_dividend,
                "predicted_dividend": predicted_div,
                "last_year_dividend": last_year_dividend,
                "total_invest": total_invest,
                "years": years
            })
            logging.info(f"Start: {d.strftime('%Y-%m-%d')}, CAGR: {cagr:.2%}, MaxDD: {max_drawdown:.2%}, Total Div: {total_dividend:.0f}, Predicted: {predicted_div:.0f}")
    
    # 绘制 rolling 结果分布图
    if rolling_results:
        output = os.path.join(output_dir, "rolling_backtest_report.png")
        report.plot_rolling_results(rolling_results, output)
