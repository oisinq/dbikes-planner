from datetime import datetime, timedelta
from routes import *

import update_station_records
from flask import request
import json
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from apscheduler.schedulers.background import BackgroundScheduler
import threading
import time
import requests

station_names = ['Smithfield North', 'Parnell Square North', 'Clonmel Street', 'Avondale Road', 'Mount Street Lower',
                 'Christchurch Place', 'Grantham Street', 'Pearse Street', 'York Street East', 'Excise Walk',
                 'Fitzwilliam Square West', 'Portobello Road', 'St. James Hospital (Central)', 'Parnell Street',
                 'Frederick Street South', 'Custom House', 'Rathdown Road', "North Circular Road (O'Connell's)",
                 'Hanover Quay', 'Oliver Bond Street', 'Collins Barracks Museum', 'Brookfield Road', 'Benson Street',
                 'Earlsfort Terrace', 'Golden Lane', 'Deverell Place', 'Wilton Terrace (Park)', 'John Street West',
                 'Fenian Street', 'Merrion Square South', 'South Dock Road', 'City Quay', 'Exchequer Street',
                 'The Point', 'Broadstone', 'Hatch Street', 'Lime Street', 'Charlemont Street', 'Kilmainham Gaol',
                 'Hardwicke Place', 'Wolfe Tone Street', 'Francis Street', 'Greek Street', 'Guild Street',
                 'Herbert Place', 'High Street', 'Western Way', 'Talbot Street', 'Newman House', "Sir Patrick's Dun",
                 'New Central Bank', 'Grangegorman Lower (Central)', 'King Street North', 'Killarney Street',
                 'Herbert Street', 'Hanover Quay East', 'Custom House Quay', 'Molesworth Street', 'Georges Quay',
                 'Kilmainham Lane', 'Mount Brown', 'Market Street South', 'Kevin Street', 'Eccles Street East',
                 'Grand Canal Dock', 'Merrion Square East', 'York Street West', "St. Stephen's Green South",
                 'Denmark Street Great', 'Royal Hospital', 'Heuston Station (Car Park)', 'Grangegorman Lower (North)',
                 "St. Stephen's Green East", 'Heuston Station (Central)', 'Townsend Street', "George's Lane",
                 'Phibsborough Road', 'Eccles Street', 'Portobello Harbour', 'Mater Hospital', 'Blessington Street',
                 'James Street', 'Mountjoy Square East', 'Merrion Square West', 'Convention Centre', 'Hardwicke Street',
                 'Parkgate Street', 'Dame Street', 'Heuston Bridge (South)', 'Cathal Brugha Street', 'Sandwith Street',
                 'Buckingham Street Lower', 'Rothe Abbey', 'Charleville Road', "Princes Street / O'Connell Street",
                 'Upper Sherrard Street', 'Fitzwilliam Square East', 'Grattan Street', 'St James Hospital (Luas)',
                 'Harcourt Terrace', 'Bolton Street', 'Jervis Street', 'Ormond Quay Upper',
                 'Grangegorman Lower (South)', 'Mountjoy Square West', 'Wilton Terrace', 'Emmet Road',
                 'Heuston Bridge (North)', 'Leinster Street South', 'Blackhall Place']

weather = {}
bikes_model = {}
bikestands_model = {}


def update_weather():
    js = requests.get(
        "https://api.openweathermap.org/data/2.5/weather?lat=53.277717&lon=-6.218428&APPID"
        "=d8d0b9ed5f181cfbdf3330b0037aff7d&units=metric").text

    request_weather = json.loads(js)

    parsed_weather = {'rain': 0.0}

    if "rain" in request_weather and "1h" in request_weather["rain"]:
        parsed_weather['rain'] = request_weather["rain"]["1h"]

    parsed_weather['temperature'] = request_weather['main']['temp']
    parsed_weather['humidity'] = request_weather['main']['humidity']
    parsed_weather['wind_speed'] = request_weather['wind']['speed']
    parsed_weather['visibility'] = request_weather['visibility']

    global weather
    weather = parsed_weather


def update_bike_data(current_weather):
    result = pd.read_json(
        "https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey=6e5c2a98e60a3336ecaede8f8c8688da25144692")

    for _index, row in result.iterrows():
        update_station_records.update_record(row, current_weather)


