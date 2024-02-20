from threading import Thread, Event
import time
import signal
from strategies.index import index
from strategies.moving_avg import moving_avg

COLOR_RESET = "\033[0m"  # Reset to default terminal color
GREEN_START = "\033[92m"  # Green color start
BLUE_START = "\033[94m"  # Blue color start
RED_START = "\033[91m"  # Red color start

async def getTotalCapital():
    return 10000


async def sellAllStocks():
    pass


# Global flags to control shutdown
shutdown_flag = False
runThreads = Event()

def signal_handler(signum, frame):
    global shutdown_flag, runThreads
    if not shutdown_flag:
        print(
            f"{BLUE_START}\nReceived shutdown signal. Shutting down gracefully after all stocks have been sold..."
            f"\nPress Ctrl+C again to exit immediately.\n{COLOR_RESET}"
        )
        shutdown_flag = True
    else:
        print(
            f"{RED_START}\nTold all threads to stop then exited immediately{COLOR_RESET}"
        )
        runThreads.clear()
        exit(0)


async def run():
    global shutdown_flag, runThreads
    # Register signal handler for graceful interruption
    signal.signal(signal.SIGINT, signal_handler)

    # init API

    # multithreaded
    while not shutdown_flag:
        totalCapital = await getTotalCapital()
        print()
        print("Total capital: ", totalCapital)
        # strategies is a list of functions which for now are just the run index function
        strategies = [index, moving_avg]
        moneyPerStrategy = totalCapital / len(strategies)
        threads = []
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

        if shutdown_flag:
            print(f"{GREEN_START}\nExited gracefully after all stocks were sold{COLOR_RESET}")
            break


def main():
    # Run the async function
    import asyncio

    asyncio.run(run())


if __name__ == "__main__":
    main()
