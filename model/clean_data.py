import pandas as pd
from datetime import datetime, time

def datetime_to_seconds(t):
    return (t.hour * 60 + t.minute) * 60 + t.second

def seconds_in_previous_days(t):
    return t.timetuple().tm_yday * 24*60*60

def nearestTime(items, pivot):
    return min(items, key=lambda x: abs(x - pivot))

def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.utcnow().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time

dictionary = {}
my_data = pd.read_csv("weather.csv")

for line in my_data.values:
    date = datetime.strptime(line[0], '%d-%b-%Y %H:%M')
    dictionary[date] = line

print(dictionary.keys)

my_data = pd.read_csv("charlemount.csv")
f = open('result_charlemount.csv', 'w')
g = open('outlier_charlemount.csv', 'w')
f.write("available_bike_stands,time_of_day,type_of_day,time_of_year,day_of_year,iso_date,temperature,rain,relative_humidity,vapour_pressure,wind_speed,sunshine,visibility,change_in_bike_availability,epoch,bikes_at_t1,bikes_at_t2\n")
g.write("available_bike_stands,time_of_day,type_of_day,time_of_year,day_of_year,iso_date,temperature,rain,relative_humidity,vapour_pressure,wind_speed,sunshine,visibility,change_in_bike_availability,epoch,bikes_at_t1,bikes_at_t2\n")

previous_number_of_bikes = 0
previous_previous_number_of_bikes = 0
for line in my_data.sort_values('last_update').values:
    available_bikes = line[4]
    epoch_time = line[5]
    
    entry_datetime = datetime.fromtimestamp(epoch_time/1000)

    if is_time_between(time(0, 30), time(5, 0), entry_datetime.time()):
        continue
    
    weather_date = nearestTime(dictionary.keys(), entry_datetime)

    weather_line = dictionary[weather_date]

    day_index = entry_datetime.weekday()
    day_type = ''

    if day_index <= 4:
        day_type = '0'
    else:
        day_type = '1'

    f.write(f"{available_bikes},{datetime_to_seconds(entry_datetime)},{day_type},{seconds_in_previous_days(entry_datetime) + datetime_to_seconds(entry_datetime)}," + \
    f"{entry_datetime.timetuple().tm_yday},{entry_datetime.isoformat()},{weather_line[4]},{weather_line[1]},{weather_line[9]},{weather_line[8]},{weather_line[12]},{weather_line[17]},{weather_line[18]},{available_bikes-previous_number_of_bikes},{int(epoch_time/1000)},{previous_number_of_bikes},{previous_previous_number_of_bikes}\n")
    

    if (available_bikes- previous_number_of_bikes) >= 10 or (previous_number_of_bikes - available_bikes) >= 10:
        g.write(f"{available_bikes},{datetime_to_seconds(entry_datetime)},{day_type},{seconds_in_previous_days(entry_datetime) + datetime_to_seconds(entry_datetime)}," + \
        f"{entry_datetime.timetuple().tm_yday},{entry_datetime.isoformat()},{weather_line[4]},{weather_line[1]},{weather_line[9]},{weather_line[8]},{weather_line[12]},{weather_line[17]},{weather_line[18]},{available_bikes-previous_number_of_bikes},{int(epoch_time/1000)},{previous_number_of_bikes},{previous_previous_number_of_bikes}\n")
    
    previous_previous_number_of_bikes = previous_number_of_bikes
    previous_number_of_bikes = available_bikes
   