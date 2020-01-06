from pygam.datasets import wage
from pygam import LinearGAM, s, f
import numpy as np
import matplotlib.pyplot as plt

X, y = wage()

gam = LinearGAM(s(0, n_splines=5) + s(1) + f(2)).fit(X, y)

gam.summary()

lam = np.logspace(-3, 5, 5)
lams = [lam] * 3

gam.gridsearch(X, y, lam=lams)
gam.summary()

lams = np.random.rand(100, 3) # random points on [0, 1], with shape (100, 3)
lams = lams * 8 - 3 # shift values to -3, 3
lams = np.exp(lams) # transforms values to 1e-3, 1e3

random_gam =  LinearGAM(s(0) + s(1) + f(2)).gridsearch(X, y, lam=lams)
random_gam.summary()

print(gam.statistics_['GCV'] < random_gam.statistics_['GCV'])

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