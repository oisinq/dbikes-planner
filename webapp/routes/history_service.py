from datetime import datetime, timedelta
from routes import *

import update_station_records
from flask import request
import json
import datetime
import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from apscheduler.schedulers.background import BackgroundScheduler
import threading
import time
import requests

#todo: might be able to get rid of this
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
                 'Heuston Bridge (North)', 'Leinster Street South', 'Blackhall Place', "Princes Street"]


@routes.route('/history/<station_name>/<mode>', methods=['GET'])
def generate_history_graph(station_name, mode):
    if station_name not in station_names:
        return "Error: Please specify a valid station"

    if "/" in station_name:
        data = pd.read_csv('gs://dbikes-planner.appspot.com/station_records/Princes Street.csv', usecols=[0, 1, 2, 3, 5])
    else:
        data = pd.read_csv(f"gs://dbikes-planner.appspot.com/station_records/{station_name}.csv", usecols=[0, 1, 2, 3, 5])

    d = datetime.datetime.now()

    if d.isoweekday() in range(1, 6):
        historical_data = data[data['type_of_day'] == 0].tail(17000)
    else:
        historical_data = data[data['type_of_day'] == 10].tail(17000)

    #todo: rename variable
    nov_mask = pd.to_datetime(historical_data['iso_date']).map(lambda x: (x - datetime.datetime(1970, 1, 1)).days) == (datetime.datetime.now() -
                                                                                                                       datetime.datetime(1970, 1, 1)).days
    todays_data = historical_data[nov_mask]

    if mode == 'bikestands':
        historical_x, historical_y = (historical_data['time_of_day'], historical_data['available_bike_stands'])
        today_x, today_y = (todays_data['time_of_day'], todays_data['available_bike_stands'])
    else:
        historical_x, historical_y = (historical_data['time_of_day'], historical_data['available_bikes'])
        today_x, today_y = (todays_data['time_of_day'], todays_data['available_bikes'])

    coefficients = np.polyfit(historical_x, historical_y, 50)
    poly_func = np.poly1d(coefficients)

    new_historical_x = np.linspace(18000, 86400) # explain
    new_historical_y = poly_func(new_historical_x)

    result = {"graph": [], "todays_graph": []}

    for x_value, y_value in zip(new_historical_x, new_historical_y):
        result['graph'].append((x_value, y_value))

    for x_value, y_value in zip(today_x, today_y):
        result['todays_graph'].append((x_value, y_value))

    return jsonify(result)


# This route is needed for backwards compatibility with old versions of the app
@routes.route('/history/<station_name>', methods=['GET'])
def old_generate_history_graph(station_name):
    return generate_history_graph(station_name, 'bikes')