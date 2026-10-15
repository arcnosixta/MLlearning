import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
X_train = np.array([[30., 10000.], [60., 30000.], [90., 50000.]])
X_test = np.array([[120., 60000.]])
scaler = StandardScaler().fit(X_train)
print("Train:\n", scaler.transform(X_train))
print("Test:\n", scaler.transform(X_test))
print("Means:", scaler.mean_)
print("MinMax test:", MinMaxScaler().fit(X_train).transform(X_test))
