from threading import Event, Thread
import time
import hackathon_linc as linc
from api_wrapper import api_wrapper
from strategies.commodities import commodities
from strategies.forex import forex
from strategies.index import index
from strategies.moving_avg import moving_avg


def start_trading(stop_threads: Event, shutdown_flag: Event, api: api_wrapper):
    api.sell_all_stocks()
    while not shutdown_flag.is_set():
        total_capital = api.get_total_capital()
        strategies = [index, forex, commodities, moving_avg]
        money_per_strategy = total_capital / len(strategies)

        print("Buying stocks with ", money_per_strategy, " per strategy")
        threads = [
            Thread(target=strategy, args=(money_per_strategy, stop_threads, api))
            for strategy in strategies
        ]

        # Start threads
        for thread in threads:
            thread.start()

        # Let threads run for a while
        time.sleep(40)

        # Stop threads
        stop_threads.set()
        for thread in threads:
            thread.join()
        stop_threads.clear()

        api.sell_all_stocks()
        print()
