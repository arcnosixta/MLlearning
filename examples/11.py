import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
rng = np.random.default_rng(42)
X = rng.uniform(-2, 2, (70, 1))
y = X[:, 0]**2 + rng.normal(0, 0.7, 70)
Xtr, Xte, ytr, yte = train_test_split(X, y, random_state=42)
for degree in [1, 2, 15]:
    model = make_pipeline(PolynomialFeatures(degree, include_bias=False), StandardScaler(), Ridge(alpha=1))
    model.fit(Xtr, ytr)
    print(degree, "train:", mean_squared_error(ytr, model.predict(Xtr)),
          "test:", mean_squared_error(yte, model.predict(Xte)))
