import dataclasses
import datetime
import pandas as pd
import datetime
import logging
import collections
import yfinance
import pprint

import warnings
from requests.exceptions import RequestsDependencyWarning

warnings.simplefilter("ignore", RequestsDependencyWarning)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
import pandas as pd

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
    
    # Buy with external fund when stock drops to avg_down_ratio to average down the holding price
    # Total fund is the percentage of stock that meet the critera multiply by the total market value after drop.
    avg_down_ratio: float = 0.4
    
    initial_fund: float = 100000
    
    floor_shares_rate:float = 0.2
    regular_investment_rate : float = 0.5
class Portfolio:
    def __init__(self, config:Portfolio_Conifg):
        self.stock_holding : dict[str, Holding] = {}
        self.total_invest = 0 # Excludes the divident investment
        self.cash = 0
        self.config = config

    def add_cash(self, cash: float):
        logging.info(f"Transfer cash {cash}")
        self.cash += cash
        self.total_invest += cash

    def buy(self, date:datetime.date, symbol:str, fund:int, unit_price:float):
        if symbol not in self.stock_holding:
            holding = Holding(symbol = symbol)
            self.stock_holding[symbol] = holding
        
        holding = self.stock_holding[symbol]
        new_shares = fund / unit_price
        holding.holding_price = (holding.holding_price * holding.shares + fund)/(holding.shares + new_shares)
        holding.market_price = unit_price
        holding.market_value = holding.market_price * holding.shares
        if holding.shares == 0:
            # New buy
            holding.floor_shares = self.config.floor_shares_rate * new_shares

        holding.shares += new_shares
        holding.avg_down_price = holding.holding_price * self.config.avg_down_ratio # Price down
        holding.take_profit_price = holding.holding_price * self.config.take_profit_ratio # Price double
        holding.total_purchase_cost += fund
        logging.info(f"[{date}] Buy {symbol} at price {unit_price} with fund {fund}, get {new_shares} shares, new holding price at {holding.holding_price}")
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
        holding.buys[date] = {
            "shares": sell_shares,
            "unit_price": unit_price,
            "return_cash": sell_shares * unit_price
        }
        pass

    def dividend(self, date:datetime.date, symbol:str, dividen_per_share: float):
        if symbol not in self.stock_holding:
            raise KeyError(f"No holdings for {symbol}")

        if dividen_per_share == 0:
            return
        
        holding = self.stock_holding[symbol]
    
        self.cash += holding.shares * dividen_per_share
        holding.total_dividend_value += holding.shares * dividen_per_share
        logging.info(f"Receive dividend for {symbol}, {dividen_per_share} per share, return cash {holding.shares * dividen_per_share}")
        pass

    
    def rebalance(self, date:datetime.date, closing_prices: dict):
        extra_fund_required = 0
        
        # If need to sell
        # for symbol, price in closing_prices.items():
        #     if symbol in self.stock_holding:
        #         if price > self.stock_holding[symbol].take_profit_price:
        #             self.sell(date, symbol, self.config.sell_fraction, price)
        #             self.stock_holding[symbol].take_profit_price *= self.config.take_profit_ratio
        
        # If need to avg down, requires external fund
        # total_holding_value = sum([hold.holding_value for _, hold in self.stock_holding.items()])
        # avg_down_fund = total_holding_value/len(self.stock_holding)
        avg_down_symbols = []
        # for symbol, price in closing_prices.items():
        #     if symbol in self.stock_holding:
        #         if price < self.stock_holding[symbol].avg_down_price:
        #             avg_down_symbols.append(symbol)
        
        # # Increae total position by average holding value
        # if avg_down_symbols:
        #     # Avg down with the amount of initial investment
        #     total_market_value = sum([h.market_value for _, h in self.stock_holding.items()])
        #     extra_fund_required = total_market_value * len(avg_down_symbols) / len(self.stock_holding) 

        # for symbol in avg_down_symbols:
        #     self.buy(date, symbol, (self.cash)/len(avg_down_symbols), closing_prices[symbol])

        
        # No avg down, but with cash, buy the lowest performanced one.
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
    
