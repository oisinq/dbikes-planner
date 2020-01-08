import pandas as pd
from datetime import datetime

def datetime_to_seconds(t):
    return (t.hour * 60 + t.minute) * 60 + t.second

def seconds_in_previous_days(t):
    return t.timetuple().tm_yday * 24*60*60

my_data = pd.read_csv("charlemount.csv")
f = open('result_charlemount.csv', 'w')
f.write("available_bike_stands,time_of_day,type_of_day,time_of_year,iso_date\n")

for line in my_data.sort_values('last_update').values:
    available_bikes = line[4]
    epoch_time = line[5]
    
    time = datetime.fromtimestamp(epoch_time/1000)
    
    day_index = time.weekday()
    day_type = ''

    if day_index <= 4:
        day_type = '0'
    else:
        day_type = '1'

    f.write(f"{available_bikes},{datetime_to_seconds(time)},{day_type},{seconds_in_previous_days(time) + datetime_to_seconds(time)},{time.isoformat()}\n")