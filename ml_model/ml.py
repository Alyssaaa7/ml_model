import pandas as pd
import numpy as np
from pmdarima import auto_arima
from datetime import datetime

def generate_timestamps_in_interval(interval, n, date):
    year = date.year
    month = date.month
    day = date.day
    timestamps = []
    for _ in range(n):
        minute = np.random.randint(interval.left, interval.right)
        hour, minute = divmod(minute, 60)
        timestamps.append(datetime(year, month, day, hour, minute))
    return timestamps

def generate_weights(df):
    """Generate weights for the dataframe based on the 'date' column.
    
    Past 7 days have a weight of 2, and others have a weight of 1.
    Adjust as needed.
    
    Arguments:
    - df: dataframe with a 'date' column.
    
    Returns:
    - Series of weights corresponding to the dataframe rows.
    """
    last_date = df['date'].max()
    seven_days_ago = last_date - pd.Timedelta(days=7)
    weights = df['date'].apply(lambda x: 2 if x > seven_days_ago else 1)
    return weights

def get_next_day_frequency(date, df):
    df['date'] = df['timestamp'].dt.date
    df['day_of_week'] = df['timestamp'].dt.day_name()
    weekday_df = df[df['day_of_week'].isin(['Monday','Tuesday','Wednesday','Thursday','Friday'])]
    weekend_df = df[df['day_of_week'].isin(['Saturday','Sunday'])]

    weekday_freq = weekday_df.groupby('date').size().ewm(alpha=0.3).mean()
    weekend_freq = weekend_df.groupby('date').size().ewm(alpha=0.3).mean()

    weekday_train = weekday_freq[-30:]
    weekend_train = weekend_freq[-30:]

    weekday_model = auto_arima(weekday_train)
    weekend_model = auto_arima(weekend_train)
    
    last_day_in_data = df['date'].max()
    target_date = pd.to_datetime(date).to_pydatetime().date()
    days_ahead = (target_date - last_day_in_data).days()

    if target_date.weekday() < 5:
        next_day_pred = weekday_model.predict(n_periods=days_ahead).iloc[-1]
    else:
        next_day_pred = weekend_model.predict(n_periods=days_ahead).iloc[-1]
    return int(next_day_pred.round())

def get_predicted_timestamps(date, sql_result=[]):  # Added sql_result as a default empty list as a parameter
    df = pd.DataFrame(sql_result, columns=['timestamp'])
    N = get_next_day_frequency(date, df)

    df['time'] = df['timestamp'].dt.hour * 60 + df['timestamp'].dt.minute
    intervals = [pd.Interval(i, i + 30) for i in range(0, 24*60, 30)]
    df['interval'] = pd.cut(df['time'], bins = [interval.left for interval in intervals] + [intervals[-1].right])

    # Apply weights to the counts within intervals
    weights = generate_weights(df)
    weighted_counts = df.groupby('interval').apply(lambda x: (x['interval'].value_counts() * weights.loc[x.index]).sum())

    probabilities = weighted_counts / weighted_counts.sum()
    expected_counts = (probabilities * N).round().astype(int)
    total_generated = expected_counts.sum()

    if total_generated != N:
        sorted_interval = probabilities.sort_values(ascending=False).index
        while total_generated < N:
            for interval in sorted_interval:
                if total_generated >= N:
                    break
                expected_counts.loc[interval] += 1
                total_generated += 1
        while total_generated > N:
            for interval in sorted_interval:
                if total_generated <= N or expected_counts.loc[interval] == 0:
                    break
                expected_counts.loc[interval] -= 1
                total_generated -= 1

    timestamps = []
    for interval, count in expected_counts.items():
        timestamps.extend(generate_timestamps_in_interval(interval, count, date))

    return timestamps
