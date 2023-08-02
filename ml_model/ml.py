import pandas as pd
import numpy as np

# read your csv file into a DataFrame
df = pd.read_csv('your_file.csv', parse_dates=['timestamp'])

# create a 'time' column representing minutes since the start of the day
df['time'] = df['timestamp'].dt.hour * 60 + df['timestamp'].dt.minute

# define the intervals (48 half-hourly intervals in a day)
intervals = pd.interval_range(start=0, end=24*60, freq=30)

# cut 'time' column into half-hourly intervals
df['interval'] = pd.cut(df['time'], bins=[interval.left for interval in intervals] + [intervals[-1].right])

# count the occurrences in each interval
counts = df['interval'].value_counts(sort=False)

# calculate the probabilities
probabilities = counts / counts.sum()

# create a function to generate timestamps for a day
def generate_timestamps(n):
    # draw n intervals according to the probabilities
    drawn_intervals = np.random.choice(probabilities.index, size=n, p=probabilities.values)

    # for each drawn interval, generate evenly spaced timestamps within that interval
    timestamps = []
    for interval in drawn_intervals:
        interval_length = interval.right - interval.left
        timestamps_per_interval = np.random.randint(1, 5) # you can adjust this as needed
        step = interval_length / timestamps_per_interval
        for i in range(timestamps_per_interval):
            minute = int(interval.left + i * step)
            hour, minute = divmod(minute, 60)
            timestamps.append(pd.Timestamp(year=2023, month=8, day=1, hour=hour, minute=minute))

    return timestamps

# generate 50 timestamps
timestamps = generate_timestamps(50)

# sort the timestamps
timestamps.sort()
