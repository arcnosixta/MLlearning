from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
X, y = load_iris(return_X_y=True)
Xtr, Xte = train_test_split(X, random_state=42)
reducer = make_pipeline(StandardScaler(), PCA(n_components=2))
reducer.fit(Xtr)
print("Reduced test:", reducer.transform(Xte).shape)
print("Variance:", reducer.named_steps["pca"].explained_variance_ratio_)
