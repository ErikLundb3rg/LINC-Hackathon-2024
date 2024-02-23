from io import TextIOWrapper
from threading import Event
import time

from api_wrapper import api_wrapper

def forex(capital: float, should_stop: Event, api: api_wrapper):
    start_capital = capital
    with open("./logs/index_logs.txt", "a") as logs:
        logs.write("starting index strategy\n")
        [amounts, capital_left] = buy_forex(capital, logs, api)
        while not should_stop.is_set():
            time.sleep(1)
        capital_net = sell_forex(capital_left, logs, api, amounts)
        result = capital_net - start_capital
        logs.write(f"Net result: {result}\n\n")


def buy_forex(capital: float, logs: TextIOWrapper, api: api_wrapper):
    prices = api.get_all_current_prices()
    forex_prices = [[ticker, prices[ticker]] for ticker in prices if prices["type"] == "currency"]
    
    # Compare the difference between the current prices and the start prices and return a dict form symbol to current price with the prices that have increased the most
    logs.write(f"Currencies: {forex_prices}\n")
    money_per_currency = capital / len(forex_prices)
    amounts = {}
    for [ticker, price] in forex_prices:
        amount = money_per_currency // price
        amounts[ticker] = amount
        buy_dict = api.buy(ticker, amount, logs)
        capital -= buy_dict["amount"] * buy_dict["price"]

    logs.write(f"Capital after buying all index stocks: {capital}\n")
    return [amounts, capital]


    

def sell_forex(capital: float, logs: TextIOWrapper, api: api_wrapper, amounts: dict[str, int]):
    logs.write("Selling all index stocks\n")

    for ticker, amount in amounts.items():
        sell_dict = api.sell(ticker, amount, logs)
        capital += sell_dict["amount"] * sell_dict["price"]

    return capital