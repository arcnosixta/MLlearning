from pathlib import Path
import joblib
import numpy as np
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split, KFold, GridSearchCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error
X, y = load_diabetes(return_X_y=True, scaled=False)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
baseline = DummyRegressor(strategy="median").fit(Xtr, ytr)
search = GridSearchCV(make_pipeline(StandardScaler(), Ridge()),
    {"ridge__alpha": [0.1, 1, 10, 100]},
    cv=KFold(5, shuffle=True, random_state=42), scoring="neg_mean_absolute_error")
search.fit(Xtr, ytr)
model = search.best_estimator_
print("Parameters:", search.best_params_)
print("Baseline MAE:", mean_absolute_error(yte, baseline.predict(Xte)))
print("Model MAE:", mean_absolute_error(yte, model.predict(Xte)))
path = Path("model.joblib")
joblib.dump(model, path)
restored = joblib.load(path)
assert np.allclose(restored.predict(Xte), model.predict(Xte))
print("Saved and verified:", path.resolve())
