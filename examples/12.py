from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.dummy import DummyRegressor
X_train = [[0], [1], [2], [3]]
y_train = [2, 4, 6, 8]
X_test, y_test = [[4], [5], [6]], [10, 12, 14]
pred = [9, 13, 12]
baseline = DummyRegressor(strategy="median").fit(X_train, y_train)
print("MAE:", mean_absolute_error(y_test, pred))
print("RMSE:", mean_squared_error(y_test, pred)**0.5)
print("R2:", r2_score(y_test, pred))
print("Baseline MAE:", mean_absolute_error(y_test, baseline.predict(X_test)))
