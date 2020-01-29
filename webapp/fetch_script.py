#!/usr/bin/python3

import pandas as pd

result = pd.read_json("https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey=6e5c2a98e60a3336ecaede8f8c8688da25144692")

with open('bike_times.csv', 'a') as f:
    result.to_csv(f, header=False)