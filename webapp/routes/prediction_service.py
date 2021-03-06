from datetime import datetime, timedelta
from . import routes

from flask import request
import json
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
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


def update_weather():
    print("Updating weather data...")
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

    if "visibility" in request_weather:
        parsed_weather['visibility'] = request_weather['visibility']
    else:
        parsed_weather['visibility'] = 0

    print("Weather data update complete!")

    return parsed_weather


def read_file_for_station(station_name):
    print(f"opening {station_name} {datetime.now()}")
    if "/" in station_name:
        data = pd.read_csv('gs://dbikes-planner.appspot.com/station_records/Princes Street.csv')
    else:
        data = pd.read_csv(f"gs://dbikes-planner.appspot.com/station_records/{station_name}.csv")

    return data


def get_fitted_bikestands_model(station_name):
    data = read_file_for_station(station_name)

    model = KNeighborsClassifier(n_neighbors=10, weights='distance')

    model.fit(data.iloc[:, [2, 3, 4, 6, 7, 9, 10, 12, 15]], data.iloc[:, 14])

    return model


def get_fitted_bikes_model(station_name):
    data = read_file_for_station(station_name)

    model = KNeighborsClassifier(n_neighbors=10, weights='distance')

    model.fit(data.iloc[:, [2, 3, 4, 6, 7, 9, 10, 12, 15]], data.iloc[:, 13])

    return model


def predict_availability(station, minutes, type):
    current_time = datetime.now()
    request_time = current_time + timedelta(minutes=minutes)

    time_of_day = (request_time.hour * 60 + request_time.minute) * 60 + request_time.second
    type_of_day = 0 if request_time.weekday() < 5 else 10
    day_of_year = request_time.timetuple().tm_yday

    if type == 'bikes':
        model = get_fitted_bikes_model(station)
    else:
        model = get_fitted_bikestands_model(station)

    weather = update_weather()

    prediction = model.predict([[time_of_day, type_of_day, day_of_year, weather['temperature'],
                                 weather['humidity'], weather['wind_speed'], weather['rain'],
                                 weather['visibility'], current_time.timestamp()//3600]])

    prediction_probs = model.predict_proba(
        [[time_of_day, type_of_day, day_of_year, weather['temperature'],
          weather['humidity'], weather['wind_speed'], weather['rain'],
          weather['visibility'], current_time.timestamp()//3600]])

    classes = model.classes_
    probs = {}

    for index, label in enumerate(classes):
        probs[label] = prediction_probs[0][index]

    return {"prediction": prediction[0], "probabilities": probs}


@routes.route('/predict/<journey_type>', methods=['GET'])
def predict_bike_stands_availability(journey_type):

    if 'station' in request.args:
        station = request.args['station']
    else:
        return "Error: No station field provided. Please specify an id."

    if 'minutes' in request.args:
        minutes = int(request.args['minutes'])
    else:
        minutes = 0

    if journey_type != 'bikes' and journey_type != 'bikestands':
        return "Error: prediction type invalid. Must be /bikes or /bikestands."

    if station not in station_names:
        return "Error: Invalid station provided. Please specify a valid station name"

    result = predict_availability(station, minutes, journey_type)

    return json.dumps(result)


@routes.errorhandler(404)
def page_not_found():
    return "<h1>404</h1><p>The resource could not be found. Sorry!</p>", 404
