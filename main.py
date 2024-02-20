from threading import Event
import signal
from trading import start_trading

COLOR_RESET = "\033[0m"  # Reset to default terminal color
GREEN_START = "\033[92m"  # Green color start
BLUE_START = "\033[94m"  # Blue color start
RED_START = "\033[91m"  # Red color start

# Global flags to control shutdown
shutdown_flag = Event()
stop_threads = Event()


def signal_handler(signum, frame):
    global shutdown_flag, stop_threads
    if not shutdown_flag.is_set():
        print(
            f"{BLUE_START}\nReceived shutdown signal. Shutting down gracefully after all stocks have been sold..."
            f"\nPress Ctrl+C again to exit immediately.\n{COLOR_RESET}"
        )
        shutdown_flag.set()
    else:
        print(
            f"{RED_START}\nTold all threads to stop then exited immediately{COLOR_RESET}"
        )
        stop_threads.set()
        exit(0)


async def run():
    global shutdown_flag, stop_threads
    # Register signal handler for graceful interruption
    signal.signal(signal.SIGINT, signal_handler)

    # Main Program Loop
    await start_trading(stop_threads, shutdown_flag)

    print(f"{GREEN_START}Exited gracefully after all stocks were sold{COLOR_RESET}")


def main():
    # Run the async function
    import asyncio

    asyncio.run(run())


if __name__ == "__main__":
    main()
