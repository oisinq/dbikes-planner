import os
import shutil
from os import path
from os import listdir
from os.path import isfile, join

import pandas as pd


def main():
    mypath = "/Users/oisin/Coding/ucd/Fourth/fyp/fyp/webapp/stations/"
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f.endswith(".csv") and not f.startswith("all")]

    for file in onlyfiles:
        print(file)
        df = pd.read_csv(file)

        df.drop(df.columns[0], axis=1, inplace=True)

        df.to_csv(file, index=None)


if __name__ == "__main__":
    main()
