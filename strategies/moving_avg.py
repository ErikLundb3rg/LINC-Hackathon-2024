from io import TextIOWrapper
from threading import Event
import time
import pandas as pd

from api_wrapper import api_wrapper


def moving_avg(capital: float, should_stop: Event, api: api_wrapper):
    start_capital = capital
    with open(
        "./logs/moving_avg_logs.txt", "a"
    ) as logs:  # Open the log file in append mode
        logs.write("starting moving avg strategy\n")
        intervals = 0
        while not should_stop.is_set():
            if intervals % 60 == 0:
                [amounts, capital_left] = buy_moving_avg(capital, logs, api)
            time.sleep(1)
            if amounts is not None and intervals % 60 == 0:
                capital = sell_moving_avg(capital_left, logs, api, amounts)
        result = capital - start_capital
        logs.write(f"Net result: {result}\n\n")


def buy_moving_avg(capital: float, logs: TextIOWrapper, api: api_wrapper):
    df = api.get_300_days_back()
    # if the length of the dataframe for each stock is less than 300, then return
    dfg = df.groupby("symbol")
    for key, value in dfg:
        if len(value) < 300:
            return [None, capital]

    df["time"] = pd.to_datetime(df["time"])
    dict = get_ma_values_as_dict(df)
    relevant_stocks = {
        key: [value["200_day_MA"], value["50_day_MA"]]
        for key, value in dict.items()
        if value["200_day_MA"][0] < value["50_day_MA"][0]
    }
    # map the stocks to the amount of entries that 200_day_MA is less than 50_day_MA in a row
    relevant_stocks = {
        key: len([i for i in range(len(value[0])) if value[0][i] < value[1][i]])
        for key, value in relevant_stocks.items()
    }

    # sort the stocks by the amount of entries that 200_day_MA is less than 50_day_MA in a row
    relevant_stocks = sorted(relevant_stocks.items(), key=lambda x: x[1], reverse=False)
    relevant_stocks = relevant_stocks[:5]
    relevant_stocks = [stock[0] for stock in relevant_stocks]

    prices = api.get_all_current_prices()
    amounts = {}
    for stock in relevant_stocks:
        amount = capital // prices[stock]
        amounts[stock] = amount
        buy_dict = api.buy(stock, amount, logs)
        capital -= buy_dict["amount"] * buy_dict["price"]

    return [amounts, capital]


def calculate_moving_averages(group: pd.DataFrame) -> pd.DataFrame:
    # Ensure the DataFrame is sorted by date
    group = group.sort_values(by="time", ascending=False)

    # Calculate moving averages
    group["200_day_MA"] = group["mid"].rolling(window=200, min_periods=1).mean()
    group["50_day_MA"] = group["mid"].rolling(window=50, min_periods=1).mean()

    return group


def get_ma_values_as_dict(df: pd.DataFrame) -> dict:
    # Ensure 'time' is a datetime object and sort the DataFrame
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values(by="time", ascending=False)

    # Group by 'symbol' and calculate moving averages
    ma_df = df.groupby("symbol").apply(calculate_moving_averages).reset_index(drop=True)

    # Initialize an empty dictionary to store the results
    ma_values_dict = {}

    # After resetting the index, 'symbol' should no longer be ambiguous
    for symbol, group in ma_df.groupby("symbol"):
        # Extract the moving average lists
        ma_200 = group["200_day_MA"].tolist()[200:]
        ma_50 = group["50_day_MA"].tolist()[50:150]

        # Map the symbol to its moving average lists
        ma_values_dict[symbol] = {"200_day_MA": ma_200, "50_day_MA": ma_50}

    return ma_values_dict


def sell_moving_avg(
    capital: float, logs: TextIOWrapper, api: api_wrapper, amounts: dict[str, int]
):
    logs.write("Selling all stocks\n")

    for ticker, amount in amounts.items():
        sell_dict = api.sell(ticker, amount, logs)
        capital += sell_dict["amount"] * sell_dict["price"]

    return capital
