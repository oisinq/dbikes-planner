import flask
import pandas as pd
import time
from flask import request, jsonify
from shapely.geometry import Point, MultiPoint
from shapely.ops import nearest_points
from scipy import spatial
import random

def call_ting():
    return random.randint(0,20)

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def predict_availability():
    station_list = pd.read_json("https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey=6e5c2a98e60a3336ecaede8f8c8688da25144692")

    coordinate_list = []

    for coordinate in station_list['position'].values:
        point = (float(coordinate['lat']), float(coordinate['lng']))
        coordinate_list.append(point)

    tree = spatial.KDTree(coordinate_list)

    start_location = 0
    end_location = 0

    if 'start' in request.args:
        longitude, latitude = request.args['start'].split(",")
        start_location = (float(longitude), float(latitude))
    else:
        return "Error: No starting location specified."
    
    if 'end' in request.args:
        longitude, latitude = request.args['end'].split(",")
        end_location = (float(longitude), float(latitude))
    else:
        return "Error: No ending location specified."

    print("...")
    print(start_location)

    closest_start_stations = tree.query(start_location, k=3)
    closest_end_stations = tree.query(end_location, k=3)

    start_station = None
    highest_prediction = -1

    for station_index in closest_start_stations[1]:
        print("Sending a request for " + station_list.iloc[station_index]['address'])
        availability = call_ting()

        if start_station is None or highest_prediction < availability:
            start_station = station_list.iloc[station_index]
            highest_prediction = availability

    end_station = None
    highest_prediction = -1

    for station_index in closest_end_stations[1]:
        print("Sending a request for " + station_list.iloc[station_index]['address'])
        availability = call_ting()

        if end_station is None or highest_prediction < availability:
            end_station = station_list.iloc[station_index]
            highest_prediction = availability

    print(start_station)
    print(end_station)
    

    return "<h1>How's it goin' boss</h1>"


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found. Sorry!</p>", 404

app.run()
