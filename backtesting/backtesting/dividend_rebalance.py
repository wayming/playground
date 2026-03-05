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
from .strategy import Holding, OPERATION_BUY, OPERATION_SELL
from .strategy import TradingStrategy, TakeProfitPercentageStrategy, AverageDownStrategy, CashSplitEvenlyStrategy

warnings.simplefilter("ignore", RequestsDependencyWarning)

# 设置打印完整 DataFrame
pd.set_option('display.max_rows', None)  # 显示所有行
pd.set_option('display.max_columns', None)  # 显示所有列
pd.set_option('display.width', None)  # 不限制每行的宽度
pd.set_option('display.max_colwidth', None)  # 不限制列的宽度

def parse_date(date_str: str):
    date_formats = ["%d %b %Y", "%d %B %Y"]
    for f in date_formats:
        try:
            date = datetime.datetime.strptime(date_str, f)
            return date
        except ValueError:
            logging.warning(f"Invalid date format {date_str}, try another format")
    raise ValueError(f"Can not parse date string {date_str}")

def yahoo_finance_csv_loader(sym: str):
    dividends = collections.OrderedDict()
    prices = []
    all_columns = []
    with open(sym + ".txt") as f:
        header_line = next(f).replace("Adj Close", "AdjClose")
        all_columns = header_line.split()
        for line in f:
            line = line.strip()
            if not line:
                continue
            line = line.replace("Sept", "Sep")
            if "Dividend" in line:
                parts = line.split()
                date = parse_date(" ".join(parts[:3]))
                dividends[date] = float(parts[3])
            else:
                parts = line.split()
                price = []
                assert len(parts) == 9, f"Invalid format of the price line at {sym}.txt, line {line}"
                price.append(parse_date(" ".join(parts[:3])))
                price.extend([float(x) for x in parts[3:8]])
                price.append(parts[8].replace(",",""))
                prices.append(price)

    prices_df = pd.DataFrame(prices, columns=all_columns)
    prices_df.set_index('Date', inplace=True)
    prices_df.index = pd.to_datetime(prices_df.index, errors='coerce')
    
    div_df = pd.DataFrame.from_dict(dividends, orient="index", columns=["Dividend"])
    div_df.index.name = "Date"
    div_df.index = pd.to_datetime(div_df.index, errors='coerce')  # 转换日期格式
    
    all_columns += ["Dividend"]
    df = prices_df.join(div_df, how="outer")
    df.sort_index(inplace=True)
    df["Dividend"] = df["Dividend"].fillna(0)

    for col in all_columns[1:]:
        df[col] = df[col].astype(float)
    df["Symbol"] = sym

    return df

@dataclasses.dataclass
class Portfolio_Conifg:
    # Sell 20% when price doubled
    take_profit_ratio : float = 2
    take_profit_sell_ratio: float = 0.2
    
    # Buy with external fund when stock drops to avg_down_trigger_ratio to average down the holding price
    # Total fund is the percentage of stock that meet the critera multiply by the total market value after drop.
    avg_down_trigger_ratio: float = 0.6
    
    initial_fund: float = 100000
    
    floor_shares_rate:float = 0.2
    regular_investment_rate : float = 0.5

    

