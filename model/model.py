from pygam.datasets import wage
from pygam import LinearGAM, s, f
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

my_data = pd.read_csv("charlemount.csv")

# print(type(my_data))

# my_data['available_bike_stands'][-1000:].plot(figsize=(12,8))
# plt.show()

X = my_data['last_update'][-3000:].values
y_int = my_data['available_bike_stands'][-3000:].values

y = [datetime.fromtimestamp(item) for item in y_int]

gam = LinearGAM(n_splines=200).fit(X, y)

print(gam.summary())

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