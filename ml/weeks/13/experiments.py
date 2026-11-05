"""Measure image-filter responses and transfer a small NumPy convolutional model."""

import json

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from sklearn.linear_model import LogisticRegression
from threadpoolctl import threadpool_limits


FILTERS = np.array([
    [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]],
    [[-1, -2, -1], [0, 0, 0], [1, 2, 1]],
    [[0, 1, 2], [-1, 0, 1], [-2, -1, 0]],
], dtype=float).reshape(3, 9).T / 4


def localized(ru, kk):
    return {"ru": ru, "kk": kk}


def series(ru, kk, kind, x, y):
    return {"label": localized(ru, kk), "kind": kind,
            "points": [[int(a), round(float(b), 4)] for a, b in zip(x, y)]}


def images(classes, count, seed, shift=0, noise=0.10):
    """Draw equally frequent synthetic line classes on 12 by 12 images."""
    rng = np.random.default_rng(seed)
    labels = np.tile(np.arange(classes), count)
    rng.shuffle(labels)
    pixels = rng.normal(0, noise, (len(labels), 12, 12))
    for image, label in zip(pixels, labels):
        row, col = 5 + rng.integers(-shift, shift + 1, size=2)
        segment = np.arange(-2, 3)
        if label == 0:
            image[row + segment, col] += 1
        elif label == 1:
            image[row, col + segment] += 1
        else:
            image[row + segment, col + segment] += 1
    return pixels.clip(0, 1), labels


def patches(images):
    windows = sliding_window_view(images, (3, 3), axis=(1, 2))
    return windows.reshape(len(images), 10, 10, 9)


def response_cases():
    names = [("Вертикаль", "Тік"), ("Горизонталь", "Көлденең"), ("Диагональ", "Диагональ")]
    rows = []
    clean, labels = images(3, 1, 3305, noise=0)
    for category, (ru, kk) in enumerate(names):
        responses = np.abs(patches(clean[labels == category])[0] @ FILTERS).max(axis=0)
        rows.append({
            "label": localized(ru, kk),
            "note": localized(f"Наибольший модуль отклика: {responses.max():.2f}. "
                              "По Y выбран максимум среди строк окна.",
                              f"Ең үлкен жауап модулі: {responses.max():.2f}. "
                              "Y үшін терезе жолдары бойынша максимум алынды."),
            "series": [series(a, b, "line", range(10), responses[:, i])
                       for i, (a, b) in enumerate(names)],
        })
    return rows


def pooled_features(pixels):
    return np.abs(patches(pixels) @ FILTERS).mean(axis=(1, 2))


def pooling_cases():
    pixels, labels = images(2, 40, 7)
    raw = LogisticRegression().fit(pixels.reshape(len(labels), -1), labels)
    pooled = LogisticRegression().fit(pooled_features(pixels), labels)
    cases = []
    for shift, ru, kk in ((0, "Без сдвига", "Ығысусыз"), (2, "До двух пикселей", "Екі пиксельге дейін"),
                          (3, "До трёх пикселей", "Үш пиксельге дейін")):
        evaluation, expected = images(2, 60, 11, shift=shift, noise=0.13)
        raw_score = raw.score(evaluation.reshape(len(expected), -1), expected)
        pooled_score = pooled.score(pooled_features(evaluation), expected)
        cases.append({
            "label": localized(ru, kk),
            "note": localized(f"На {len(expected)} изображениях: пиксели {raw_score:.3f}, "
                              f"пулинг откликов {pooled_score:.3f}.",
                              f"{len(expected)} кескінде: пиксельдер {raw_score:.3f}, "
                              f"жауап пулингі {pooled_score:.3f}."),
            "series": [series("Accuracy", "Accuracy", "bar", (1, 2), (raw_score, pooled_score))],
            "xTicks": [{"value": 1, "label": localized("Пиксели", "Пиксельдер")},
                       {"value": 2, "label": localized("Пулинг", "Пулинг")}],
        })
    return cases


