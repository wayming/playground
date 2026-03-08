import abc
import dataclasses
import pprint
import logging

OPERATION_BUY = "buy"
OPERATION_SELL = "sell"


@dataclasses.dataclass
class Holding:
    symbol: str
    shares: float = 0.0
    holding_price: float = 0.0 # For calculating take profit and avg down price
    market_price: float = 0.0
    avg_down_price: float = 0.0
    take_profit_price: float = 0.0
    position_value: float = 0.0
    total_dividend_received: float = 0.0
    total_purchase_cost: float = 0.0
    last_avg_down_price: float = 0.0
    initial_shares: float = 0.0
    initial_price: float = 0.0
    
    # Immutable after the initial buy
    floor_shares: float = 0.0

    buys: dict = dataclasses.field(default_factory=dict)
    sells: dict = dataclasses.field(default_factory=dict)

    
    def export(self):
        return pprint.pformat(dataclasses.asdict(self))

class TradingStrategy(abc.ABC):
    @abc.abstractmethod
    def execute(self, date, cash, holding: Holding, market_data) -> list[tuple[str, str, float]]:
        """
        Execute trading strategy and return list of operations.
        
        Args:
            date: Current date
            cash: Current cash balance
            holding: Current holding
            market_data: Dictionary of symbol -> market data (e.g., Close price)
            
        Returns:
            List of tuples (operation, symbol, amount) where:
            - operation: "buy" or "sell"
            - symbol: Stock symbol
            - amount: Dollar amount to trade
        """
        pass


class TakeProfitPercentageStrategy(TradingStrategy):
    def __init__(self, take_profit_rate: float = 2, take_profit_sell_ratio: float = 0.2) -> None:
        super().__init__()
        self.take_profit_rate = take_profit_rate
        self.take_profit_sell_ratio = take_profit_sell_ratio
        
    def execute(self, date, cash, holdings: dict, market_data) -> list[tuple[str, str, float]]:
        symbols = list(market_data.keys())
        if not symbols:
            return []
        operations = []

        for symbol, holding in holdings.items():
            avg_cost_per_share = holding.total_purchase_cost/holding.shares
            if market_data[symbol]["Close"] > avg_cost_per_share * self.take_profit_rate:
                operations.append((OPERATION_SELL, symbol, holding.shares * self.take_profit_sell_ratio))
        
        return operations

class AverageDownStrategy(TradingStrategy):
    def __init__(self, average_down_rate: float = 0.5, average_down_buy_ratio: float = 1.0) -> None:
        super().__init__()
        self.average_down_rate = average_down_rate
        self.average_down_buy_ratio = average_down_buy_ratio
        
    def execute(self, date, cash, holdings: dict, market_data) -> list[tuple[str, str, float]]:
        # Buy all stocks with equal weight
        symbols = list(market_data.keys())
        if not symbols:
            return []
        
        operations = []

        for symbol, holding in holdings.items():
            avg_cost_per_share = holding.total_purchase_cost/holding.shares
            if market_data[symbol]["Close"] < avg_cost_per_share * self.average_down_rate:
                operations.append((OPERATION_BUY, symbol, holding.shares * self.average_down_buy_ratio))
        
        return operations

# Average down by MA250
# Each bind only trigger once, and restart from band1 when MA250 exceeds initial price
class AverageDownByMA250Strategy(TradingStrategy):
    def __init__(self, symbols) -> None:
        super().__init__()
        self.symbols = symbols
        self.average_down_bands = {
            "band1": (0.85, 0.5),
            "band2": (0.70, 1),
            "band3": (0.50, 2),
            "bind4": (None, None),
        }
        self.state = {symbol: "band1" for symbol in self.symbols}
    
    def next_bind(self, bind:str):
        bands = list(self.average_down_bands.keys())
        current_index = bands.index(bind)
        return bands[current_index + 1] if current_index < len(bands) - 1 else bind
    
    def execute(self, date, cash, holdings: dict, market_data) -> list[tuple[str, str, float]]:
        # Buy all stocks with equal weight
        symbols = list(market_data.keys())
        if not symbols:
            return []

        operations = []

        for symbol, holding in holdings.items():
            band_threshold, band_buy_ratio = self.average_down_bands[self.state[symbol]]
            if band_threshold and band_buy_ratio and market_data[symbol]["Close"] < market_data[symbol]["MA250"] * band_threshold:
                operations.append((OPERATION_BUY, symbol, holding.initial_shares * band_buy_ratio))
                logging.info(f"Average down by MA250: {symbol} {holding.initial_shares} shares at {market_data[symbol]['Close']}, "
                f"reach {self.state[symbol]} threshold {band_threshold}")
                self.state[symbol] = self.next_bind(self.state[symbol])
            elif market_data[symbol]["Close"] > market_data[symbol]["MA250"]:
                self.state[symbol] = "band1" # close price exceeds MA250, restart from band1
        return operations

# Buy all stocks with equal weight
class CashSplitEvenlyStrategy(TradingStrategy):
    def execute(self, date, cash, holdings: dict, market_data) -> list[tuple[str, str, float]]:
        # Buy all stocks with equal weight
        symbols = list(market_data.keys())
        if not symbols:
            return []
        
        operations = []
        
        if cash < sum([market_data[symbol]["Close"] for symbol in symbols]):
            logging.debug(f"Cash is not enough for buying all stocks")
            return []
        
        cash_per_stock = cash / len(symbols)
        for symbol in symbols:
            operations.append((OPERATION_BUY, symbol, int(cash_per_stock/market_data[symbol]["Close"])))
        
        return operations


# Buy the stock with the highest dividend yield
class CashForHighDivStrategy(TradingStrategy):
    def execute(self, date, cash, holdings: dict, market_data) -> list[tuple[str, str, float]]:
        # Buy all stocks with equal weight
        symbols = list(market_data.keys())
        if not symbols:
            return []
                
        _, highest_yield_symbol = max([(data["Yield"], symbol) for symbol, data in market_data.items() if data["Yield"] is not None])
        if cash < market_data[highest_yield_symbol]["Close"]:
            logging.debug(f"Cash is not enough for buying {highest_yield_symbol}")
            return []
        
        return [(OPERATION_BUY, highest_yield_symbol, int(cash/market_data[highest_yield_symbol]["Close"]))]
        
