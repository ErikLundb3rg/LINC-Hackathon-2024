from io import TextIOWrapper
from threading import Event
import time

from api_wrapper import api_wrapper

def commodities(capital: float, should_stop: Event, api: api_wrapper):
    start_capital = capital
    with open("./logs/index_logs.txt", "a") as logs:
        logs.write("starting index strategy\n")
        intervals = 0
        while not should_stop.is_set():
            if intervals % 60 == 0:
                [amounts, capital_left] = buy_commodities(capital, logs, api)
            time.sleep(1)
            if intervals % 60 == 0:
                capital = sell_commodities(capital_left, logs, api, amounts)
            intervals += 1
        result = capital - start_capital
        logs.write(f"Net result: {result}\n\n")


def buy_commodities(capital: float, logs: TextIOWrapper, api: api_wrapper):
    prices = api.get_all_current_prices("Commodity")
    
    # Compare the difference between the current prices and the start prices and return a dict form symbol to current price with the prices that have increased the most
    logs.write(f"Currencies: {prices}\n")
    money_per_currency = capital / len(prices)
    amounts = {}
    for [ticker, price] in prices:
        amount = money_per_currency // price
        amounts[ticker] = amount
        buy_dict = api.buy(ticker, amount, logs)
        capital -= buy_dict["amount"] * buy_dict["price"]

    logs.write(f"Capital after buying all index stocks: {capital}\n")
    return [amounts, capital]


    

def sell_commodities(capital: float, logs: TextIOWrapper, api: api_wrapper, amounts: dict[str, int]):
    logs.write("Selling all index stocks\n")

    for ticker, amount in amounts.items():
        sell_dict = api.sell(ticker, amount, logs)
        capital += sell_dict["amount"] * sell_dict["price"]

    return capital