def transfer_data():
    source = images(3, 24, 3305, shift=2)
    train = images(2, 6, 42, shift=3, noise=0.22)
    validation = images(2, 24, 86, shift=3, noise=0.22)
    return source, train, validation


class TinyCNN:
    def __init__(self, classes, seed, backbone=None):
        rng = np.random.default_rng(seed)
        self.kernel = rng.normal(0, 0.32, (9, 8))
        self.kernel_bias = np.zeros(8)
        self.head = rng.normal(0, 0.4, (8, classes))
        self.head_bias = np.zeros(classes)
        if backbone is not None:
            self.kernel = backbone.kernel.copy()
            self.kernel_bias = backbone.kernel_bias.copy()

    def forward(self, windows):
        raw = windows @ self.kernel + self.kernel_bias
        features = np.maximum(0, raw).mean(axis=(1, 2))
        return raw, features, features @ self.head + self.head_bias

    def fit(self, training, evaluation, epochs, rate, freeze=False):
        train_x, train_y = training
        valid_x, valid_y = evaluation
        train_windows = patches(train_x)
        valid_windows = patches(valid_x)
        targets = np.eye(len(self.head_bias))[train_y]
        scores = []
        for step in range(epochs + 1):
            if step % 5 == 0:
                validation_logits = self.forward(valid_windows)[2]
                accuracy = (validation_logits.argmax(axis=1) == valid_y).mean()
                loss = np.logaddexp.reduce(validation_logits, axis=1) - validation_logits[
                    np.arange(len(valid_y)), valid_y
                ]
                scores.append((step, accuracy, loss.mean()))
            if step == epochs:
                break
            raw, features, logits = self.forward(train_windows)
            probabilities = np.exp(logits - logits.max(axis=1, keepdims=True))
            probabilities /= probabilities.sum(axis=1, keepdims=True)
            delta = (probabilities - targets) / len(targets)
            if not freeze:
                mean_gradient = (delta @ self.head.T) / (raw.shape[1] * raw.shape[2])
                gradient = mean_gradient[:, None, None, :] * (raw > 0)
                self.kernel -= rate * (train_windows.reshape(-1, 9).T @ gradient.reshape(-1, 8))
                self.kernel_bias -= rate * gradient.sum(axis=(0, 1, 2))
            self.head -= rate * features.T @ delta
            self.head_bias -= rate * delta.sum(axis=0)
        return np.array(scores)


def transfer_cases():
    source, train, validation = transfer_data()
    pretrained = TinyCNN(3, seed=10)
    pretrained.fit(source, source, epochs=160, rate=1.2)
    cases = []
    for ru, kk, transfer, freeze in (
        ("С нуля", "Нөлден", False, False),
        ("Заморозить фильтры", "Сүзгілерді бекіту", True, True),
        ("Донастроить фильтры", "Сүзгілерді бейімдеу", True, False),
    ):
        model = TinyCNN(2, seed=21, backbone=pretrained if transfer else None)
        steps, scores, losses = model.fit(train, validation, epochs=95, rate=0.9, freeze=freeze).T
        cases.append({
            "label": localized(ru, kk),
            "note": localized(f"Обучение на {len(train[1])} изображениях. Accuracy на "
                              f"{len(validation[1])} валидационных: {scores[-1]:.3f}. "
                              f"Кросс-энтропия: {losses[-1]:.3f}.",
                              f"Оқытуда {len(train[1])} кескін. {len(validation[1])} "
                              f"валидация кескініндегі accuracy: {scores[-1]:.3f}. "
                              f"Кросс-энтропия: {losses[-1]:.3f}."),
            "series": [series("Accuracy", "Accuracy", "line", steps, scores),
                       series("Кросс-энтропия", "Кросс-энтропия", "line", steps, losses)],
        })
    return cases


def main():
    with threadpool_limits(limits=1):
        result = [response_cases(), pooling_cases(), transfer_cases()]
    print(json.dumps({"topics": result}, ensure_ascii=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
