import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense
from sklearn.metrics import mean_absolute_error, mean_squared_error
import tensorflow as tf

# Load the dataset
df = pd.read_excel('your_dataset.xlsx')

# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Calculate time difference between current row and previous row in hours
df['diff'] = df['timestamp'].diff().dt.total_seconds() / 3600  # converting seconds to hours
df = df.dropna()  # drop the first row which has a NaN diff value

# Define number of past steps to consider and number of future steps (hours) to predict
n_steps_past = 72
n_steps_future = 24
n_features = 1

# Normalize the 'diff' column
scaler = MinMaxScaler(feature_range=(0, 1))
df['diff'] = scaler.fit_transform(df['diff'].values.reshape(-1, 1))

# Prepare the dataset
X, y = [], []
for i in range(n_steps_past, len(df) - n_steps_future):
    X.append(df['diff'].iloc[i - n_steps_past:i].values)
    y.append(df['diff'].iloc[i:i + n_steps_future].values)

X = np.array(X).reshape(-1, n_steps_past, n_features)
y = np.array(y)

# Define LSTM model
model = Sequential()
model.add(LSTM(50, activation='relu', input_shape=(n_steps_past, n_features)))
model.add(Dense(n_steps_future))

# Compile the model
model.compile(optimizer='adam', loss='mse')

# Train the model
model.fit(X, y, epochs=50, verbose=1)

# Predict future timestamps
X_new = df['diff'].to_numpy()[-n_steps_past:]  
X_new = X_new.reshape((1, n_steps_past, n_features))

predicted_diffs = model.predict(X_new)[0]
predicted_diffs = scaler.inverse_transform(predicted_diffs.reshape(-1, 1))  # inverse transform to the original scale

# Create future timestamps
last_timestamp = df['timestamp'].iloc[-1]
predicted_timestamps = [last_timestamp + pd.to_timedelta(predicted_diffs[i][0], unit='h') for i in range(n_steps_future)]

print(predicted_timestamps)

