import pandas as pd
import numpy as np
import random

# Read data from CSV file
df = pd.read_csv('timestamps.csv')

# Convert timestamps to datetime and extract the time
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['time'] = df['timestamp'].dt.time

# Define the time intervals
intervals = pd.date_range(start='00:00', end='23:59', freq='30min').time

# Count the occurrences in each interval
df['interval'] = pd.cut(df['time'], bins=intervals, include_lowest=True)
counts = df['interval'].value_counts()

# Calculate probabilities for each interval
probs = counts / counts.sum()

# Calculate the expected number of timestamps in each interval for a total of 50 timestamps
expected_counts = (probs * 50).round().astype(int)

# Generate the new timestamps
new_timestamps = []

for interval, count in expected_counts.items():
    # Calculate the start and end of the interval
    start = interval.left
    end = interval.right
    
    # Calculate the difference between the end and start times in minutes
    diff = ((end.hour * 60 + end.minute) - (start.hour * 60 + start.minute))
    
    # If diff is zero, that means we are at the end of the time frame i.e. 00:00, so set diff to 24*60 minutes
    if diff == 0:
        diff = 24*60

    # Calculate the spacing between each timestamp
    if count > 0:
        spacing = diff / count
    else:
        continue

    # Generate the timestamps
    for i in range(count):
        minute = start.hour * 60 + start.minute + i*spacing
        hour = minute // 60
        minute = minute % 60
        new_timestamps.append(pd.Timestamp(year=2023, month=8, day=2, hour=int(hour), minute=int(minute)))

new_timestamps

