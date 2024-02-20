import time


def index(capital, shouldRun):
    print("starting index strategy")
    while shouldRun.is_set():
        time.sleep(5)
        print("Rebalanced for the index strategy with: ", capital)
    print("Ending index strategy")
