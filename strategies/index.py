import time


def index(capital, should_stop):
    print("starting index strategy")
    while not should_stop.is_set():
        time.sleep(5)
        print("Rebalanced for the index strategy with: ", capital)
    print("Ending index strategy")
