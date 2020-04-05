import os
import shutil
from os import path
from os import listdir
from os.path import isfile, join
from datetime import datetime

import pandas as pd


def timestamp_fix():
    mypath = "/Users/oisin/Coding/ucd/Fourth/fyp/fyp/webapp/stations/"
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f.endswith(".csv") and not f.startswith("all")]

    for file in onlyfiles:
        print(file)
        df = pd.read_csv(file)

        timestamp = df['iso_date']

        result = []

        for stamp in timestamp:
            result.append(int(datetime.fromisoformat(stamp).timestamp()))

        df['unix_timestamp'] = result
        df.to_csv(file, index=None)


def ordinal_categories():
    mypath = "/Users/oisin/Coding/ucd/Fourth/fyp/fyp/webapp/stations/"
    onlyfiles = [f for f in listdir(mypath) if
                 isfile(join(mypath, f)) and f.endswith(".csv") and not f.startswith("all")]

    for file in onlyfiles:
        print(file)
        df = pd.read_csv(file)

        bike_availability = df['bike_availability']
        bike_stand_availability = df['bike_stand_availability']

        bike_result = []
        stand_result = []

        ranks = ['empty', 'very low', 'low', 'moderate', 'high']

        for value in bike_availability:

            bike_result.append(ranks.index(value))

        for value in bike_stand_availability:
            stand_result.append(ranks.index(value))

        df['bike_availability_ordinal'] = bike_result
        df['bike_stand_availability_ordinal'] = stand_result
        df.to_csv(file, index=None)


if __name__ == "__main__":
    timestamp_fix()
