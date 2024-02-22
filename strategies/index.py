from io import TextIOWrapper
from threading import Event
import time

from api_wrapper import api_wrapper


def index(capital: float, should_stop: Event, api: api_wrapper):
    start_capital = capital
    with open("./logs/index_logs.txt", "a") as logs:
        logs.write("\nstarting index strategy\n")
        while not should_stop.is_set():
            # Run the an iteration of the index strategy
            capital = index_iteration(capital, logs, api)
            logs.write(f"Rebalancing for the index strategy with: {capital}\n")
            logs.flush()
        result = capital - start_capital
        logs.write(f"Index strategy ended with {result}\n\n")


def index_iteration(capital: float, logs: TextIOWrapper, api: api_wrapper):
    prices = api.get_all_current_prices()
    money_per_stock = capital / len(prices)
    amounts = {}
    for price in prices:
        ticker = price["symbol"]
        amount = money_per_stock // price["bidMedian"]
        amounts[ticker] = amount
        logs.write(f"Buying {amount} of {ticker}\n")
        buy_dict = api.buy(ticker, amount, logs)
        capital -= buy_dict["amount"] * buy_dict["price"]

    logs.write(f"Capital after buying all index stocks: {capital}\n")

    time.sleep(5)

    logs.write("Selling all index stocks\n")

    for ticker, amount in amounts.items():
        logs.write(f"Selling {amount} of {ticker}\n")
        sell_dict = api.sell(ticker, amount, logs)
        capital += sell_dict["amount"] * sell_dict["price"]

    return capital
