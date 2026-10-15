from sklearn.datasets import make_blobs
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
X, _ = make_blobs(n_samples=180, centers=3, cluster_std=0.7, random_state=42)
scaled = StandardScaler().fit_transform(X)
model = KMeans(n_clusters=3, n_init=10, random_state=42).fit(scaled)
print("Centers:\n", model.cluster_centers_)
print("Silhouette:", silhouette_score(scaled, model.labels_))
