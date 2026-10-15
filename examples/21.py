from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
X, y = load_iris(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, stratify=y, random_state=42)
pipe = make_pipeline(StandardScaler(), KNeighborsClassifier())
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
search = GridSearchCV(pipe, {"kneighborsclassifier__n_neighbors": [3, 5, 9]}, cv=cv, scoring="accuracy")
search.fit(Xtr, ytr)
print("Best:", search.best_params_, "CV:", search.best_score_)
print("Final test:", search.score(Xte, yte))
