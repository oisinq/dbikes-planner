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

def best_station(location, station_list, station_tree):
    closest_start_stations = station_tree.query(location, k=3)

    station = None
    highest_prediction = -1

    for station_index in closest_start_stations[1]:
        print("Sending a request for " + station_list.iloc[station_index]['address'])
        availability = call_ting()

        if station is None or highest_prediction < availability:
            station = station_list.iloc[station_index]
            highest_prediction = availability
    
    return station

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def predict_availability():
    station_list = pd.read_json("https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey=6e5c2a98e60a3336ecaede8f8c8688da25144692")

    coordinate_list = []

    for coordinate in station_list['position'].values:
        point = (float(coordinate['lat']), float(coordinate['lng']))
        coordinate_list.append(point)

    station_tree = spatial.KDTree(coordinate_list)

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

    start_station = best_station(start_location, station_list, station_tree)
    end_station = best_station(end_location, station_list, station_tree)

    print(start_station)
    print(end_station)
    

    return "<h1>How's it goin' boss</h1>"


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found. Sorry!</p>", 404

app.run()