class Portfolio:
    def __init__(self, config:Portfolio_Conifg):
        self.stock_holding : dict[str, Holding] = {}
        self.total_invest = 0 # Excludes the divident investment
        self.cash = 0
        self.config = config
        self.balance_strategies : list[TradingStrategy] = []
        self.pending_operations : list[tuple[str, str, float]] = []
        self.cash_split_strategy : TradingStrategy = CashSplitEvenlyStrategy()
    def add_balance_strategy(self, strategy:TradingStrategy):
        self.balance_strategies.append(strategy)    
    
    def add_cash(self, date, cash: float):
        logging.info(f"[{date}] Transfer cash {cash}")
        self.cash += cash
        self.total_invest += cash

    def buy(self, date:datetime.date, symbol:str, shares:int, unit_price:float):
        if symbol not in self.stock_holding:
            holding = Holding(symbol = symbol)
            self.stock_holding[symbol] = holding
        
        holding = self.stock_holding[symbol]
        fund_to_use = shares * unit_price
        old_holing_price = holding.holding_price
        holding.holding_price = (holding.holding_price * holding.shares + fund_to_use)/(holding.shares + shares)
        holding.market_price = unit_price
        holding.position_value = holding.market_price * holding.shares
        if holding.shares == 0:
            # New buy
            holding.floor_shares = self.config.floor_shares_rate * shares

        holding.shares += shares
        holding.avg_down_price = holding.holding_price * self.config.avg_down_trigger_ratio # Price down
        holding.take_profit_price = holding.holding_price * self.config.take_profit_ratio # Price double
        holding.total_purchase_cost += fund_to_use
        logging.info(f"[{date}] Buy {symbol} at price {unit_price} with fund_to_use {fund_to_use}, get {shares} shares, old holding price at {old_holing_price}, new holding price at {holding.holding_price}")
        holding.buys[date] = {
            "fund": fund_to_use,
            "unit_price": unit_price,
            "shares": shares
        }
        self.cash -= fund_to_use
        pass
    
    def sell(self, date:datetime.date, symbol:str, sell_ratio:float, unit_price:float):
        if symbol not in self.stock_holding:
            raise KeyError(f"No holdings for {symbol}")
    
        holding = self.stock_holding[symbol]
        if holding.shares <= holding.floor_shares:
            logging.info(f"{symbol} reach floor shares {holding.floor_shares}, current shares {holding.shares}, no sell")
            return
        sell_shares = holding.shares * sell_ratio
        self.cash += sell_shares * unit_price
        holding.shares -= sell_shares
        holding.market_price = unit_price
        holding.position_value = holding.market_price * holding.shares
        logging.info(f"[{date}] Sell {symbol} shares {sell_shares} at {unit_price}, holding price {holding.market_price}, return cash {sell_shares * unit_price}")
        holding.sells[date] = {
            "shares": sell_shares,
            "unit_price": unit_price,
            "return_cash": sell_shares * unit_price
        }
        pass

    def dividend(self, date:datetime.date, symbol:str, dividen_per_share: float, closing_prices: dict = None):
        if symbol not in self.stock_holding:
            raise KeyError(f"No holdings for {symbol}")

        if dividen_per_share == 0:
            return
        
        holding = self.stock_holding[symbol]
        dividend_cash = holding.shares * dividen_per_share
        
        # 收到分红现金
        holding.total_dividend_value += dividend_cash
        logging.info(f"Receive dividend for {symbol}, {dividen_per_share} per share, return cash {dividend_cash}")
        
        # 立即将分红现金用于再投资（如果有价格信息）
        if dividend_cash > 0 and closing_prices:
            for op, symbol, shares in self.cash_split_strategy.execute(date, dividend_cash, self.stock_holding, closing_prices):
                if op == OPERATION_BUY:
                    self.buy(date, symbol, shares, closing_prices[symbol])
                elif op == OPERATION_SELL:
                    raise ValueError("Cash split strategy should not sell")
        
        # 更新所有股票的市场价格
        if closing_prices:
            self.populate_market_prices(closing_prices)

    
    def rebalance(self, date:datetime.date, closing_prices: dict):
        cash_required = 0

        for strategy in self.balance_strategies:
            self.pending_operations.extend(strategy.execute(date, self.cash, self.stock_holding, closing_prices))
        
        buys = [op for op in self.pending_operations if op[0] == OPERATION_BUY]
        sells = [op for op in self.pending_operations if op[0] == OPERATION_SELL]
        print(sells)
        for _, symbol, shares in sells:
            self.sell(date, symbol, shares, closing_prices[symbol])
        
        for _, symbol, shares in buys:
            if symbol not in self.stock_holding:
                holding = Holding(symbol = symbol)
                self.stock_holding[symbol] = holding
                if self.cash < shares * closing_prices[symbol]:
                    cash_required += shares * closing_prices[symbol]
                    continue
                self.buy(date, symbol, shares, closing_prices[symbol])
        
        if self.cash > 0 and self.cash_split_strategy:
            for op, symbol, shares in self.cash_split_strategy.execute(date, self.cash, self.stock_holding, closing_prices):
                if op == OPERATION_BUY:
                    self.buy(date, symbol, shares, closing_prices[symbol])
                elif op == OPERATION_SELL:
                    raise ValueError("Cash split strategy should not sell")

        self.populate_market_prices(closing_prices)

        return cash_required
    
    def populate_market_prices(self, closing_prices: dict):
        for sym, unit_price in closing_prices.items():
            self.stock_holding[sym].market_price = unit_price
            self.stock_holding[sym].position_value = self.stock_holding[sym].shares * unit_price
            
    def stats(self, closing_prices:dict, predict_dividents:list):
        result_stats = {"holding": {}}
        total_stock_value = 0
        for symbol, holding in self.stock_holding.items():
            value = holding.shares * closing_prices[symbol]
            logging.info(f"{symbol}: {holding.shares}, value {value}")
            total_stock_value += value
            result_stats["holding"][symbol] ={
                "shares": holding.shares,
                "value": value
            }
        result_stats["total_value"] = total_stock_value
        result_stats["cash_remaining"] = self.cash
        result_stats["total_invest"] = self.total_invest
        result_stats["rate_of_return"] = round((total_stock_value - self.total_invest)/self.total_invest, 2)
        result_stats["total_predict_divident"] = self.estimate_divident(predict_dividents)

        logging.info(f"{pprint.pformat(result_stats)}")
        return result_stats
        
    def show(self):
        for symbol, holding in self.stock_holding.items():
            logging.info(holding.show())

    
    def estimate_divident(self, dividents:list):
        total_dividends = 0
        for row in dividents:
            for symbol, divid_per_share in row.items():
                if not pd.isna(divid_per_share) and divid_per_share > 0:
                    total_dividends += self.stock_holding[symbol].shares * divid_per_share
        logging.info(f"Estimate total dividents of the period {int(total_dividends)}")
        return total_dividends
    
