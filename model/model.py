from pygam.datasets import wage
from pygam import LinearGAM, s, f, te, GammaGAM
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

def display_bike_availability_over_time(my_data):
    plt.figure()

    print(X[0])

    plt.plot(my_data['epoch'], my_data['change_in_bike_availability'])

    plt.title("Change in availability over time")

    plt.show()
    
def display_breakdown():
    for i, term in enumerate(gam.terms):
        if term.isintercept:
            continue

        XX = gam.generate_X_grid(term=i)
        pdep, confi = gam.partial_dependence(term=i, X=XX, width=0.95)
        print("Types: " + str(type(pdep)) + " - " + str(type(confi)))
        plt.figure()
        print("huh: " + str(type(XX)))
        print("hah: " + str(term.feature))
        plt.plot(XX[:, term.feature], pdep)
        plt.plot(XX[:, term.feature], confi, c='r', ls='--')
        print("Term: " + repr(term) + " - " + attributes[i])
        if i == 0 or i == 1:
            plt.title("Time of day and type of day")
        else:
            plt.title(attributes[i+1])
    plt.show()

def test_model(gam):
    # time_of_day,type_of_day,day_of_year,temperature,rain,relative_humidity,vapour_pressure,wind_speed,sunshine,visibility
    # 21: 50625,1,1951425,22,2017-01-22T14:03:45,5.1,0,64,5.6,3,0.7,20000
    tester = [50625,1,22,5.1,0,64,5.6,3]

    y_pred = gam.predict([tester])

    print(y_pred)

    # 0,75229,0,6036829,69,
    # tester = [75229,0,69,10.2,0,81,10.0,6,0.0,30000]

    # y_pred = gam.predict([tester])

    # print(y_pred)

    # (38 previous)
    # 27,29121,0,22838721,264,11.9,0,69,9.6,4,0.0,60000,-11,1474355121,38,40

    tester = [29121,0,264,11.9,0,69,9.6,4]

    y_pred = gam.predict([tester])

    print(y_pred)

my_data = pd.read_csv("result_charlemount.csv")

attributes = ['time_of_day', 'type_of_day', 'day_of_year', 'temperature', 'rain', 'relative_humidity', 'vapour_pressure', 'wind_speed']

X = my_data[attributes].values

y = my_data['available_bike_stands'].values

gam = GammaGAM(te(0, 1) + s(2) + s(3) + s(4) + s(5) + s(6) + s(7), n_splines=[35, 20, 20, 10, 20, 10, 10, 25], dtype=['numerical', 'categorical', 'numerical', 'numerical', 'numerical', 'numerical', 'numerical', 'numerical'])

gam.gridsearch(X, y)

gam.summary()

display_breakdown()

test_model(gam)