from threading import Event
import signal
from api_wrapper import api_wrapper
from trading import start_trading
import os


def delete_all_files_in_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)
                print(f"Deleted {file_path}")
            else:
                print(f"Skipped {file_path}, not a file or link")
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")


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


def main():
    global shutdown_flag, stop_threads
    # Register signal handler for graceful interruption
    signal.signal(signal.SIGINT, signal_handler)
    api = api_wrapper()
    delete_all_files_in_directory("./logs")

    start_trading(stop_threads, shutdown_flag, api)

    print(f"{GREEN_START}Exited gracefully after all stocks were sold{COLOR_RESET}")


if __name__ == "__main__":
    main()