def back_testing_yh_finance(star_date:str, symbols:str, initial_fund: int, years: str, config: Portfolio_Conifg = None, enable_rebalance: bool = True):
    stock_data = yfinance.Tickers(symbols)
    hist = stock_data.history(start=star_date, period=years, interval='1d')
    logging.debug(hist[["Close", "Dividends"]])

    today = datetime.datetime.today()
    last_year_first_day = datetime.datetime(today.year - 1, 1, 1)
    last_year_first_day.strftime("%Y-%m-%d")
    last_year_hist = stock_data.history(start=last_year_first_day, period='1y', interval='1d')
    
    if config is None:
        config = Portfolio_Conifg()
    config.initial_fund = initial_fund
    portfolio = Portfolio(config)
    portfolio.add_cash(star_date, initial_fund)
    portfolio.add_balance_strategy(AverageDownStrategy(config.avg_down_trigger_ratio, config.avg_down_trigger_ratio))
    portfolio.add_balance_strategy(TakeProfitPercentageStrategy(config.take_profit_ratio, config.take_profit_sell_ratio))

    # 历史记录 DataFrame
    history = []
    prev_equity = None

    for date, row in hist[["Close", "Dividends"]].iterrows():

        close_price_map = row["Close"].dropna().to_dict()
        dividend_map = row["Dividends"].fillna(0).to_dict()
        if initial_fund > 0:
            portfolio.rebalance(date, close_price_map)
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
            prev_equity = equity_total
            continue
            
        # 分红
        dividend_received = 0
        for sym, divid in dividend_map.items():
            if divid > 0:
                portfolio.dividend(date, sym, divid, close_price_map)
                dividend_received += portfolio.stock_holding.get(sym, Holding(sym)).shares * divid

        # 根据enable_rebalance参数决定是否进行rebalance（止盈、场外加购等）
        extra_fund_required = 0
        if enable_rebalance:
            # 如果启用rebalance，则调用rebalance（止盈和场外加购）
            extra_fund_required = portfolio.rebalance(date, close_price_map)
        
        if extra_fund_required > 0:
            portfolio.add_cash(date, extra_fund_required)
            portfolio.rebalance(date, close_price_map)

        # 记录每日状态
        position_value = sum(h.position_value for sym, h in portfolio.stock_holding.items())
        equity_total = position_value + portfolio.cash
        drawdown = 0
        if prev_equity and equity_total < prev_equity:
            drawdown = (prev_equity - equity_total) / prev_equity
        history.append({
            "date": date,
            "position_value": position_value,
            "cash": portfolio.cash,
            "equity_total": equity_total,
            "dividend_received": dividend_received,
            "exposure": position_value / equity_total if equity_total > 0 else 0,
            "drawdown": drawdown
        })
        prev_equity = max(prev_equity, equity_total)  # 历史高点用于计算回撤

    portfolio.show()
    portfolio.stats(hist["Close"].ffill().iloc[-1].to_dict(), last_year_hist["Dividends"].fillna(0).to_dict(orient="records"))

    # 返回 history DataFrame 和 portfolio（用于计算预测分红）
    return pd.DataFrame(history).set_index("date"), portfolio

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
    while(start < end):
        yield start
        start = start.replace(year=start.year+1)

def subtract_one_year(dt):
    try:
        return dt.replace(year=dt.year - 1)
    except ValueError:
        first_of_next_month = dt.replace(year=dt.year - 1, month=dt.month + 1, day=1)
        return first_of_next_month - datetime.timedelta(days=1)


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
    log_file = os.path.join(output_dir, "backtest.log")
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
        if not args.rebalance:
            logging.info("Rebalancing disabled: only dividend reinvestment")
        else:
            logging.info("Rebalancing enabled: take profit and average down")
        
        history, portfolio = back_testing_yh_finance(d.strftime("%Y-%m-%d"), all_symbols, args.initial_fund, period, config, args.rebalance)
        
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
