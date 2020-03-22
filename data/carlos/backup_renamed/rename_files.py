import os
import shutil
from os import path
from os import listdir
from os.path import isfile, join

import pandas as pd


def main():
    mypath = "/Users/oisin/Coding/ucd/Fourth/fyp/fyp/data/carlos"
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f.endswith(".csv") and 'export' in f]

    for file in onlyfiles:
        my_data = pd.read_csv(file)

        os.rename(file, f"{my_data['address'][0]}.csv")


if __name__ == "__main__":
    main()