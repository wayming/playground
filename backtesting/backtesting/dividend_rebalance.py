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
class Holding:
    symbol: str
    shares: float = 0.0
    holding_price: float = 0.0 # For calculating take profit and avg down price
    market_price: float = 0.0
    avg_down_price: float = 0.0
    take_profit_price: float = 0.0
    market_value: float = 0.0
    total_dividend_value: float = 0.0
    total_purchase_cost: float = 0.0

    
    # Immutable after the initial buy
    floor_shares: float = 0.0

    buys: dict = dataclasses.field(default_factory=dict)
    sells: dict = dataclasses.field(default_factory=dict)

    
    def show(self):
        return f"""[{self.symbol}]
        shares: \t{self.shares}
        holding_price: \t{self.holding_price}
        market_price: \t{self.market_price}
        market_value: \t{self.market_value}
        total_dividend_value: \t{self.total_dividend_value}
        total_purchase_cost: \t{self.total_purchase_cost}
        buys: \t{pprint.pformat(self.buys)}
        sells: \t{pprint.pformat(self.sells)}
    """
@dataclasses.dataclass
class Portfolio_Conifg:
    # Sell 20% when price doubled
    take_profit_ratio : float = 2
    sell_fraction: float = 0.2
    
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

    def add_cash(self, date, cash: float):
        logging.info(f"[{date}] Transfer cash {cash}")
        self.cash += cash
        self.total_invest += cash

    def buy(self, date:datetime.date, symbol:str, fund:int, unit_price:float):
        if symbol not in self.stock_holding:
            holding = Holding(symbol = symbol)
            self.stock_holding[symbol] = holding
        
        holding = self.stock_holding[symbol]
        new_shares = fund / unit_price
        old_holing_price = holding.holding_price
        holding.holding_price = (holding.holding_price * holding.shares + fund)/(holding.shares + new_shares)
        holding.market_price = unit_price
        holding.market_value = holding.market_price * holding.shares
        if holding.shares == 0:
            # New buy
            holding.floor_shares = self.config.floor_shares_rate * new_shares

        holding.shares += new_shares
        holding.avg_down_price = holding.holding_price * self.config.avg_down_trigger_ratio # Price down
        holding.take_profit_price = holding.holding_price * self.config.take_profit_ratio # Price double
        holding.total_purchase_cost += fund
        logging.info(f"[{date}] Buy {symbol} at price {unit_price} with fund {fund}, get {new_shares} shares, old holding price at {old_holing_price}, new holding price at {holding.holding_price}")
        holding.buys[date] = {
            "fund": fund,
            "unit_price": unit_price,
            "shares": new_shares
        }
        self.cash -= fund
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
        holding.market_value = holding.market_price * holding.shares
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
            # 按当前持有的股票比例分配分红现金
            held_symbols = [s for s in closing_prices.keys() if s in self.stock_holding]
            if held_symbols:
                fund_per_stock = dividend_cash / len(held_symbols)
                for sym in held_symbols:
                    self.buy(date, sym, fund_per_stock, closing_prices[sym])
        
        # 更新所有股票的市场价格
        if closing_prices:
            self.populate_market_prices(closing_prices)

    
    def rebalance(self, date:datetime.date, closing_prices: dict):
        extra_fund_required = 0
        
        # If need to sell（止盈逻辑）
        for symbol, price in closing_prices.items():
            if symbol in self.stock_holding:
                if price > self.stock_holding[symbol].take_profit_price:
                    self.sell(date, symbol, self.config.sell_fraction, price)
                    self.stock_holding[symbol].take_profit_price *= self.config.take_profit_ratio
        
        avg_down_symbols = []
        for symbol, price in closing_prices.items():
            if symbol in self.stock_holding:
                if price < self.stock_holding[symbol].avg_down_price:
                    avg_down_symbols.append(symbol)
        
        # Increae total position by average holding value
        if avg_down_symbols:
            # Avg down with the propotions of the total position value
            extra_fund_required = sum([h.market_value for symbol, h in self.stock_holding.items() if symbol in avg_down_symbols])

            # Check if external fund available
            if self.cash > 0:
                for symbol in avg_down_symbols:
                    market_value = self.stock_holding[symbol].market_value
                    if self.cash >= market_value:
                        self.buy(date, symbol, market_value, closing_prices[symbol])
                        self.cash -= market_value
                    else:
                        self.buy(date, symbol, self.cash, closing_prices[symbol])
                        self.cash = 0
                # 补仓结束
                self.cash = 0
                extra_fund_required = 0
                
        if not avg_down_symbols and self.cash > 0:
            # profits = []
            # for symbol, price in closing_prices.items():
            #     profits.append((price/self.stock_holding[symbol].holding_price, symbol))
            
            # n_low_performanced = len(profits)//2
            # for _, sym in sorted(profits)[:n_low_performanced]:
            #     self.buy(date, sym, self.cash/n_low_performanced, closing_prices[symbol])
            for symbol, price in closing_prices.items():
                self.buy(date, symbol, self.cash/len(closing_prices), price)
                
        self.cash = 0
        self.populate_market_prices(closing_prices)

        return extra_fund_required
    
    def populate_market_prices(self, closing_prices: dict):
        for sym, unit_price in closing_prices.items():
            self.stock_holding[sym].market_price = unit_price
            self.stock_holding[sym].market_value = self.stock_holding[sym].shares * unit_price
            
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
    cashes_in = {}

    # 历史记录 DataFrame
    history = []
    prev_equity = None

    for date, row in hist[["Close", "Dividends"]].iterrows():

        close_price_map = row["Close"].dropna().to_dict()
        dividend_map = row["Dividends"].fillna(0).to_dict()
        if initial_fund > 0:
            cashes_in[date] = initial_fund
            for sym, price in close_price_map.items():
                if price > 0:
                    portfolio.buy(date, sym, initial_fund/len(close_price_map), price)
            initial_fund = 0
            # 记录初始状态
            position_value = sum(h.shares * close_price_map.get(sym, 0) for sym, h in portfolio.stock_holding.items())
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
        position_value = sum(h.shares * close_price_map.get(sym, 0) for sym, h in portfolio.stock_holding.items())
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


