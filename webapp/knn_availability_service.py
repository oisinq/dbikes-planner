import append_data
import flask
from flask import request
import json
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from station import Station
from station_status import StationStatus
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

stations = {}
weather = {}
bikes_model = {}


def get_current_weather():
    js = requests.get(
        "https://api.openweathermap.org/data/2.5/weather?lat=53.277717&lon=-6.218428&APPID"
        "=d8d0b9ed5f181cfbdf3330b0037aff7d&units=metric").text

    request_weather = json.loads(js)
    parsed_weather = {'rain': 0.0}

    if "rain" in request_weather:
        if "1h" in request_weather["rain"]:
            parsed_weather['rain'] = request_weather["rain"]["1h"]

    parsed_weather['temperature'] = request_weather['main']['temp']
    parsed_weather['humidity'] = request_weather['main']['humidity']
    parsed_weather['wind_speed'] = request_weather['wind']['speed']
    parsed_weather['visibility'] = request_weather['visibility']

    return parsed_weather


def update_bike_data(current_weather):
    result = pd.read_json(
        "https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey=6e5c2a98e60a3336ecaede8f8c8688da25144692")

    for _index, row in result.iterrows():
        station_name = row["address"]

        status = StationStatus(row['available_bikes'], int(row['last_update'] / 1000))
        stations[station_name].add_status(status)

        append_data.update_record(current_weather, row)


def fit_model(station_name):
    if "/" in station_name:
        data = pd.read_csv(open(f'stations/Princes Street.csv', 'r'))
    else:
        data = pd.read_csv(open(f'stations/{station_name}.csv', 'r'))

    bikes_model[station_name].fit(data.iloc[:, [2,3,4,6,7,9,10,12]], data.iloc[:, 13])
    print(f"fitted for {station_name}")


def refresh_model():
    for station in stations.values():
        station_name = station.name

        fit_model(station_name)


class FetchingThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("Starting...")
        while True:
            weather = get_current_weather()
            update_bike_data(weather)
            refresh_model()

            print("thread: i sleep...")
            time.sleep(60*5)


def setup():
    for station_name in station_names:
        station = Station(station_name)
        stations[station_name] = station

        bikes_model[station_name] = KNeighborsClassifier(n_neighbors=3, weights='distance')


setup()

fetching_thread = FetchingThread()
fetching_thread.start()
#fetching_thread.join()

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def predict_availability():
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

    prediction = 'yurt'

    return f"<h1>My answer is...</h1><p>{prediction}. Am I close?</p>"


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found. Sorry!</p>", 404


app.run()
