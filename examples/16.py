from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
X, y = make_classification(n_samples=500, n_features=10, random_state=42)
Xtr, Xte, ytr, yte = train_test_split(X, y, stratify=y, random_state=42)
models = [RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42),
          HistGradientBoostingClassifier(max_iter=80, max_leaf_nodes=7, random_state=42)]
for model in models:
    model.fit(Xtr, ytr)
    print(type(model).__name__, model.score(Xte, yte))
