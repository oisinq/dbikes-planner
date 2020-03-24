import clean_data
import pandas as pd
import threading
import time


def update_bike_data():
    result = pd.read_json(
        "https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey=6e5c2a98e60a3336ecaede8f8c8688da25144692")

    for _index, row in result.iterrows():
        station_name = row["address"]

        clean_data.update_record()

        with open(f"./bike_records/result_{station_name}.csv", 'a') as f:
            result.to_csv(f, header=False)



class FetchingThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("Starting...")
        while True:
            time.sleep(60 * 10)
            update_bike_data()
            update_weather_data()
            refresh_model()
