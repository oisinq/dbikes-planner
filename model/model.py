from pygam.datasets import wage
from pygam import LinearGAM, s, f, te
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

def display_breakdown():
    for i, term in enumerate(gam.terms):
        if term.isintercept:
            continue

        XX = gam.generate_X_grid(term=i)
        pdep, confi = gam.partial_dependence(term=i, X=XX, width=0.95)

        plt.figure()
        plt.plot(XX[:, term.feature], pdep)
        plt.plot(XX[:, term.feature], confi, c='r', ls='--')
        plt.title(repr(term))
    plt.show()


my_data = pd.read_csv("result_charlemount.csv")

X = my_data[['time_of_day', 'type_of_day', 'day_of_year', 'temperature', 'rain', 'relative_humidity', 'vapour_pressure', 'wind_speed', 'sunshine', 'visibility']].values
y = my_data['available_bike_stands'].values

gam = LinearGAM(te(0, 1) + s(2) + s(3) + s(4) + s(5) + s(6) + s(7) + s(8) + s(9), dtype=['numerical', 'categorical', 'numerical', 'numerical', 'numerical', 'numerical', 'numerical', 'numerical', 'numerical', 'numerical'])
gam.gridsearch(X, y)

gam.summary()

#display_breakdown()

# time_of_day,type_of_day,day_of_year,temperature,rain,relative_humidity,vapour_pressure,wind_speed,sunshine,visibility
# 21: 50625,1,1951425,22,2017-01-22T14:03:45,5.1,0,64,5.6,3,0.7,20000
tester = [50625,1,22,5.1,0,64,5.6,3,0.7,20000]

y_pred = gam.predict([tester])

print(y_pred)

y_pred = badGam.predict([tester])

print(y_pred)

# 0,75229,0,6036829,69,
tester = [75229,0,69,10.2,0,81,10.0,6,0.0,30000]

y_pred = gam.predict([tester])

print(y_pred)

y_pred = badGam.predict([tester])

print(y_pred)

# plt.plot(predi, c='r', ls='--')
# plt.plot(y_pred, c='k')
# plt.show()