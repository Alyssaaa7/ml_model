import pandas as pd
import numpy as np

# read your csv file into a DataFrame
df = pd.read_csv('your_file.csv')

# make sure 'timestamp' column is in datetime format
df['timestamp'] = pd.to_datetime(df['timestamp'])

# extract weekday name, hour and minute, then create a new column for 30-minute interval 
df['weekday'] = df['timestamp'].dt.day_name()
df['hour'] = df['timestamp'].dt.hour
df['minute'] = df['timestamp'].dt.minute
df['time_interval'] = df['hour'] + np.where(df['minute'] >= 30, 0.5, 0)

# count occurrences for each weekday and time_interval
count_df = df.groupby(['weekday', 'time_interval']).size().reset_index(name='counts')

# calculate total counts for each weekday
total_counts = count_df.groupby('weekday')['counts'].sum().reset_index(name='total_counts')

# merge total counts back to the count_df
count_df = pd.merge(count_df, total_counts, on='weekday')

# calculate probability
count_df['probability'] = count_df['counts'] / count_df['total_counts']

# simulate for a specific day
def simulate_day(day_name):
    specific_day_df = count_df[count_df['weekday'] == day_name]
    return np.random.choice(specific_day_df['time_interval'], size=50, p=specific_day_df['probability'])

# simulate for a weekday
print(simulate_day('Monday'))

# simulate for a weekend
print(simulate_day('Saturday'))
