import threading
import time
from datetime import datetime

import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from google.cloud import datastore

from . import routes
from . import knn_availability_service
import flask
import geopy.distance
from flask import request, jsonify, url_for
from scipy import spatial
import requests
import uuid

def predict_station(station, minutes, request_type):
    return knn_availability_service.predict_availability(station['address'], minutes, request_type)


def get_cycle_streets_url(start, end, plan_type):
    return f"https://www.cyclestreets.net/api/journey.json?key=b81a31ea96441895&itinerarypoints={start['lng']}," \
           f"{start['lat']}|{end['lng']},{end['lat']}&plan={plan_type}"


def get_walking_route_url(start, end):
    if type(start) is tuple:
        return f"https://api.openrouteservice.org/v2/directions/foot-walking?api_key" \
               f"=5b3ce3597851110001cf6248b66c64a9ecee404f89d0465e2e02f92c" \
               f"&start={start[1]},{start[0]}" \
               f"&end={end['lng']},{end['lat']}"
    else:
        return f"https://api.openrouteservice.org/v2/directions/foot-walking?api_key=5b3ce3597851110001cf6248b66c64a" \
               f"9ecee404f89d0465e2e02f92c&start={start['lng']},{start['lat']}&end={end[1]},{end[0]}"


def get_hiking_route_url(start, end):
    if type(start) is tuple:
        return f"https://api.openrouteservice.org/v2/directions/foot-hiking?api_key" \
               f"=5b3ce3597851110001cf6248b66c64a9ecee404f89d0465e2e02f92c" \
               f"&start={start[1]},{start[0]}" \
               f"&end={end['lng']},{end['lat']}"
    else:
        return f"https://api.openrouteservice.org/v2/directions/foot-hiking?api_key=5b3ce3597851110001cf6248b66c64a" \
               f"9ecee404f89d0465e2e02f92c&start={start['lng']},{start['lat']}&end={end[1]},{end[0]}"


def get_current_availability(station, request_type):
    if request_type == 'bikes':
        current = station['available_bikes']
    else:
        current = station['available_bike_stands']

    if current == 0:
        return 'empty'
    elif current < 2:
        return 'very low'
    elif current < 5:
        return 'low'
    elif current < 10:
        return 'moderate'
    else:
        return "high"


station_list = None
station_tree = None


def find_best_station(location, request_type, minutes):
    closest_start_stations = station_tree.query(location, k=3)
    hierarchy = ['high', 'moderate', 'low', 'very low', 'empty']

    # NOTE: Don't mix up the index with the "Number" attribute in the DataFrame. They don't match up.
    first_station_index = closest_start_stations[1][0]
    best_station = station_list.iloc[first_station_index]
    results = []

    for index, station_index in enumerate(closest_start_stations[1]):
        station = station_list.iloc[station_index]

        # current_availability = get_current_availability(station, request_type) # Not currently used, could be useful

        distance = geopy.distance.distance(location, (station['position']['lat'], station['position']['lng']))

        prediction_response = predict_station(station_list.iloc[station_index], int(float(minutes) + (distance.m / 84)),
                                              request_type) # 84 metres per minute == 1.4 m/s, which is the average urban walking speed

        availability = prediction_response['prediction']

        results.append(prediction_response)
        # todo: add a "very high" availability & take it into account if we jump between "very high" and "empty"
        # todo: also look into normalising data

        # todo: quickfix this
        if availability == 'high':  # if a station has high availability, we return now because it's the closest
            return station_list.iloc[station_index]

    # This picks the best station from the outputs (ignoring distance, since k=3)
    for level_index, level in enumerate(hierarchy[1:]):  # Ignores 'high', because of the previous if
        results_at_level = list(filter(lambda result: result['prediction'] == level, results))

        if len(results_at_level) == 1:  # if just one at this level, return it
            station_index = closest_start_stations[1][results.index(results_at_level[0])]
            return station_list.iloc[station_index]
        elif len(results_at_level) > 1:  # if more than one at this level, return the station who has the better chance
            max_item = max(results_at_level, key=lambda x: x['probabilities'][hierarchy[level_index+1]])
            station_index = closest_start_stations[1][results.index(max_item)]
            return station_list.iloc[station_index]

    return best_station


@routes.route('/route', methods=['GET'])
def generate_route():
    print(f"started {datetime.now()}")

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

    if 'minutes' in request.args:
        minutes = request.args['minutes']
    else:
        return "Error: No minutes specified."

    start_station = find_best_station(start_location, 'bikes', minutes)

    end_station = find_best_station(end_location, 'bikestands', minutes)

    quietest_cycle_route_json = requests.get(
        get_cycle_streets_url(start_station['position'], end_station['position'], 'quietest'))
    fastest_cycle_route_json = requests.get(
        get_cycle_streets_url(start_station['position'], end_station['position'], 'fastest'))
    shortest_cycle_route_json = requests.get(
        get_cycle_streets_url(start_station['position'], end_station['position'], 'shortest'))

    start_walking_route_json = requests.get(get_walking_route_url(start_location, start_station['position']))

    if start_walking_route_json.status_code >= 400:
        start_walking_route_json = requests.get(get_hiking_route_url(start_location, start_station['position']))

    end_walking_route_json = requests.get(get_walking_route_url(end_station['position'], end_location))

    if end_walking_route_json.status_code >= 400:
        end_walking_route_json = requests.get(get_hiking_route_url(end_station['position'], end_location))

    result = jsonify({"start_walking_route": start_walking_route_json.json(), "shortest_cycle_route":
        shortest_cycle_route_json.json(), "fastest_cycle_route": fastest_cycle_route_json.json(),
                    "quietest_cycle_route": quietest_cycle_route_json.json(), "end_walking_route":
                        end_walking_route_json.json(), "start_station": start_station['address'],
                    "end_station": end_station['address'], "id": uuid.uuid4()})

    print(f"starting thread {datetime.now()}")
    save_route_thread = SaveRouteThread(result)
    save_route_thread.start()

    return result


class SaveRouteThread(threading.Thread):
    def __init__(self, result):
        threading.Thread.__init__(self)
        self.result = result

    def run(self):
        datastore_client = datastore.Client()

        id = uuid.uuid4()
        route_key = datastore_client.key('Route', str(id))

        print(str(id))

        route = datastore.Entity(key=route_key, exclude_from_indexes=['route'])
        route.update({"route": self.result.get_data(as_text=True)})

        datastore_client.put(route)


@routes.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found. Sorry!</p>", 404


def refresh_bikes():

    global station_list
    station_list = pd.read_json(
        "https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey=6e5c2a98e60a3336ecaede8f8c8688da25144692")
    station_list = station_list.sort_values(by='number')

    coordinate_list = []

    for coordinate in station_list['position'].values:
        point = (float(coordinate['lat']), float(coordinate['lng']))
        coordinate_list.append(point)

    global station_tree
    station_tree = spatial.KDTree(coordinate_list)


refresh_bikes()

# class RefreshThread(threading.Thread):
#     def __init__(self):
#         threading.Thread.__init__(self)
#
#     def run(self):
#         while True:
#             global station_list
#             station_list = pd.read_json(
#                 "https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey=6e5c2a98e60a3336ecaede8f8c8688da25144692")
#             time.sleep(5*60)

# scheduler = BackgroundScheduler()
# scheduler.add_job(func=refresh_bikes, trigger="interval", minutes=5)
# scheduler.start()
