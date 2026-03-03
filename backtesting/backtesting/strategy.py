import abc
import dataclasses
import pprint
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
        position_value: \t{self.position_value}
        total_dividend_value: \t{self.total_dividend_value}
        total_purchase_cost: \t{self.total_purchase_cost}
        buys: \t{pprint.pformat(self.buys)}
        sells: \t{pprint.pformat(self.sells)}
    """

class TradingStrategy(abc.ABC):
    @abc.abstractmethod
    def execute(self, date, cash, holding: Holding, closing_prices) -> list[tuple[str, str, float]]:
        """
        Execute trading strategy and return list of operations.
        
        Args:
            date: Current date
            closing_prices: Dictionary of symbol -> price
            
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
        
    def execute(self, date, cash, holdings: dict, closing_prices) -> list[tuple[str, str, float]]:
        symbols = list(closing_prices.keys())
        if not symbols:
            return []
        
        operations = []

        for symbol, holding in holdings.items():
            avg_cost_per_share = holding.total_purchase_cost/holding.shares
            if closing_prices[symbol] > avg_cost_per_share * self.take_profit_rate:
                operations.append((OPERATION_SELL, symbol, holding.shares * self.take_profit_sell_ratio))
        
        return operations

class AverageDownStrategy(TradingStrategy):
    def __init__(self, average_down_rate: float = 0.5, average_down_buy_ratio: float = 1.0) -> None:
        super().__init__()
        self.average_down_rate = average_down_rate
        self.average_down_buy_ratio = average_down_buy_ratio
        
    def execute(self, date, cash, holdings: dict, closing_prices) -> list[tuple[str, str, float]]:
        # Buy all stocks with equal weight
        symbols = list(closing_prices.keys())
        if not symbols:
            return []
        
        operations = []

        for symbol, holding in holdings.items():
            avg_cost_per_share = holding.total_purchase_cost/holding.shares
            if closing_prices[symbol] < avg_cost_per_share * self.average_down_rate:
                operations.append((OPERATION_BUY, symbol, holding.shares * self.average_down_buy_ratio))
        
        return operations

class CashSplitEvenlyStrategy(TradingStrategy):
    def execute(self, date, cash, holdings: dict, closing_prices) -> list[tuple[str, str, float]]:
        # Buy all stocks with equal weight
        symbols = list(closing_prices.keys())
        if not symbols:
            return []
        
        operations = []
        
        cash_per_stock = cash / len(symbols)
        for symbol in symbols:
            operations.append((OPERATION_BUY, symbol, cash_per_stock/closing_prices[symbol]))
        
        return operations