def plot_report(history: pd.DataFrame, title: str = "Backtest Report", output: str = None):
    if history.empty:
        print("No history data to plot")
        return

    if output is None:
        output = "./backtest_report.png"

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(title, fontsize=14)

    # 图1: 总权益曲线 (Equity Curve)
    ax1 = axes[0, 0]
    ax1.plot(history.index, history["equity_total"], label="Total Equity", linewidth=1.5)
    ax1.plot(history.index, history["position_value"], label="Position Value (no cash)", linewidth=1, linestyle="--", alpha=0.7)
    ax1.set_title("Equity Curve (Log Scale)")
    ax1.set_yscale("log")
    ax1.set_ylabel("Value")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 图2: 分红现金流 (Dividend Flow)
    ax2 = axes[0, 1]
    dividend_cumsum = history["dividend_received"].cumsum()
    ax2.bar(history.index, history["dividend_received"], width=1, alpha=0.6, label="Daily Dividend", color="green")
    ax2_twin = ax2.twinx()
    ax2_twin.plot(history.index, dividend_cumsum, color="darkgreen", linewidth=2, label="Cumulative Dividend")
    ax2_twin.set_ylabel("Cumulative Dividend", color="darkgreen")
    ax2.set_title("Dividend Cash Flow")
    ax2.legend(loc="upper left")
    ax2_twin.legend(loc="upper right")
    ax2.grid(True, alpha=0.3)

    # 图3: 仓位暴露 (Exposure)
    ax3 = axes[1, 0]
    ax3.fill_between(history.index, history["exposure"], alpha=0.5, color="orange")
    ax3.set_title("Exposure (Position Value / Total Equity)")
    ax3.set_ylabel("Exposure Ratio")
    ax3.set_ylim(0, 1.1)
    ax3.grid(True, alpha=0.3)

    # 图4: 回撤 (Drawdown)
    ax4 = axes[1, 1]
    # 计算真正的回撤：从历史高点开始
    rolling_max = history["equity_total"].cummax()
    drawdown = (history["equity_total"] - rolling_max) / rolling_max
    ax4.fill_between(history.index, drawdown, 0, alpha=0.7, color="red")
    ax4.set_title("Drawdown")
    ax4.set_ylabel("Drawdown %")
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    
    # 保存到文件而不是 show()
    plt.savefig(output, dpi=150)
    plt.close()
    logging.info(f"Chart saved to: {output}")
    return output


