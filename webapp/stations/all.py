import os
import shutil
from os import path
from os import listdir
from os.path import isfile, join

import pandas as pd

def main():
    mypath = "/Users/oisin/Coding/ucd/Fourth/fyp/fyp/webapp/stations/"
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f.endswith(".csv")]

    f = open(f'all.csv', 'a')

    f.write("available_bikes,available_bike_stands,time_of_day,type_of_day,day_of_year,iso_date,temperature,relative_humidity,vapour_pressure,wind_speed,rain,sunshine,visibility,bike_availability,bike_stand_availability,address\n")

    for file in onlyfiles:
        print(file)
        my_data = pd.read_csv(file)
        my_data['address'] = file.split(".csv")[0]

        f.write(my_data.to_csv(header=False, index=False))


if __name__ == "__main__":
    main()
