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


@routes.route('/history/<station_name>', methods=['GET'])
def generate_history_graph(station_name):
    if station_name not in station_names:
        return "Error: Please specify a valid station"

    if "/" in station_name:
        data = pd.read_csv(open(f'stations/Princes Street.csv', 'r'), usecols=[0, 2, 3])
    else:
        data = pd.read_csv(open(f'stations/{station_name}.csv', 'r'), usecols=[0, 2, 3])

    d = datetime.datetime.now()

    if d.isoweekday() in range(1, 6):
        filtered_data = data[data['type_of_day'] == 0].tail(17000)
    else:
        filtered_data = data[data['type_of_day'] == 10].tail(17000)

    x, y = (filtered_data['time_of_day'], filtered_data['available_bikes'])

    coefficients = np.polyfit(x, y, 50)
    poly_func = np.poly1d(coefficients)

    new_x = np.linspace(18000, 86400)
    new_y = poly_func(new_x)

    result = {"graph": []}

    for x_value, y_value in zip(new_x, new_y):
        result['graph'].append((x_value, y_value))

    return jsonify(result)
