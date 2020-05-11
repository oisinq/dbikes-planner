from . import routes
from . import prediction_service

import threading
from datetime import datetime, timedelta
import pandas as pd
from google.cloud import datastore
import geopy.distance
from flask import request, jsonify
from scipy import spatial
import requests
import uuid


def predict_station(station, minutes, request_type):
    return prediction_service.predict_availability(station['address'], minutes, request_type)


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
    closest_start_stations = station_tree.query(location, k=3, p=3)
    hierarchy = ['high', 'moderate', 'low', 'very low', 'empty']

    trip_time = datetime.now() + timedelta(minutes=int(minutes))

    # NOTE: Don't mix up the index with the "Number" attribute in the DataFrame. They don't match up.
    first_station_index = closest_start_stations[1][0]
    best_station = station_list.iloc[first_station_index]

    results = []

    for index, station_index in enumerate(closest_start_stations[1]):
        station = station_list.iloc[station_index]

        distance = geopy.distance.distance(location, (station['position']['lat'], station['position']['lng']))

        # 84 metres per minute == 1.4 m/s, which is the average urban walking speed
        prediction_response = predict_station(station, int(float(minutes) + (distance.m / 84)),
                                              request_type)

        availability = prediction_response['prediction']

        results.append(prediction_response)

        # If any of these conditions are true, then this is the best station
        if availability == 'high' or (availability == 'moderate' and not is_peak_time(trip_time)):
            return station

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


def is_peak_time(selected_time):
    if 8 <= selected_time.hour <= 10 or 16 <= selected_time.hour <= 18:
        return True

    return False


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

    # To estimate the arrival time at the end station, we estimate the distance between the start and end location,
    # and calculate 90% of this distance (assume 10% of the journey is walked)
    estimated_cycling_distance = geopy.distance.distance(start_location, end_location) / 100.0 * 90.0
    # 420 metres per minute == 7 m/s, which is the average urban cycling speed
    estimated_cycling_minutes = int(float(minutes) + (estimated_cycling_distance.m / 420))

    end_station = find_best_station(end_location, 'bikestands', estimated_cycling_minutes)

    quietest_cycle_route_json = requests.get(
        get_cycle_streets_url(start_station['position'], end_station['position'], 'quietest'))
    fastest_cycle_route_json = requests.get(
        get_cycle_streets_url(start_station['position'], end_station['position'], 'fastest'))
    shortest_cycle_route_json = requests.get(
        get_cycle_streets_url(start_station['position'], end_station['position'], 'shortest'))
    balanced_cycle_route_json = requests.get(
        get_cycle_streets_url(start_station['position'], end_station['position'], 'balanced'))

    start_walking_route_json = requests.get(get_walking_route_url(start_location, start_station['position']))

    if start_walking_route_json.status_code >= 400:
        start_walking_route_json = requests.get(get_hiking_route_url(start_location, start_station['position']))

    end_walking_route_json = requests.get(get_walking_route_url(end_station['position'], end_location))

    if end_walking_route_json.status_code >= 400:
        end_walking_route_json = requests.get(get_hiking_route_url(end_station['position'], end_location))

    result = jsonify({"start_walking_route": start_walking_route_json.json(), "shortest_cycle_route":
        shortest_cycle_route_json.json(), "fastest_cycle_route": fastest_cycle_route_json.json(),
                    "quietest_cycle_route": quietest_cycle_route_json.json(), "balanced_cycle_route":
                          balanced_cycle_route_json.json(), "end_walking_route":
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

    coordinate_list = []

    for coordinate in station_list['position'].values:
        point = (float(coordinate['lat']), float(coordinate['lng']))
        coordinate_list.append(point)

    global station_tree
    station_tree = spatial.KDTree(coordinate_list)


refresh_bikes()
