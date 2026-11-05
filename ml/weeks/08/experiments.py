"""Week 08: SVM, kNN and logistic regression on the same two rings."""
import json

import numpy as np
from sklearn.datasets import make_circles
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

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


def boundary_samples(model):
    axis = np.linspace(-1.4, 1.4, 45)
    gx, gy = np.meshgrid(axis, axis)
    grid = np.column_stack((gx.ravel(), gy.ravel()))
    predictions = model.predict(grid).reshape(gx.shape)
    boundary = np.zeros(predictions.shape, dtype=bool)
    boundary[1:, :] |= predictions[1:, :] != predictions[:-1, :]
    boundary[:, 1:] |= predictions[:, 1:] != predictions[:, :-1]
    return gx[boundary], gy[boundary]


def group_plots(x, y):
    return [
        series(f"Класс {class_id}", f"{class_id}-класс", "scatter", *x[y == class_id].T)
        for class_id in (0, 1)
    ]


def build_lab():
    x, y = make_circles(n_samples=260, factor=0.48, noise=0.13, random_state=81)
    train_x, test_x, train_y, test_y = train_test_split(
        x, y, stratify=y, test_size=0.3, random_state=3305,
    )
    svm_cases = []
    for ru, kk, kernel, gamma in (
        ("Линейное ядро", "Сызықтық ядро", "linear", "scale"),
        ("RBF · gamma=0.08", "RBF · gamma=0.08", "rbf", 0.08),
        ("RBF · gamma=3", "RBF · gamma=3", "rbf", 3),
    ):
        svm = make_pipeline(StandardScaler(), SVC(C=1, kernel=kernel, gamma=gamma))
        svm.fit(train_x, train_y)
        count = svm[-1].n_support_.sum()
        accuracy = svm.score(test_x, test_y)
        svm_cases.append(case(
            ru, kk,
            f"Опорных векторов={count} · test accuracy={accuracy:.3f}",
            f"Тірек векторлары={count} · test accuracy={accuracy:.3f}",
            *group_plots(test_x, test_y),
            series("Граница на сетке", "Тордағы шекара", "scatter", *boundary_samples(svm)),
        ))

    scaler = StandardScaler().fit(train_x)
    scaled = scaler.transform(train_x)
    grid = np.array([(a, b) for a in np.linspace(-0.9, 0.9, 25) for b in np.linspace(-0.9, 0.9, 25)])
    # Pick a near-boundary query whose local and broader votes differ.
    short = KNeighborsClassifier(1).fit(scaled, train_y).predict(scaler.transform(grid))
    long = KNeighborsClassifier(25).fit(scaled, train_y).predict(scaler.transform(grid))
    query = grid[np.flatnonzero(short != long)[0]]
    query_scaled = scaler.transform([query])
    neighbor_cases = []
    for count in (1, 7, 25):
        model = KNeighborsClassifier(count).fit(scaled, train_y)
        ids = model.kneighbors(query_scaled, return_distance=False)[0]
        votes = np.bincount(train_y[ids], minlength=2)
        note = f"0: {votes[0]} · 1: {votes[1]} · P(1)={votes[1] / count:.3f}"
        neighbor_cases.append(case(
            f"k={count}", f"k={count}", note, note,
            *group_plots(train_x, train_y),
            series("Голосующие", "Дауыс берушілер", "scatter", *train_x[ids].T),
            series("Запрос", "Сұрау нүктесі", "scatter", [query[0]], [query[1]]),
        ))

    compare_cases = []
    names = ["Train acc.", "Test acc.", "Test F1"]
    for ru, kk, estimator in (
        ("Логистическая регрессия", "Логистикалық регрессия", LogisticRegression(max_iter=1000)),
        ("kNN · k=7", "kNN · k=7", KNeighborsClassifier(7)),
        ("SVM · RBF", "SVM · RBF", SVC(kernel="rbf", C=1, gamma=3)),
    ):
        model = make_pipeline(StandardScaler(), estimator).fit(train_x, train_y)
        guess = model.predict(test_x)
        values = [
            model.score(train_x, train_y), accuracy_score(test_y, guess), f1_score(test_y, guess),
        ]
        note = " · ".join(f"{name}={score:.3f}" for name, score in zip(names, values, strict=True))
        compare_cases.append(case(
            ru, kk, note, note,
            series("Метрики", "Метрикалар", "bar", range(len(names)), values),
            ticks=[(name, name) for name in names],
        ))
    return {"topics": [svm_cases, neighbor_cases, compare_cases]}


if __name__ == "__main__":
    print(json.dumps(build_lab(), ensure_ascii=False, allow_nan=False))
