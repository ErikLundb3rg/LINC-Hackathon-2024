from io import TextIOWrapper
from threading import Event
import time
import hackathon_linc as lh
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
import math
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime

from api_wrapper import api_wrapper


TRAINING_FACTOR = 1
LOOKBACK = 50
TICKER = "STOCK_304"
trainingScaler = MinMaxScaler(feature_range=(0, 1))

def get_values(api):
  historical = api.get_300_days_back()
  historical = historical.loc[historical['symbol'] == TICKER]
  historical.sort_values('time')
  dataFrame = historical
  # historical.sort(key = lambda x: x['time'])
  # dataFrame = pd.DataFrame.from_dict(historical)
  
  dataFrame = dataFrame.drop("symbol", axis=1).drop("time", axis=1)
  amzn_values = np.array(dataFrame['mid'].tolist())
  amzn_values = amzn_values.reshape(-1, 1)
  # SCALING THE DATA
  # Transform the Values
  return amzn_values 



def get_network(api):
  amzn_values = get_values(api)
  time.sleep(1)
  amzn_values_scaled = trainingScaler.fit_transform(amzn_values)

  # CREATING TRAINING and TESTING DATASETS
  training_split = math.floor(len(amzn_values_scaled) * TRAINING_FACTOR)  # 1267+
  # "X" values in batches of 50
  training_amzn = amzn_values_scaled[0:training_split]
  training_ind_amzn = []
  training_dep_amzn = []

  # Preparing Training Data
  for i in range(LOOKBACK, len(training_amzn)):
      training_ind_amzn.append(training_amzn[i - LOOKBACK : i][0])
      training_dep_amzn.append(training_amzn[i][0])

  training_ind_amzn, training_dep_amzn = np.array(training_ind_amzn), np.array(training_dep_amzn)
  training_ind_amzn = np.reshape(training_ind_amzn, (training_ind_amzn.shape[0], training_ind_amzn.shape[1], 1))
  
  amzn_model = Sequential()
  amzn_model.add(
      LSTM(100, return_sequences=True, input_shape=(training_ind_amzn.shape[1], 1))
  )
  amzn_model.add(Dropout(0.2))
  amzn_model.add(LSTM(100, return_sequences=True))
  amzn_model.add(Dropout(0.2))
  amzn_model.add(LSTM(100))
  amzn_model.add(Dropout(0.2))
  amzn_model.add(Dense(25))
  amzn_model.add(Dense(1))
  amzn_model.compile(optimizer="adam", loss="mean_squared_error")
  amzn_model.fit(training_ind_amzn, training_dep_amzn, epochs=60, batch_size=32)
  return amzn_model

def lstm(capital: float, should_stop: Event, api: api_wrapper):
    start_capital = capital
    
    model = get_network(api)
    nrStocks = 0
    
    
    with open("./logs/lstm_logs.txt", "a") as logs:
        logs.write("\nstarting lstm strategy\n")
        while not should_stop.is_set():
            # Run the an iteration of the lstm strategy
            capital, nrStocks = lstm_iteration(capital, logs, api, model, nrStocks)
            time.sleep(5)
            logs.write(f"Rebalancing for the lstm strategy with: {capital}\n")
            logs.flush()
        result = capital - start_capital
        logs.write(f"lstm strategy ended with {result}\n\n")


def lstm_iteration(capital: float, logs: TextIOWrapper, api: api_wrapper, model, nrStocks):
  # api.sell(TICKER, nrStocks, logs)
  time.sleep(5)
  amzn_values = get_values(api)
  
  testing_input_amzn = amzn_values
  testing_input_amzn = trainingScaler.fit_transform(testing_input_amzn)
  predictions = []
  for i in range(LOOKBACK, len(testing_input_amzn) + LOOKBACK):
      predictions.append(testing_input_amzn[i - LOOKBACK : i][0])
  predictions = np.array(predictions)
  predictions = np.reshape(
      predictions, (predictions.shape[0], predictions.shape[1], 1)
  )
  
  
  prediction = model.predict(predictions[-LOOKBACK:])
  prediction = trainingScaler.inverse_transform(prediction)
  alpha = prediction[-1]- prediction[-2]
  
  nrStocks = max(capital // amzn_values[-1] -5, 0)
  
  print("Alpha", alpha) 
  if alpha[0] > 0: 
    print("******************************** BUYINGN *************")
    print("Amount of stocks", nrStocks)
    # api.buy(TICKER, nrStocks, logs)
 
  return capital, nrStocks
