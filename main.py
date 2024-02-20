from threading import Thread
import time

def main():
  # init API 
  strategies = [Strategy()]
  
  # multithreaded
  while True:
    moneyPerStrategy = 1000
    threads = [] 
    runThreads = True
    
    for strategy in strategies: 
      t = Thread(target=strategy.run, args=[moneyPerStrategy, runThreads])
      threads.append(t)
      
    for thread in threads:
      thread.start()
      
    # Let threads run for a while  
    time.sleep(10)
    
    # Stop them
    runThreads = False
    for thread in threads: 
      thread.join()
      


if __name__ == "__main__": 
  main()