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

N = 50

# calculate the expected number of timestamps in each interval
expected_counts = (probabilities * N).round().astype(int)

# calculate the total number of generated timestamps
total_generated = expected_counts.sum()

# if the total number is not equal to N, adjust the counts proportionally
if total_generated != N:
    adjustment_factor = N / total_generated
    expected_counts = (expected_counts * adjustment_factor).round().astype(int)

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
for interval, count in expected_counts.items():
    timestamps.extend(generate_timestamps_in_interval(interval, count))

# sort the timestamps
timestamps.sort()

timestamps
