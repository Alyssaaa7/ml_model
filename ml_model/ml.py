import pandas as pd

# Load your data
df = pd.read_excel('your_data.xlsx')

# Convert your timestamps to datetime format and set it as index
df['timestamp'] = pd.to_datetime(df['timestamp'])
df.set_index('timestamp', inplace=True)

# Resample your data to the minute level
df_resampled = df.resample('T').count() 

# Convert to binary representation (1 if there was a timestamp in a given minute, 0 otherwise)
df_resampled = (df_resampled > 0).astype(int)

# Flatten the series into a single column dataframe
df_resampled = df_resampled.reset_index().melt('timestamp', var_name='a', value_name='presence')
df_resampled.drop('a', axis=1, inplace=True)



def generate_sequences(data, sequence_length):
    x = []
    y = []
    for i in range(len(data) - sequence_length):
        x.append(data[i : i + sequence_length])
        y.append(data[i + sequence_length])
    return np.array(x), np.array(y)


from sklearn.model_selection import train_test_split

sequence_length = 60  # sequence length could be any number depending on how far back you think is relevant for your prediction.
# For instance, if you think the past 60 minutes are relevant for the prediction, sequence_length should be 60

X, y = generate_sequences(df_resampled['presence'].values, sequence_length)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Reshape input to fit LSTM layer
X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)

from keras.models import Sequential
from keras.layers import LSTM, Dense

model = Sequential()
model.add(LSTM(50, activation='relu', input_shape=(sequence_length, 1)))
model.add(Dense(1, activation='sigmoid'))  # sigmoid activation function for binary classification

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

model.fit(X_train, y_train, epochs=5, verbose=1)
# Note that the model is predicting probabilities.
# To make a binary prediction, you must choose a threshold (like 0.5) to convert these probabilities to 0s and 1s.
y_pred = model.predict(X_test)
y_pred_binary = np.where(y_pred >= 0.5, 1, 0)

# Now y_pred_binary contains the binary predictions of your model for the test data


