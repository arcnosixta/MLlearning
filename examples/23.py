import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error
rng = np.random.default_rng(42)
series = np.arange(100)*0.2 + np.sin(np.arange(100)/5) + rng.normal(0, 0.1, 100)
X, y = series[:-1, None], series[1:]
for train, test in TimeSeriesSplit(n_splits=3).split(X):
    model = Ridge().fit(X[train], y[train])
    print("Last train / first test:", train[-1], test[0])
    print("Model MAE:", mean_absolute_error(y[test], model.predict(X[test])),
          "Naive MAE:", mean_absolute_error(y[test], X[test, 0]))
