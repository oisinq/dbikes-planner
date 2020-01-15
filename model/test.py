import pandas as pd
from pygam import LinearGAM
from sklearn.datasets import load_boston

boston = load_boston()

df = pd.DataFrame(boston.data, columns=boston.feature_names)
target_df = pd.Series(boston.target)
print(df.head())
print(target_df.head())

X = df.values
y = target_df
gam = LinearGAM(n_splines=10).gridsearch(X, y)
gam.summary()

