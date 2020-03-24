import flask
from flask import request
from pygam import LinearGAM, s, te
import pandas as pd
from datetime import datetime
from model.station import Station
from model.station_status import StationStatus
import threading
import requests
import json
import time

station_names = ['Smithfield North', 'Parnell Square North', 'Clonmel Street', 'Avondale Road', 'Mount Street Lower', 'Christchurch Place', 'Grantham Street', 'Pearse Street', 'York Street East', 'Excise Walk', 'Fitzwilliam Square West', 'Portobello Road', 'St. James Hospital (Central)', 'Parnell Street', 'Frederick Street South', 'Custom House', 'Rathdown Road', "North Circular Road (O'Connell's)", 'Hanover Quay', 'Oliver Bond Street', 'Collins Barracks Museum', 'Brookfield Road', 'Benson Street', 'Earlsfort Terrace', 'Golden Lane', 'Deverell Place', 'Wilton Terrace (Park)', 'John Street West', 'Fenian Street', 'Merrion Square South', 'South Dock Road', 'City Quay', 'Exchequer Street', 'The Point', 'Hatch Street', 'Lime Street', 'Charlemont Street', 'Kilmainham Gaol', 'Hardwicke Place', 'Wolfe Tone Street', 'Francis Street', 'Greek Street', 'Guild Street', 'Herbert Place', 'High Street', 'Western Way', 'Talbot Street', 'Newman House', "Sir Patrick's Dun", 'New Central Bank', 'Grangegorman Lower (Central)', 'King Street North', 'Killarney Street', 'Herbert Street', 'Hanover Quay East', 'Custom House Quay', 'Molesworth Street', 'Georges Quay', 'Kilmainham Lane', 'Mount Brown', 'Market Street South', 'Kevin Street', 'Eccles Street East', 'Grand Canal Dock', 'Merrion Square East', 'York Street West', "St. Stephen's Green South", 'Denmark Street Great', 'Royal Hospital', 'Heuston Station (Car Park)', 'Grangegorman Lower (North)', "St. Stephen's Green East", 'Heuston Station (Central)', 'Townsend Street', "George's Lane", 'Phibsborough Road', 'Eccles Street', 'Portobello Harbour', 'Mater Hospital', 'Blessington Street', 'James Street', 'Mountjoy Square East', 'Merrion Square West', 'Convention Centre', 'Hardwicke Street', 'Parkgate Street', 'Dame Street', 'Heuston Bridge (South)', 'Cathal Brugha Street', 'Sandwith Street', 'Buckingham Street Lower', 'Rothe Abbey', 'Charleville Road', "Princes Street / O'Connell Street", 'Upper Sherrard Street', 'Fitzwilliam Square East', 'Grattan Street', 'St James Hospital (Luas)', 'Harcourt Terrace', 'Bolton Street', 'Jervis Street', 'Ormond Quay Upper', 'Grangegorman Lower (South)', 'Mountjoy Square West', 'Wilton Terrace', 'Emmet Road', 'Heuston Bridge (North)', 'Leinster Street South', 'Blackhall Place']
stations = {}

class myThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def fetch_bike_data():
        result = pd.read_json("https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey=6e5c2a98e60a3336ecaede8f8c8688da25144692")

        print("fetching...")
        for _index, row in result.iterrows():
            status = StationStatus(row['available_bikes'], int(row['last_update'] / 1000))

            stations[row["address"]].add_status(status)

        with open('../bike_times.csv', 'a') as f:
            result.to_csv(f, header=False)

        time.sleep(60*10)
    
    def run(self):
        print ("Starting...")
        fetch_bike_data()

def fetch_weather_data():
    js = requests.get("https://api.openweathermap.org/data/2.5/weather?lat=53.277717&lon=-6.218428&APPID=d8d0b9ed5f181cfbdf3330b0037aff7d&units=metric").text

    weather = json.loads(js)
    parsed_weather = {}

    parsed_weather['rain']  = 0.0

    if "rain" in weather:
        if "1h" in weather["rain"]:
            parsed_weather['rain'] = weather["rain"]["1h"]

    parsed_weather['temperature'] = weather['main']['temp']
    parsed_weather['humidity'] = weather['main']['humidity']
    parsed_weather['wind'] = weather['wind']['speed']

    return parsed_weather

def setup_gams(station_gams):
    for station_name in station_names:
        try:
            print("trying " + f"./result_{station_name}.csv")
            my_data = pd.read_csv(open(f"./result_{station_name}.csv"))
            print("it opened...")
            #my_data = pd.read_csv(open(f"./result_charlemount.csv"))

            attributes = ['time_of_day', 'type_of_day', 'day_of_year', 'temperature', 'rain', 'relative_humidity','wind_speed']

            X = my_data[attributes].values
            y = my_data['available_bike_stands'].values

            gam = LinearGAM(te(0, 1) + s(2) + s(3) + s(4) + s(5) + s(6), n_splines=[65, 20, 20, 10, 20, 10, 25], dtype=['numerical', 'categorical', 'numerical', 'numerical', 'numerical', 'numerical', 'numerical'])
            gam.gridsearch(X, y)

            station_gams[station_name] = gam
        except:
            pass

def setup_stations(stations):
    for station_name in station_names:
        station = Station(station_name)
        stations[station_name] = station

def get_current_gam_attributes():
    weather = fetch_weather_data()

    # attributes = ['time_of_day', 'type_of_day', 'day_of_year', 'temperature', 'rain', 'relative_humidity','wind_speed']

    current_datetime = datetime.now()

    time_of_day = (current_datetime.hour * 60 + current_datetime.minute) * 60 + current_datetime.second

    if current_datetime.weekday() <= 4:
        type_of_day = '0'
    else:
        type_of_day = '1'
    
    day_of_year = current_datetime.timetuple().tm_yday
    
    print(weather)

    return [time_of_day, type_of_day, day_of_year, weather['temperature'], weather['rain'], weather['humidity'], weather['wind']]

station_gams = {}
setup_stations(stations)

# thread1 = myThread()
# thread1.start()
# thread1.join()

setup_gams(station_gams)


# wiki - https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask
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
    
    gam = station_gams[station]

    print(get_current_gam_attributes())

    prediction = gam.predict([get_current_gam_attributes()])

    # need to take into account previous availability next

    return f"<h1>My answer is...</h1><p>{prediction}. Am I close?</p>"


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found. Sorry!</p>", 404

app.run()
