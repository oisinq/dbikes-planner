import pandas as pd
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

    if "/" in station['address']:
        f = open(f'stations/Princes Street.csv', 'a')
    else:
        f = open(f'stations/{station["address"]}.csv', 'a')

    available_bike_stands = station['available_bike_stands']
    available_bikes = station['available_bikes']
    epoch_time = station['last_update']

    entry_datetime = datetime.fromtimestamp(epoch_time / 1000)

    if is_time_between(time(0, 30), time(5, 0), entry_datetime.time()):
        return

    day_type = ''
    day_index = entry_datetime.weekday()

    if day_index <= 4:
        day_type = 0
    else:
        day_type = 10

    f.write(f"{available_bikes},{available_bike_stands},{datetime_to_seconds(entry_datetime)},{day_type},"
            f"{entry_datetime.timetuple().tm_yday},{entry_datetime.isoformat()},{weather['temperature']},{weather['humidity']},"
            f"null,{weather['wind_speed']},{weather['rain']},null,{weather['visibility']},"
            f"{category(available_bikes)},{category(available_bike_stands)}\n")