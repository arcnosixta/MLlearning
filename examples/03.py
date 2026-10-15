import numpy as np
X = np.array([[30., 1.], [60., 2.], [90., 3.]])
means = X.mean(axis=0)
centered = X - means
print("shape:", X.shape)
print("means:", means)
print("centered:\n", centered)
print("predictions:", X @ np.array([2., 10.]))
