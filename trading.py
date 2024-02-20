from threading import Thread
import time
from strategies.index import index
from strategies.moving_avg import moving_avg


async def get_total_capital():
    total_capital = 10000
    print("Total capital: ", total_capital)
    return total_capital


async def sell_all_stocks():
    print("Selling all stocks")


async def start_trading(stop_threads, shutdown_flag):
    while not shutdown_flag.is_set():
        total_capital = await get_total_capital()
        strategies = [index, moving_avg]
        money_per_strategy = total_capital / len(strategies)

        print("Buying stocks with ", money_per_strategy, " per strategy")
        threads = [
            Thread(target=strategy, args=(money_per_strategy, stop_threads))
            for strategy in strategies
        ]

        # Start threads
        for thread in threads:
            thread.start()

        # Let threads run for a while
        time.sleep(10)

        # Stop threads
        stop_threads.set()
        for thread in threads:
            thread.join()
        stop_threads.clear()

        await sell_all_stocks()
        print()
