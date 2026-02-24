import dataclasses
import datetime

import pandas as pd


@dataclasses.dataclass
class historical_price:
    date: datetime
    open: float
    high: float
    low: float
    close: float
    adj_close: float
    volume: float


def yahoo_finance_csv_loader():
    df = pd.read_csv("APA.txt", parse_dates=["Date"], index_col="Date")
    print(df)
    pass


def __main__():
    yahoo_finance_csv_loader()