def back_testing_yh_finance(star_date:str, symbols:str, initial_fund: int, years: str):
    stock_data = yfinance.Tickers(symbols)
    hist = stock_data.history(start=star_date, period=years, interval='1d')
    print(hist[["Close", "Dividends"]])

    today = datetime.datetime.today()
    last_year_first_day = datetime.datetime(today.year - 1, 1, 1)
    last_year_first_day.strftime("%Y-%m-%d")
    last_year_hist = stock_data.history(start=last_year_first_day, period='1y', interval='1d')
    
    config = Portfolio_Conifg()
    config.initial_fund = initial_fund
    portfolio = Portfolio(config)
    portfolio.add_cash(initial_fund)
    cashes_in = {}
    for date, row in hist[["Close", "Dividends"]].iterrows():

        close_price_map = row["Close"].dropna().to_dict()
        dividend_map = row["Dividends"].fillna(0).to_dict()
        if initial_fund > 0:
            cashes_in[date] = initial_fund
            for sym, price in close_price_map.items():
                if price > 0:
                    portfolio.buy(date, sym, initial_fund/len(close_price_map), price)
            initial_fund = 0
            continue
            
        for sym, divid in dividend_map.items():
            if divid > 0:
                portfolio.dividend(date, sym, divid)

        extra_fund_required = portfolio.rebalance(date, close_price_map)
        if extra_fund_required > 0:
            portfolio.add_cash(extra_fund_required)

        # if not [d for d, _ in cashes_in.items() if d >= subtract_one_year(date)]:
        #     # Regular investment if no avg down investiment in the past 12 monthes
        #     regular_fund = config.initial_fund * config.regular_investment_rate  / len(symbols.split())
        #     portfolio.add_cash(regular_fund)
        #     cashes_in[date] = regular_fund
    portfolio.show()
    portfolio.stats(hist["Close"].ffill().iloc[-1].to_dict(), last_year_hist["Dividends"].fillna(0).to_dict(orient="records"))

def month_ranges(start :datetime.datetime, end : datetime.datetime):
    while(start < end):
        yield start
        
        year = start.year
        month = start.month + 1
        if month > 12:
            year += 1
            month = 1
        start = datetime.datetime(year, month, 1)
        
def subtract_one_year(dt):
    try:
        return dt.replace(year=dt.year - 1)
    except ValueError:
        # 若日期无效（如2月29日），则退到该月的最后一天
        # 方法：将月份加1，然后减去一天
        first_of_next_month = dt.replace(year=dt.year - 1, month=dt.month + 1, day=1)
        return first_of_next_month - datetime.timedelta(days=1)
    
    
if __name__ == "__main__":

    # start = datetime.datetime(2025, 1, 1)
    # print(start.strftime("%Y-%m-%d"))
    # stock_data = yfinance.Tickers("BHP.AX CBA.AX WES.AX WDS.AX TCL.AX")
    # hist = stock_data.history(start=start.strftime("%Y-%m-%d"), period='1y', interval='1d')
    # print(hist)
    # exit

    today = datetime.datetime.today()
    # Allow maximum 20 years period
    start = datetime.datetime(today.year - 20, 1, 1)
    end = datetime.datetime(today. year - 10, 1, 1)
    start = datetime.datetime(2008, 5, 1)
    end = datetime.datetime(2026, 1, 1)
    for d in month_ranges(start, end):
        back_testing_yh_finance(d.strftime("%Y-%m-%d"), "BHP.AX CBA.AX WES.AX WDS.AX TCL.AX", 100000, '10y')
        # back_testing_yh_finance(start.strftime("%Y-%m-%d"), "ZIP.AX PNV.AX SGR.AX NUF.AX LTR.AX", 100000)
        # back_testing_yh_finance(start.strftime("%Y-%m-%d"), "1800.hk 1088.HK 0941.HK 3968.HK 0883.HK", 100000, '10y')
        # back_testing_yh_finance(start.strftime("%Y-%m-%d"), "1088.HK 0941.HK 0883.HK", 100000, '1y')
        # back_testing_yh_finance(start.strftime("%Y-%m-%d"), "0002.HK 0003.HK 0011.HK 0388.HK 1038.HK", 100000, '10y')
        # back_testing_yh_finance(start.strftime("%Y-%m-%d"), "7203.T 6758.T", 100000, '15y')
        
        break

    #back_testing(["APA", "CSL", "NAB", "RIO", "WDS"], 200000)