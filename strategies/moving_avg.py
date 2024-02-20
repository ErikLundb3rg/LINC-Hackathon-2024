import time


def moving_avg(capital, should_stop):
    print("starting moving avg strategy")
    while not should_stop.is_set():
        time.sleep(2)
        print("Rebalanced for the moving avg strategy with: ", capital)
    print("Ending moving avg strategy")
