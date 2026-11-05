"""Choose SVM hyperparameters using training folds, then test and reload."""

import json
import tempfile
from pathlib import Path

import joblib
import numpy as np
from sklearn.datasets import load_wine
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import (
    GridSearchCV,
    RandomizedSearchCV,
    StratifiedKFold,
    cross_val_score,
    train_test_split,
)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


def localized(ru, kk):
    return {"ru": ru, "kk": kk}


def series(ru, kk, kind, x, y):
    return {"label": localized(ru, kk), "kind": kind,
            "points": [[int(a), round(float(b), 4)] for a, b in zip(x, y)]}


def cv_cases(pipeline, train_x, train_y):
    cases = []
    for folds in (3, 5, 8):
        cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=3305)
        scores = cross_val_score(pipeline, train_x, train_y, cv=cv, scoring="f1_macro")
        indices = range(1, folds + 1)
        cases.append({
            "label": localized(f"{folds} фолда" if folds != 8 else "8 фолдов", f"{folds} фолд"),
            "note": localized(f"Средний macro-F1: {scores.mean():.3f}. Разброс σ: {scores.std():.3f}.",
                              f"Орташа macro-F1: {scores.mean():.3f}. Шашырау σ: {scores.std():.3f}."),
            "series": [series("Фолд", "Фолд", "bar", indices, scores),
                       series("Среднее", "Орташа", "line", indices, [scores.mean()] * folds)],
        })
    return cases


def search_cases(pipeline, train_x, train_y, cv):
    space = {"svc__C": [0.01, 0.1, 1, 10], "svc__gamma": [0.001, 0.01, 0.1, 1]}
    options = {"scoring": "f1_macro", "cv": cv, "return_train_score": True}
    searches = [
        ("Сетка", "Тор", GridSearchCV(pipeline, space, **options)),
        ("Случайно 4", "Кездейсоқ 4",
         RandomizedSearchCV(pipeline, space, n_iter=4, random_state=7, **options)),
        ("Случайно 8", "Кездейсоқ 8",
         RandomizedSearchCV(pipeline, space, n_iter=8, random_state=7, **options)),
    ]
    cases = []
    for ru, kk, search in searches:
        search.fit(train_x, train_y)
        report = search.cv_results_
        order = np.argsort(-report["mean_test_score"], kind="stable")
        indices = range(1, len(order) + 1)
        best = search.best_params_
        cases.append({
            "label": localized(ru, kk),
            "note": localized(
                f"{len(order)} кандидатов. Лидер: C={best['svc__C']}, gamma={best['svc__gamma']}, "
                f"macro-F1 CV={search.best_score_:.3f}.",
                f"{len(order)} үміткер. Үздігі: C={best['svc__C']}, gamma={best['svc__gamma']}, "
                f"macro-F1 CV={search.best_score_:.3f}."),
            "series": [series("Валидация", "Валидация", "line", indices, report["mean_test_score"][order]),
                       series("Обучение", "Оқыту", "line", indices, report["mean_train_score"][order])],
        })
    return cases, searches[0][2].best_estimator_


def test_cases(model, test_x, test_y, train_x):
    with tempfile.TemporaryDirectory() as directory:
        artifact = Path(directory) / "model.joblib"
        joblib.dump(model, artifact)
        restored = joblib.load(artifact)
        predictions = restored.predict(test_x)
    original = model.predict(test_x)
    if not np.array_equal(original, predictions):
        raise ValueError("Reload changed the predicted classes")
    rng = np.random.default_rng(3305)
    shifted = test_x + rng.normal(0, 1.5, test_x.shape) * train_x.std(axis=0)
    cases = []
    for ru, kk, y in (
        ("Тест", "Тест", original),
        ("После загрузки", "Қайта жүктеген соң", predictions),
        ("Тест с шумом", "Шуы бар тест", restored.predict(shifted)),
    ):
        accuracy = accuracy_score(test_y, y)
        f1 = f1_score(test_y, y, average="macro")
        cases.append({
            "label": localized(ru, kk),
            "note": localized(f"На {len(y)} объектах: accuracy={accuracy:.3f}, macro-F1={f1:.3f}.",
                              f"{len(y)} объект үшін accuracy={accuracy:.3f}, macro-F1={f1:.3f}."),
            "series": [series("Метрики", "Метрикалар", "bar", (1, 2), (accuracy, f1))],
            "xTicks": [{"value": i, "label": localized(name, name)}
                       for i, name in enumerate(("Accuracy", "Macro-F1"), 1)],
        })
    return cases


def main():
    x, y = load_wine(return_X_y=True)
    train_x, test_x, train_y, test_y = train_test_split(
        x, y, test_size=0.25, stratify=y, random_state=3305,
    )
    pipeline = make_pipeline(StandardScaler(), SVC())
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=3305)
    search, best = search_cases(pipeline, train_x, train_y, cv)
    result = [cv_cases(pipeline, train_x, train_y), search,
              test_cases(best, test_x, test_y, train_x)]
    print(json.dumps({"topics": result}, ensure_ascii=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
