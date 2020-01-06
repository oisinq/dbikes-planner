from pygam.datasets import wage
from pygam import LinearGAM, s, f
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

my_data = pd.read_csv("charlemount.csv")

print(type(my_data))

my_data['available_bike_stands'][-1000:].plot(figsize=(12,8))
plt.show()