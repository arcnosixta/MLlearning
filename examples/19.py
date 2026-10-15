from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
X, y = make_moons(n_samples=300, noise=0.18, random_state=42)
Xtr, Xte, ytr, yte = train_test_split(X, y, stratify=y, random_state=42)
model = make_pipeline(StandardScaler(), MLPClassifier(
    hidden_layer_sizes=(16, 8), solver="lbfgs", max_iter=2000, random_state=42))
model.fit(Xtr, ytr)
print("Accuracy:", model.score(Xte, yte))
print("Layer shapes:", [w.shape for w in model.named_steps["mlpclassifier"].coefs_])
