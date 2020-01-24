import flask
from flask import request, jsonify
from pygam.datasets import wage
from pygam import LinearGAM, s, f, te
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

def setup_dicts(stationGams):
    for station in ['charlemount']:
        my_data = pd.read_csv(f"result_{station}.csv")

        X = my_data[['time_of_day', 'type_of_day', 'day_of_year', 'temperature', 'rain', 'relative_humidity', 'vapour_pressure', 'wind_speed', 'sunshine', 'visibility']].values
        y = my_data['available_bike_stands'].values

        gam = LinearGAM(te(0, 1) + s(2) + s(3) + s(4) + s(5) + s(6) + s(7) + s(8) + s(9), dtype=['numerical', 'categorical', 'numerical', 'numerical', 'numerical', 'numerical', 'numerical', 'numerical', 'numerical', 'numerical'])
        gam.gridsearch(X, y)

        stationGams[station] = gam

stationGams = {}

# we need to store the availability in the past somewhere
# I think just have a list where each item is an object saying the availability at all stops at a given moment in time

setup_dicts(stationGams)

# wiki - https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask
app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def predict_availability():
    if 'station' in request.args:
        station = int(request.args['station'])
    else:
        return "Error: No station field provided. Please specify an id."

    if 'minutes' in request.args:
        minutes = int(request.args['minutes'])
    else:
        return "Error: No minutes field provided. Please specify an id."
    
    gam = stationGams[station]

    

# @app.route('/', methods=['GET'])
# def home():
#     return '''<h1>Distant Reading Archive</h1>
# <p>A prototype API for distant reading of science fiction novels.</p>'''


# @app.route('/api/v1/resources/books/all', methods=['GET'])
# def api_all():
#     return jsonify(books)



# @app.route('/api/v1/resources/books', methods=['GET'])
# def api_id():
#     # Check if an ID was provided as part of the URL.
#     # If ID is provided, assign it to a variable.
#     # If no ID is provided, display an error in the browser.
#     if 'id' in request.args:
#         id = int(request.args['id'])
#     else:
#         return "Error: No id field provided. Please specify an id."

#     # Create an empty list for our results
#     results = []

#     # Loop through the data and match results that fit the requested ID.
#     # IDs are unique, but other fields might return many results
#     for book in books:
#         if book['id'] == id:
#             results.append(book)

#     # Use the jsonify function from Flask to convert our list of
#     # Python dictionaries to the JSON format.
#     return jsonify(results)

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found. Sorry!</p>", 404

app.run()
