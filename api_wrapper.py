from io import TextIOWrapper
import time
import hackathon_linc as linc
import threading
from typing import TypeVar, Callable, Union
import pandas as pd

# Define a TypeVar T that can be any type, representing the return type of update_func.
T = TypeVar("T")


class cashed_value(object):
    def __init__(self):
        self.value = None
        self.last_updated = 0
        self.lock = threading.Lock()


class api_wrapper:
    def __init__(self):
        self.total_capital = cashed_value()
        self.tickers = cashed_value()
        self.all_current_prices = cashed_value()
        self.hundred_days_back = cashed_value()
        self.start_prices: Union[None, dict[str, float]] = None
        linc.init("d1d79c3c-ac03-40bd-807e-77ece49e12db")

    # Use TypeVar T to indicate the return type of update_func and the return type of _update_cached_value.
    def _update_cached_value(
        self,
        cached_value_obj: cashed_value,
        update_func: Callable[[], T],
        cache_duration: int,
    ) -> T:
        with cached_value_obj.lock:
            current_time = time.time()
            if current_time - cached_value_obj.last_updated < cache_duration:
                return cached_value_obj.value  # type: ignore
            cached_value_obj.value = update_func()
            cached_value_obj.last_updated = current_time
            return cached_value_obj.value  # type: ignore

    def get_total_capital(self):
        return self._update_cached_value(
            self.total_capital,
            lambda: linc.get_balance(),
            1,  # Cache duration in seconds
        )

    def get_tickers(self):
        return self._update_cached_value(
            self.tickers,
            lambda: linc.get_all_tickers(),
            600,  # Cache duration in seconds
        )

    # TODO: fix the return type of this to a pandas data frame
    def get_300_days_back(self):
        return self._update_cached_value(
            self.hundred_days_back,
            lambda: pd.DataFrame(linc.get_historical_data(300)),
            5,  # Cache duration in seconds
        )

    def get_all_current_prices(self) -> dict[str, float]:
        prices = self._update_cached_value(
            self.all_current_prices,
            lambda: {price["symbol"]: price["mid"] for price in linc.get_current_price()["data"] if price["type"] == "stock"},
            1,  # Cache duration in seconds
        )
        if self.start_prices is None:
            self.start_prices = prices
        return prices

    def get_all_start_prices(self):
        if self.start_prices is None:
            return self.get_all_current_prices()
        return self.start_prices

    def sell_all_stocks(self):
        print("Selling all stocks")
        # for ticker in self.get_tickers():
        #     print("Cancelling all orders for ", ticker)
        #     linc.cancel(None, ticker)
        portfolio = linc.get_portfolio()
        print("Selling all stocks in portfolio: ", portfolio)
        for ticker, quantity in portfolio.items():
            print("Selling ", quantity, " of ", ticker)
            linc.sell(ticker, quantity)
        print("Sold all stocks")
        return

    def buy(self, ticker: str, amount: int, logs: Union[None, TextIOWrapper] = None):
        if logs:
            logs.write(f"Buying {amount} of {ticker}\n")
            logs.flush()
        return linc.buy(ticker, int(amount))

    def sell(self, ticker: str, amount: int, logs: Union[None, TextIOWrapper] = None):
        if logs:
            logs.write(f"Selling {amount} of {ticker}\n")
            logs.flush()
        return linc.sell(ticker, int(amount))
