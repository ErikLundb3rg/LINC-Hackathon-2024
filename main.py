from threading import Thread
import time

def main():
  
  # init API 
  strategies = []
  
  # multithreaded
  
    
  while True:
    moneyPerStrategy = 1000
    threads = [] 
    
    for strategy in strategies: 
      t = Thread(target=strategy.run, args=[moneyPerStrategy])
      threads.append(t)
      
    for thread in threads:
      thread.start()
      
    # Let threads run for a while  
    time.sleep(100)
    
    
    
    
    
    
    

      
      
    
    
    
    
  
 
      
    
      
    
      
    

      
    
    
    
    
    
      
      
      
      
      
      
    

  pass


if __name__ == "__main__": 
  main()