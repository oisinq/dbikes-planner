from pygam.datasets import wage
from pygam import LinearGAM, s, f
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

my_data = pd.read_csv("result_charlemount.csv")

X = my_data[['time_of_day', 'type_of_day', 'time_of_year']][-3000:].values
y = my_data['available_bike_stands'][-3000:].values

gam = LinearGAM(n_splines=200).fit(X, y)

gam.summary()

for i, term in enumerate(gam.terms):
    print("woo")
    if term.isintercept:
        continue

    XX = gam.generate_X_grid(term=i)
    pdep, confi = gam.partial_dependence(term=i, X=XX, width=0.95)

    plt.figure()
    plt.plot(XX[:, term.feature], pdep)
    plt.plot(XX[:, term.feature], confi, c='r', ls='--')
    plt.title(repr(term))
    plt.show()