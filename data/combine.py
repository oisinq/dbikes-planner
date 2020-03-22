import os
import shutil
from os import path
from os import listdir
from os.path import isfile, join

import pandas as pd


def main():
    mypath = "/Users/oisin/Coding/ucd/Fourth/fyp/fyp/data"

    my_data = pd.read_csv("digitalocean_times.csv")

    for index, line in my_data.iterrows():
        if '/' in line['address']:
            station_name = "Princes Street"
        else:
            station_name = line['address']

        with open(f"{station_name}.csv", 'a') as f:
            f.write(f"{line['number']},{line['name']},{station_name},{line['bike_stands']},"
                    f"{line['available_bike_stands']},{line['last_update']}\n")


if __name__ == "__main__":
    main()