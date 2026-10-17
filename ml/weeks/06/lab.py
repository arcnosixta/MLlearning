"""Week 06: sigmoid, a binary decision threshold, and multiclass probabilities."""
import json

import numpy as np
from sklearn.datasets import load_iris, make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

def lang(ru, kk):
    return {"ru": ru, "kk": kk}


def series(ru, kk, kind, x, y):
    return {
        "label": lang(ru, kk),
        "kind": kind,
        "points": [[round(float(a), 4), round(float(b), 4)] for a, b in zip(x, y, strict=True)],
    }


def case(ru, kk, note_ru, note_kk, *plots, ticks=None):
    result = {"label": lang(ru, kk), "note": lang(note_ru, note_kk), "series": list(plots)}
    if ticks is not None:
        result["xTicks"] = [{"value": i, "label": lang(*name)} for i, name in enumerate(ticks)]
    return result


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


def fit_and_predict(features, labels):
    train_x, test_x, train_y, test_y = train_test_split(
        features, labels, test_size=0.3, stratify=labels, random_state=3305,
    )
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
    model.fit(train_x, train_y)
    return model.predict_proba(test_x), test_y, model.classes_


def build_lab():
    x = np.linspace(-5, 5, 61)
    sigmoid_cases = []
    for slope in (0.5, 1, 2):
        note = f"z={slope:g}x · p(1)={sigmoid(slope):.3f}"
        sigmoid_cases.append(case(
            f"Наклон {slope:g}", f"Көлбеулік {slope:g}", note, note,
            series("Сигмоида", "Сигмоида", "line", x, sigmoid(slope * x)),
        ))

    x, y = make_classification(
        n_samples=200, n_features=3, n_informative=3, n_redundant=0,
        class_sep=0.85, flip_y=0.08, random_state=21,
    )
    probabilities, actual, classes = fit_and_predict(x, y)
    positive = probabilities[:, list(classes).index(1)]
    order = np.argsort(positive)
    x = np.arange(1, len(actual) + 1)
    actual = actual[order]
    positive = positive[order]
    binary_cases = []
    for threshold in (0.25, 0.5, 0.75):
        prediction = positive >= threshold
        _, fp, fn, tp = confusion_matrix(actual, prediction, labels=[0, 1]).ravel()
        binary_cases.append(case(
            f"Порог {threshold:.2f}", f"Шек {threshold:.2f}",
            f"Сигналы={tp + fp} · FP={fp} · FN={fn}",
            f"Ескертулер={tp + fp} · FP={fp} · FN={fn}",
            series("Фактический класс 0", "Нақты 0-класс", "scatter", x[actual == 0], positive[actual == 0]),
            series("Фактический класс 1", "Нақты 1-класс", "scatter", x[actual == 1], positive[actual == 1]),
            series("Порог", "Шек", "line", [1, len(actual)], [threshold, threshold]),
        ))

    iris = load_iris()
    probabilities, actual, classes = fit_and_predict(iris.data, iris.target)
    names = list(iris.target_names[classes])
    gap = np.diff(np.sort(probabilities, axis=1)[:, -2:], axis=1).ravel()
    flower_cases = []
    for class_id in classes:
        candidates = np.flatnonzero(actual == class_id)
        i = int(candidates[np.argmin(gap[candidates])])
        prediction = names[int(np.argmax(probabilities[i]))]
        row = " · ".join(f"{name}={p:.3f}" for name, p in zip(names, probabilities[i], strict=True))
        flower_cases.append(case(
            f"Цветок {i + 1}", f"{i + 1}-гүл",
            f"{row}. Факт: {iris.target_names[actual[i]]} · прогноз: {prediction} · разрыв: {gap[i]:.3f}.",
            f"{row}. Нақты: {iris.target_names[actual[i]]} · болжам: {prediction} · айырма: {gap[i]:.3f}.",
            series("Оценки модели", "Модель бағалары", "bar", range(len(names)), probabilities[i]),
            ticks=[(name, name) for name in names],
        ))
    return {"topics": [sigmoid_cases, binary_cases, flower_cases]}


if __name__ == "__main__":
    print(json.dumps(build_lab(), ensure_ascii=False, allow_nan=False))
