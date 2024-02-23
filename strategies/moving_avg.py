from io import TextIOWrapper
from threading import Event
import time

from api_wrapper import api_wrapper


def moving_avg(capital: float, should_stop: Event, api: api_wrapper):
    start_capital = capital
    with open(
        "./logs/moving_avg_logs.txt", "a"
    ) as logs:  # Open the log file in append mode
        logs.write("starting moving avg strategy\n")
        while not should_stop.is_set():
            capital = moving_avg_iteration(capital, logs, api)
            logs.flush()
        result = capital - start_capital
        logs.write(f"Net result: {result}\n\n")


def moving_avg_iteration(capital: float, logs: TextIOWrapper, api: api_wrapper):
    history = api.get_300_days_back()
    for ticker in history["symbol"]:
        pass
    time.sleep(2)
    logs.write("Ran moving avg iteration\n")
    logs.flush()
    return capital
