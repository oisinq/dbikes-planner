import pandas as pd

my_data = pd.read_csv("result_Charlemont Street.csv")
f = open('charlemont_with_category.csv', 'w')

f.write("available_bike_stands,time_of_day,type_of_day,time_of_year,day_of_year,iso_date,temperature,rain,relative_humidity,vapour_pressure,wind_speed,sunshine,visibility,change_in_bike_availability,epoch,bikes_at_t1,bikes_at_t2,category\n")

i = 0
for line in my_data.values:
    if i == 0:
        i = 1
        continue
    category = ''

    available_bikes = int(line[0])
    if available_bikes == 0:
        category = 'empty'
    elif available_bikes < 2:
        category = 'very low'
    elif available_bikes < 5:
        category = 'low'
    elif available_bikes < 10:
        category = 'moderate'
    else:
        category = "high"

    for word in line:
        f.write(f"{word},")
    f.write(f"{category}\n")