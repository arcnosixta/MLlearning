from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
X, y = make_classification(n_samples=300, n_features=5, random_state=42)
Xtr, Xte, ytr, yte = train_test_split(X, y, stratify=y, random_state=42)
model = make_pipeline(StandardScaler(), LogisticRegression())
model.fit(Xtr, ytr)
p = model.predict_proba(Xte)[:, 1]
print("P(class 1):", p[:5])
print("Threshold 0.5:", (p[:5] >= 0.5).astype(int))
