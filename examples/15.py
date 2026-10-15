from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text
data = load_iris()
Xtr, Xte, ytr, yte = train_test_split(data.data, data.target, stratify=data.target, random_state=42)
model = DecisionTreeClassifier(max_depth=3, random_state=42).fit(Xtr, ytr)
print(export_text(model, feature_names=list(data.feature_names)))
print("Accuracy:", model.score(Xte, yte))
