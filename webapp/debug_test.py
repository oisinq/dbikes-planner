import pandas as pd
import requests
from station import Station
from station_status import StationStatus
import json

def read_stations():
    result = pd.read_json("https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey=6e5c2a98e60a3336ecaede8f8c8688da25144692")

    addresses = []

    for _index, row in result.iterrows():
        status = StationStatus(row['available_bikes'], int(row['last_update'] / 1000))
        address = row["address"]

        addresses.append(address)

    print(addresses)

def fetch_weather():
    js = requests.get("https://api.openweathermap.org/data/2.5/weather?lat=53.277717&lon=-6.218428&APPID=d8d0b9ed5f181cfbdf3330b0037aff7d&units=metric").text

    weather = json.loads(js)
    parsed_weather = {}


    parsed_weather['rain'] = 0.0
    
    if "rain" in weather:
        if "1h" in weather["rain"]:
            parsed_weather['rain'] = weather["rain"]["1h"]

    parsed_weather['temperature'] = weather['main']['temp']
    parsed_weather['humidity'] = weather['main']['humidity']
    parsed_weather['wind'] = weather['wind']['speed']

    return parsed_weather

print(fetch_weather())