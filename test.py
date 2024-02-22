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

lh.init("d1d79c3c-ac03-40bd-807e-77ece49e12db")


x = lh.get_all_tickers()

dataFrame = pd.DataFrame.from_dict(lh.get_historical_data(100, x[0]))
dataFrame = dataFrame.drop("symbol", axis=1).drop("gmtTime", axis=1)

# # print(dataFrame[0])
# print(dataFrame.head())

# amzn_close = dataFrame['bidMedian']

amzn = yf.Ticker("AMZN")
# Make the end date the current day
end_date = datetime.now().strftime("%Y-%m-%d")
# Pull Stock Price History
amzn_hist = amzn.history(start="2017-01-01", end=end_date)
amzn_close = amzn_hist["Close"]
amzn_values = amzn_close.values
# amzn_values = np.array(dataFrame['bidMedian'].tolist())

amzn_values = amzn_values.reshape(-1, 1)
# SCALING THE DATA
trainingScaler = MinMaxScaler(feature_range=(0, 1))
# Transform the Values
amzn_values_scaled = trainingScaler.fit_transform(amzn_values)

# CREATING TRAINING and TESTING DATASETS
training_split = math.floor(len(amzn_values_scaled) * 0.85)  # 1267+
print("Training split", training_split)
print("Actual ", len(amzn_values_scaled))
# "X" values in batches of 50
training_amzn = amzn_values_scaled[0:training_split]
training_ind_amzn = []
training_dep_amzn = []


NR_VALUES = 4
# Preparing Training Data
for i in range(NR_VALUES, len(training_amzn)):
    training_ind_amzn.append(training_amzn[i - NR_VALUES : i][0])
    training_dep_amzn.append(training_amzn[i][0])

training_ind_amzn, training_dep_amzn = np.array(training_ind_amzn), np.array(
    training_dep_amzn
)
training_ind_amzn = np.reshape(
    training_ind_amzn, (training_ind_amzn.shape[0], training_ind_amzn.shape[1], 1)
)

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


testing_input_amzn = amzn_values[training_split:]
testing_input_amzn = trainingScaler.fit_transform(testing_input_amzn)
testing_amzn = []
for i in range(NR_VALUES, len(testing_input_amzn) + NR_VALUES):
    testing_amzn.append(testing_input_amzn[i - NR_VALUES : i][0])
testing_amzn = np.array(testing_amzn)
testing_amzn = np.reshape(
    testing_amzn, (testing_amzn.shape[0], testing_amzn.shape[1], 1)
)
predict_amzn = amzn_model.predict(testing_amzn)
predict_amzn = trainingScaler.inverse_transform(predict_amzn)

plt.plot(amzn_values[training_split:], color="blue", label="AMZN Stock Price")
plt.plot(predict_amzn, color="red", label="Predicted AMZN Stock Price")
plt.title("My stock")
plt.xlabel("Days")
plt.ylabel("AMZN Stock Price")
plt.legend()
plt.show()
