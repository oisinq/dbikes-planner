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

X = my_data[['time_of_day', 'type_of_day', 'day_of_year']].values
y = my_data['available_bike_stands'].values

gam = LinearGAM(te(0, 2) + f(1), dtype=['numerical', 'categorical', 'numerical'])
gam.gridsearch(X, y)

gam.summary()

display_breakdown()

# 11,32693,1,27421493,317,2016-11-12T09:04:53
#y_pred = gam.predict([[32693,1,317]])
#predi = gam.prediction_intervals([[32693,1,317]], width=0.95)

# plt.plot(predi, c='r', ls='--')
# plt.plot(y_pred, c='k')
# plt.show()