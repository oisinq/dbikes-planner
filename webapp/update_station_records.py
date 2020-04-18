import subprocess

import pandas as pd
import datalab.storage as gcs
from datetime import datetime, time


def datetime_to_seconds(t):
    return (t.hour * 60 + t.minute) * 60 + t.second


def seconds_in_previous_days(t):
    return t.timetuple().tm_yday * 24 * 60 * 60


def nearest_time(items, pivot):
    return min(items, key=lambda x: abs(x - pivot))


def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.utcnow().time()
    if begin_time < end_time:
        return begin_time <= check_time <= end_time
    else:  # crosses midnight
        return check_time >= begin_time or check_time <= end_time


def category(quantity):
    if quantity == 0:
        return 'empty'
    elif quantity < 2:
        return 'very low'
    elif quantity < 5:
        return 'low'
    elif quantity < 10:
        return 'moderate'
    else:
        return "high"


def update_record(station, weather):
    print(f"Updating {station['address']}")
    if "/" in station['address']:
        data = pd.read_csv('gs://dbikes-planner.appspot.com/station_records/Princes Street.csv')
    else:
        data = pd.read_csv(f"gs://dbikes-planner.appspot.com/station_records/{station['address']}.csv")

    epoch_time = station['last_update']

    entry_datetime = datetime.fromtimestamp(epoch_time / 1000)

    if is_time_between(time(3, 30), time(5, 0), entry_datetime.time()):
        return

    last_line = data.tail(3).to_csv()

    if entry_datetime.isoformat() in last_line:
        return

    day_index = entry_datetime.weekday()

    if day_index <= 4:
        day_type = 0
    else:
        day_type = 10

    new_row = {'available_bikes': station['available_bikes'],
               'available_bike_stands': station['available_bike_stands'],
               'time_of_day': datetime_to_seconds(entry_datetime), 'type_of_day': day_type,
               'day_of_year': entry_datetime.timetuple().tm_yday, 'iso_date': entry_datetime.isoformat(),
               'temperature': weather['temperature'], 'relative_humidity': weather['humidity'],
               'wind_speed': weather['wind_speed'], 'rain': weather['rain'], 'visibility': weather['visibility'],
               'bike_availability': category(station['available_bikes']),
               'bike_stand_availability': category(station['available_bike_stands']),
               'unix_timestamp': entry_datetime.timestamp() // 3600}

    new_row_dataframe = pd.DataFrame(new_row, index=[0])

    combined_df = pd.concat([data, new_row_dataframe], ignore_index=True)

    gcs.Bucket('dbikes-planner.appspot.com').item(f'station_records/{station["address"]}.csv') \
        .write_to(combined_df.to_csv(index=False), 'text/csv')
