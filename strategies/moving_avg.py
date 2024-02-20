import time


def moving_avg(capital, shouldRun):
    print("starting moving avg strategy")
    while shouldRun.is_set():
        time.sleep(2)
        print("Rebalanced for the moving avg strategy with: ", capital)
    print("Ending moving avg strategy")
