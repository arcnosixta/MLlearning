import numpy as np
x = np.array([-2., -1., 0., 1., 2.])
y = 3 * x + 2
w, b, learning_rate = 0., 0., 0.1
for step in range(100):
    error = w * x + b - y
    dw = 2 * np.mean(x * error)
    db = 2 * np.mean(error)
    w -= learning_rate * dw
    b -= learning_rate * db
print("w, b:", w, b)
print("MSE:", np.mean((w*x+b-y)**2))
