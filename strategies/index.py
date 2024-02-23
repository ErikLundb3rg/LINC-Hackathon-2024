from io import TextIOWrapper
from threading import Event
import time

from api_wrapper import api_wrapper

AMOUNT_OF_STOCKS_IN_INDEX = 20


def index(capital: float, should_stop: Event, api: api_wrapper):
    start_capital = capital
    with open("./logs/index_logs.txt", "a") as logs:
        logs.write("starting index strategy\n")
        [amounts, capital_left] = buy_index(capital, logs, api)
        while not should_stop.is_set():
            time.sleep(1)
        capital_net = sell_index(capital_left, logs, api, amounts)
        result = capital_net - start_capital
        logs.write(f"Net result: {result}\n\n")


def buy_index(capital: float, logs: TextIOWrapper, api: api_wrapper):
    prices = api.get_all_current_prices("Stock")
    start_prices = api.get_all_start_prices()
    # Compare the difference between the current prices and the start prices and return a dict form symbol to current price with the prices that have increased the most
    price_diffs = {
        ticker: price - start_prices[ticker] for ticker, price in prices.items()
    }
    top_stocks = sorted(price_diffs.items(), key=lambda x: x[1], reverse=True)[
        :AMOUNT_OF_STOCKS_IN_INDEX
    ]
    top_stocks = [[ticker, prices[ticker]] for ticker, _ in top_stocks]
    logs.write(f"Top 20 stocks: {top_stocks}\n")
    money_per_stock = capital / len(top_stocks)
    amounts = {}
    for [ticker, price] in top_stocks:
        amount = money_per_stock // price
        amounts[ticker] = amount
        buy_dict = api.buy(ticker, amount, logs)
        capital -= buy_dict["amount"] * buy_dict["price"]

    logs.write(f"Capital after buying all index stocks: {capital}\n")
    return [amounts, capital]


def sell_index(
    capital: float, logs: TextIOWrapper, api: api_wrapper, amounts: dict[str, int]
):
    logs.write("Selling all index stocks\n")

    for ticker, amount in amounts.items():
        sell_dict = api.sell(ticker, amount, logs)
        capital += sell_dict["amount"] * sell_dict["price"]

    return capital
