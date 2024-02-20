from threading import Thread, Event
import time
from strategies.index import index
from strategies.moving_avg import moving_avg

async def getTotalCapital():
    return 10000

async def sellAllStocks():
    pass

async def run():
    # init API

    # multithreaded
    while True:
        totalCapital = await getTotalCapital()
        print()
        print("Total capital: ", totalCapital)
        # strategies is a list of functions which for now are just the run index function
        strategies = [index, moving_avg]
        moneyPerStrategy = totalCapital / len(strategies)
        threads = []
        runThreads = Event()
        runThreads.set()
        print("Buying stocks with ", moneyPerStrategy, " per strategy")
        for strategy in strategies:
            t = Thread(target=strategy, args=(moneyPerStrategy, runThreads))
            threads.append(t)

        for thread in threads:
            thread.start()

        # Let threads run for a while
        time.sleep(10)

        # Stop them
        runThreads.clear()
        for thread in threads:
            thread.join()
        print("Selling all stocks")
        await sellAllStocks()


def main():
    # Run the async function
    import asyncio

    asyncio.run(run())


if __name__ == "__main__":
    main()



