import pandas as pd
import numpy as np

# read your csv file into a DataFrame
df = pd.read_csv('your_file.csv', parse_dates=['timestamp'])

# create a 'time' column representing minutes since the start of the day
df['time'] = df['timestamp'].dt.hour * 60 + df['timestamp'].dt.minute

intervals = [pd.Interval(i, i + 30) for i in range(0, 24*60, 30)]

# cut 'time' column into half-hourly intervals
df['interval'] = pd.cut(df['time'], bins=[interval.left for interval in intervals] + [intervals[-1].right])

# count the occurrences in each interval
counts = df['interval'].value_counts(sort=False)

# calculate the probabilities
probabilities = counts / counts.sum()

# the total number of timestamps to generate
N = 50

# calculate the expected number of timestamps in each interval
expected_counts = (probabilities * N).round().astype(int)

# calculate the actual number of timestamps to generate in each interval
actual_counts = expected_counts.clip(upper=1)

# calculate the remaining number of timestamps to generate
remaining = N - actual_counts.sum()

# distribute the remaining timestamps according to the original probabilities
remaining_counts = np.random.choice(probabilities.index, size=remaining, p=probabilities.values)
remaining_counts = pd.Series(remaining_counts).value_counts()

# add the remaining counts to the actual counts
actual_counts += remaining_counts

# create a function to generate evenly spaced timestamps within an interval
def generate_timestamps_in_interval(interval, n):
    interval_length = interval.right - interval.left
    step = interval_length / max(n, 1)
    timestamps = []
    for i in range(n):
        minute = int(interval.left + i * step)
        hour, minute = divmod(minute, 60)
        timestamps.append(pd.Timestamp(year=2023, month=8, day=1, hour=hour, minute=minute))
    return timestamps

# generate the timestamps
timestamps = []
for interval, count in actual_counts.items():
    timestamps.extend(generate_timestamps_in_interval(interval, count))

# sort the timestamps
timestamps.sort()

timestamps
