from sklearn.preprocessing import OrdinalEncoder, MinMaxScaler
import pandas as pd


def timestamp_fix():
    data = pd.read_csv("/Users/oisin/Coding/ucd/Fourth/fyp/fyp/webapp/stations/Charlemont Street.csv")

    X = data.iloc[:, [2, 3, 4, 6, 7, 9, 10, 12, 15]]
    y = data.iloc[:, [14]]

    print("aight")
    encoder = OrdinalEncoder(categories=[['empty', 'very low', 'low', 'moderate', 'high']])

    minmax = MinMaxScaler()

    X_scaled = pd.DataFrame(minmax.fit_transform(X), columns=X.columns)
    y_scaled = pd.DataFrame(encoder.fit_transform(y.values.reshape(-1, 1)), columns=y.columns)

    print(X_scaled)
    print(y_scaled)


if __name__ == "__main__":
    timestamp_fix()
