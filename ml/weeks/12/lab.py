"""Train a tiny neural network with NumPy and compare loss curves."""

import json

import numpy as np
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split


def localized(ru, kk):
    return {"ru": ru, "kk": kk}


def series(ru, kk, kind, x, y):
    return {"label": localized(ru, kk), "kind": kind,
            "points": [[round(float(a), 4), round(float(b), 4)] for a, b in zip(x, y)]}


def sigmoid(x):
    return 1 / (1 + np.exp(-np.clip(x, -50, 50)))


def activation_cases():
    x = np.linspace(-4, 4, 41)
    cases = []
    for title, operation, ru, kk in (
        ("Sigmoid", sigmoid, "Сжимает выход в (0, 1).", "Шығысты (0, 1) аралығына келтіреді."),
        ("ReLU", lambda values: np.maximum(0, values), "Гасит отрицательные значения.",
         "Теріс мәндерді нөлге түсіреді."),
        ("Tanh", np.tanh, "Нечётная функция со значениями в (−1, 1).",
         "Мәндері (−1, 1) аралығындағы тақ функция."),
    ):
        cases.append({"label": localized(title, title), "note": localized(ru, kk),
                      "series": [series(title, title, "line", x, operation(x))]})
    return cases


def data():
    x, y = make_moons(n_samples=260, noise=0.20, random_state=3305)
    return train_test_split(x, y, test_size=0.25, stratify=y, random_state=42)


def binary_loss(logits, truth):
    return np.mean(np.logaddexp(0, logits) - truth * logits)


def train(train_x, validation_x, train_y, validation_y, width, learning_rate, epochs=360):
    rng = np.random.default_rng(3305)
    input_weights = rng.normal(0, 0.5, (train_x.shape[1], width))
    hidden_bias = np.zeros(width)
    output_weights = rng.normal(0, 0.5, width)
    output_bias = 0.0

    def forward(features):
        hidden = np.tanh(features @ input_weights + hidden_bias)
        return hidden, hidden @ output_weights + output_bias

    snapshots = []
    for epoch in range(epochs + 1):
        hidden, logits = forward(train_x)
        if epoch % 12 == 0:
            _, validation_logits = forward(validation_x)
            snapshots.append((epoch, binary_loss(logits, train_y),
                              binary_loss(validation_logits, validation_y)))
        if epoch == epochs:
            break
        residual = (sigmoid(logits) - train_y) / len(train_y)
        hidden_gradient = residual[:, None] * output_weights * (1 - hidden ** 2)
        output_weights -= learning_rate * (hidden.T @ residual)
        output_bias -= learning_rate * residual.sum()
        input_weights -= learning_rate * (train_x.T @ hidden_gradient)
        hidden_bias -= learning_rate * hidden_gradient.sum(axis=0)
    return np.array(snapshots), (forward(validation_x)[1] >= 0).astype(int)


def training_cases(partitions):
    cases = []
    for rate in (0.02, 0.2, 1.0):
        history, _ = train(*partitions, width=8, learning_rate=rate)
        epochs, train_loss, validation_loss = history.T
        cases.append({
            "label": localized(f"Шаг {rate:g}", f"Қадам {rate:g}"),
            "note": localized(f"Финальная потеря: обучение {train_loss[-1]:.3f}, "
                              f"валидация {validation_loss[-1]:.3f}.",
                              f"Соңғы шығын: оқыту {train_loss[-1]:.3f}, "
                              f"валидация {validation_loss[-1]:.3f}."),
            "series": [series("Обучение", "Оқыту", "line", epochs, train_loss),
                       series("Валидация", "Валидация", "line", epochs, validation_loss)],
        })
    return cases


def width_cases(partitions):
    _, validation_x, _, validation_y = partitions
    cases = []
    for width in (1, 8, 16):
        _, predictions = train(*partitions, width=width, learning_rate=0.6)
        errors = predictions != validation_y
        rows = []
        for category in (0, 1):
            right = validation_x[(validation_y == category) & ~errors]
            if len(right):
                rows.append(series(f"Верно: класс {category}", f"Дұрыс: {category}-класс", "scatter",
                                   right[:, 0], right[:, 1]))
        if errors.any():
            wrong = validation_x[errors]
            rows.append(series("Ошибка", "Қате", "scatter", wrong[:, 0], wrong[:, 1]))
        cases.append({
            "label": localized(f"Ширина {width}", f"Ені {width}"),
            "note": localized(f"Ошибок: {errors.sum()} из {len(errors)}, accuracy={(~errors).mean():.3f}.",
                              f"Қате: {len(errors)} нүктенің {errors.sum()}-і, accuracy={(~errors).mean():.3f}."),
            "series": rows,
        })
    return cases


def main():
    partitions = data()
    results = [activation_cases(), training_cases(partitions), width_cases(partitions)]
    print(json.dumps({"topics": results}, ensure_ascii=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
