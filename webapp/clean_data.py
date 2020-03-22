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


def category(current_available_bikes):
    if current_available_bikes == 0:
        return 'empty'
    elif current_available_bikes < 2:
        return 'very low'
    elif current_available_bikes < 5:
        return 'low'
    elif current_available_bikes < 10:
        return 'moderate'
    else:
        return "high"


def update_record():
    dictionary = {}
    my_data = pd.read_csv("weather.csv")

    for line in my_data.values:
        date = datetime.strptime(line[0], '%d-%b-%Y %H:%M')
        dictionary[date] = line

    print(dictionary.keys)

    my_data = pd.read_csv("./bike_records/charlemont.csv")
    f = open('result_charlemont.csv', 'w')

    f.write(
        "available_bike_stands,time_of_day,type_of_day,day_of_year,iso_date,temperature,relative_humidity,vapour_pressure,"
        "wind_speed,rain,sunshine,visibility,category\n")

    previous_number_of_bikes = 0

    for line in my_data.sort_values('last_update').values:
        available_bikes = line[4]
        epoch_time = line[5]

        entry_datetime = datetime.fromtimestamp(epoch_time / 1000)

        if is_time_between(time(0, 30), time(5, 0), entry_datetime.time()):
            continue

        weather_date = nearest_time(dictionary.keys(), entry_datetime)

        weather_line = dictionary[weather_date]

        day_index = entry_datetime.weekday()
        day_type = ''

        if day_index <= 4:
            day_type = 0
        else:
            day_type = 10

        f.write(f"{available_bikes},{datetime_to_seconds(entry_datetime)},{day_type},"
                f"{entry_datetime.timetuple().tm_yday},{entry_datetime.isoformat()},{weather_line[4]},{weather_line[9]},"
                f"{weather_line[8]},{weather_line[12]},{weather_line[2]},{weather_line[17]},{weather_line[18]},"
                f"{category(available_bikes)}\n")