def fit_model(station_name):
    if "/" in station_name:
        data = pd.read_csv(open(f'stations/Princes Street.csv', 'r'))
    else:
        data = pd.read_csv(open(f'stations/{station_name}.csv', 'r'))

    bikes_model[station_name].fit(data.iloc[:, [2, 3, 4, 6, 7, 9, 10, 12]], data.iloc[:, 13])
    bikestands_model[station_name].fit(data.iloc[:, [2, 3, 4, 6, 7, 9, 10, 12]], data.iloc[:, 14])
    print(f"fitted for {station_name}")


def refresh_model():
    for station_name in station_names:
        fit_model(station_name)


def refresh_data():
    update_weather()
    update_bike_data(weather)
    refresh_model()


class FetchingThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("Starting...")
        while True:
            refresh_data()

            print("thread: i sleep...")
            time.sleep(60 * 5)


def setup():
    for station_name in station_names:
        bikes_model[station_name] = KNeighborsClassifier(n_neighbors=5, weights='distance')
        bikestands_model[station_name] = KNeighborsClassifier(n_neighbors=5, weights='distance')


setup()

# fetching_thread = FetchingThread()
# fetching_thread.start()
refresh_data()

scheduler = BackgroundScheduler()
scheduler.add_job(func=refresh_data, trigger="interval", minutes=5)
scheduler.start()

@routes.route('/predict/bikes', methods=['GET'])
def predict_bike_availability():
    if 'station' in request.args:
        station = request.args['station']
    else:
        return "Error: No station field provided. Please specify an id."

    if 'minutes' in request.args:
        minutes = int(request.args['minutes'])
    else:
        return "Error: No minutes field provided. Please specify an id."

    if station not in bikes_model.keys():
        return "Error: Invalid station provided. Please specify a valid station name"

    current_time = datetime.now()
    request_time = current_time + timedelta(minutes=minutes)

    time_of_day = (request_time.hour * 60 + request_time.minute) * 60 + request_time.second
    type_of_day = 0 if request_time.weekday() < 5 else 10
    day_of_year = request_time.timetuple().tm_yday

    prediction = bikes_model[station].predict([[time_of_day, type_of_day, day_of_year, weather['temperature'],
                                                weather['humidity'], weather['wind_speed'], weather['rain'],
                                                weather['visibility']]])

    prediction_probs = bikes_model[station].predict_proba(
        [[time_of_day, type_of_day, day_of_year, weather['temperature'],
          weather['humidity'], weather['wind_speed'], weather['rain'],
          weather['visibility']]])

    classes = bikes_model[station].classes_
    probs = {}

    for index, label in enumerate(classes):
        probs[label] = prediction_probs[0][index]

    result = {"prediction": prediction[0], "probabilities": probs}

    return json.dumps(result)


@routes.route('/predict/bikestands', methods=['GET'])
def predict_bike_stands_availability():
    if 'station' in request.args:
        station = request.args['station']
    else:
        return "Error: No station field provided. Please specify an id."

    if 'minutes' in request.args:
        minutes = int(request.args['minutes'])
    else:
        minutes = 0

    if station not in bikes_model.keys():
        return "Error: Invalid station provided. Please specify a valid station name"

    current_time = datetime.now()
    request_time = current_time + timedelta(minutes=minutes)

    time_of_day = (request_time.hour * 60 + request_time.minute) * 60 + request_time.second
    type_of_day = 0 if request_time.weekday() < 5 else 10
    day_of_year = request_time.timetuple().tm_yday

    prediction = bikes_model[station].predict([[time_of_day, type_of_day, day_of_year, weather['temperature'],
                                                weather['humidity'], weather['wind_speed'], weather['rain'],
                                                weather['visibility']]])

    prediction_probs = bikes_model[station].predict_proba(
        [[time_of_day, type_of_day, day_of_year, weather['temperature'],
          weather['humidity'], weather['wind_speed'], weather['rain'],
          weather['visibility']]])

    classes = bikes_model[station].classes_
    probs = {}

    for index, label in enumerate(classes):
        probs[label] = prediction_probs[0][index]

    result = {"prediction": prediction[0], "probabilities": probs}

    return json.dumps(result)


@routes.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found. Sorry!</p>", 404