def plot_rolling_results(rolling_results):
    import pandas as pd
    import matplotlib.pyplot as plt
    
    df = pd.DataFrame(rolling_results)
    df["start_year"] = df["start_date"].dt.year
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle("Rolling 10-Year Backtest Results (2005-2015 Start Dates)", fontsize=14)
    
    # 图1: CAGR 分布
    ax1 = axes[0, 0]
    ax1.bar(df["start_year"], df["cagr"] * 100, color="steelblue", alpha=0.7)
    ax1.axhline(y=df["cagr"].mean() * 100, color="red", linestyle="--", label=f"Mean: {df['cagr'].mean()*100:.1f}%")
    ax1.set_title("CAGR by Start Year")
    ax1.set_xlabel("Start Year")
    ax1.set_ylabel("CAGR (%)")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 图2: Max Drawdown 分布
    ax2 = axes[0, 1]
    ax2.bar(df["start_year"], df["max_drawdown"] * 100, color="red", alpha=0.7)
    ax2.axhline(y=df["max_drawdown"].mean() * 100, color="darkred", linestyle="--", label=f"Mean: {df['max_drawdown'].mean()*100:.1f}%")
    ax2.set_title("Max Drawdown by Start Year")
    ax2.set_xlabel("Start Year")
    ax2.set_ylabel("Max Drawdown (%)")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 图3: 累计分红分布（10年期间实际收到的分红总额）
    ax3 = axes[0, 2]
    ax3.bar(df["start_year"], df["total_dividend"], color="green", alpha=0.7)
    ax3.axhline(y=df["total_dividend"].mean(), color="darkgreen", linestyle="--", label=f"Mean: ${df['total_dividend'].mean():.0f}")
    ax3.set_title("Total Dividend Received (10 Years)")
    ax3.set_xlabel("Start Year")
    ax3.set_ylabel("Total Dividend ($)")
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 图4: 预测分红分布（期末 shares × 2025年分红）
    ax4 = axes[1, 0]
    ax4.bar(df["start_year"], df["predicted_dividend"], color="purple", alpha=0.7)
    ax4.axhline(y=df["predicted_dividend"].mean(), color="purple", linestyle="--", label=f"Mean: ${df['predicted_dividend'].mean():.0f}")
    ax4.set_title("Predicted Annual Dividend (End Shares × 2025 DPS)")
    ax4.set_xlabel("Start Year")
    ax4.set_ylabel("Predicted Dividend ($/year)")
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # 图5: CAGR vs Max Drawdown 散点图
    ax5 = axes[1, 1]
    scatter = ax5.scatter(df["max_drawdown"] * 100, df["cagr"] * 100, c=df["start_year"], cmap="viridis", s=80, alpha=0.7)
    ax5.set_title("Risk-Return (Color = Start Year)")
    ax5.set_xlabel("Max Drawdown (%)")
    ax5.set_ylabel("CAGR (%)")
    plt.colorbar(scatter, ax=ax5, label="Start Year")
    ax5.grid(True, alpha=0.3)
    
    # 图6: 总投资额分布
    ax6 = axes[1, 2]
    ax6.bar(df["start_year"], df["total_invest"], color="orange", alpha=0.7)
    ax6.axhline(y=df["total_invest"].mean(), color="darkorange", linestyle="--", label=f"Mean: ${df['total_invest'].mean():.0f}")
    ax6.set_title("Total Investment (10 Years)")
    ax6.set_xlabel("Start Year")
    ax6.set_ylabel("Total Investment ($)")
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output = os.path.join(output_dir, "rolling_backtest_report.png")
    plt.savefig(output, dpi=150)
    plt.close()
    logging.info(f"\nRolling chart saved to: {output}")
    
    # 打印统计摘要
    logging.info("\n=== Rolling Backtest Summary ===")
    logging.info(f"Number of start dates: {len(df)}")
    logging.info(f"CAGR: Mean={df['cagr'].mean()*100:.2f}%, Min={df['cagr'].min()*100:.2f}%, Max={df['cagr'].max()*100:.2f}%")
    logging.info(f"Max Drawdown: Mean={df['max_drawdown'].mean()*100:.2f}%, Min={df['max_drawdown'].min()*100:.2f}%, Max={df['max_drawdown'].max()*100:.2f}%")
    logging.info(f"Total Investment: Mean=${df['total_invest'].mean():.0f}, Min=${df['total_invest'].min():.0f}, Max=${df['total_invest'].max():.0f}")
    logging.info(f"Predicted Dividend: Mean=${df['predicted_dividend'].mean():.0f}, Min=${df['predicted_dividend'].min():.0f}, Max=${df['predicted_dividend'].max():.0f}")


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
    
    today = datetime.datetime.today()
    # 从start年到end年，每月一个起点，每个测试period
    start = datetime.datetime(args.start, 1, 1)
    end = datetime.datetime(args.end, 1, 1)
    period = args.period
    
    logging.info(f"Configuration: debug={args.debug}, start={args.start}, end={args.end}, period={period}, rebalance={args.rebalance}, output={args.output}, symbols='{args.symbols}', initial_fund={args.initial_fund}")
    
    rolling_results = []
    
    # 预加载所有年份的分红数据（用于预测）
    all_symbols = args.symbols
    stock_data = yfinance.Tickers(all_symbols)
    full_hist = stock_data.history(start="2005-01-01", end="2026-01-01", interval='1d')
    
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
        plot_report(history, title=f"Backtest: Start {d.strftime('%Y-%m-%d')}, {period}", output=output)
        
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
            
            # 预测分红：期末 shares × 2024年分红（最新的完整年份分红数据）
            predicted_div = 0
            if 2024 in yearly_div:
                for sym, h in portfolio.stock_holding.items():
                    if sym in yearly_div[2024]:
                        predicted_div += h.shares * yearly_div[2024][sym]
            
            rolling_results.append({
                "start_date": d,
                "initial_equity": initial_equity,
                "final_equity": final_equity,
                "total_return": total_return,
                "cagr": cagr,
                "max_drawdown": max_drawdown,
                "total_dividend": total_dividend,
                "predicted_dividend": predicted_div,
                "total_invest": total_invest,
                "years": years
            })
            logging.info(f"Start: {d.strftime('%Y-%m-%d')}, CAGR: {cagr:.2%}, MaxDD: {max_drawdown:.2%}, Total Div: {total_dividend:.0f}, Predicted: {predicted_div:.0f}")
    
    # 绘制 rolling 结果分布图
    if rolling_results:
        plot_rolling_results(rolling_results)
