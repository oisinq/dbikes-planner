import pandas as pd
from datetime import datetime

def datetime_to_seconds(t):
    return (t.hour * 60 + t.minute) * 60 + t.second

def seconds_in_previous_days(t):
    return t.timetuple().tm_yday * 24*60*60

def nearestTime(items, pivot):
    return min(items, key=lambda x: abs(x - pivot))

dictionary = {}
my_data = pd.read_csv("weather.csv")

for line in my_data.values:
    date = datetime.strptime(line[0], '%d-%b-%Y %H:%M')
    dictionary[date] = line

print(dictionary.keys)

my_data = pd.read_csv("charlemount.csv")
f = open('result_charlemount.csv', 'w')
f.write("available_bike_stands,time_of_day,type_of_day,time_of_year,day_of_year,iso_date,temperature,rain,relative humidity,vapour_pressure,wind speed, sunshine, visibility\n")

for line in my_data.sort_values('last_update').values:
    available_bikes = line[4]
    epoch_time = line[5]
    
    time = datetime.fromtimestamp(epoch_time/1000)
    
    weather_date = nearestTime(dictionary.keys(), time)

    weather_line = dictionary[weather_date]

    day_index = time.weekday()
    day_type = ''

    if day_index <= 4:
        day_type = '0'
    else:
        day_type = '1'

    f.write(f"{available_bikes},{datetime_to_seconds(time)},{day_type},{seconds_in_previous_days(time) + datetime_to_seconds(time)}," + \
    f"{time.timetuple().tm_yday},{time.isoformat()},{weather_line[4]},{weather_line[1]},{weather_line[9]},{weather_line[8]},{weather_line[12]},{weather_line[17]},{weather_line[18]}\n")