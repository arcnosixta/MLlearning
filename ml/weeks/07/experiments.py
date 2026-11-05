"""Week 07: evaluate alerts on a synthetic imbalanced dataset."""
import json

import numpy as np
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, confusion_matrix, f1_score, precision_score,
    recall_score, roc_auc_score, roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
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


def build_lab():
    x, y = make_classification(
        n_samples=800, n_features=6, n_informative=4, n_redundant=0,
        weights=[0.88, 0.12], class_sep=0.9, random_state=81,
    )
    train_x, test_x, train_y, test_y = train_test_split(
        x, y, stratify=y, test_size=0.35, random_state=3305,
    )

    logistic = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
    neighbors = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=15))
    logistic.fit(train_x, train_y)
    neighbors.fit(train_x, train_y)
    logistic_score = logistic.predict_proba(test_x)[:, 1]
    neighbor_score = neighbors.predict_proba(test_x)[:, 1]

    matrix_names = ["TN", "FP", "FN", "TP"]
    matrix_cases = []
    for threshold in (0.2, 0.5, 0.8):
        matrix = confusion_matrix(test_y, logistic_score >= threshold, labels=[0, 1])
        tn, fp, fn, tp = matrix.ravel()
        counts = f"TN={tn} · FP={fp} · FN={fn} · TP={tp}"
        matrix_cases.append(case(
            f"Порог {threshold:.2f}", f"Шек {threshold:.2f}",
            f"{counts} · цена={fp + 5 * fn}", f"{counts} · құны={fp + 5 * fn}",
            series("Исходы", "Нәтижелер", "bar", range(4), matrix.ravel()),
            ticks=[(name, name) for name in matrix_names],
        ))

    metric_names = ["Accuracy", "Precision", "Recall", "F1"]
    constant = np.zeros_like(test_y)
    metric_cases = []
    for ru, kk, prediction in (
        ("Всегда класс 0", "Үнемі 0-класс", constant),
        ("Порог 0.50", "Шек 0.50", logistic_score >= 0.5),
        ("Порог 0.20", "Шек 0.20", logistic_score >= 0.2),
    ):
        values = [
            accuracy_score(test_y, prediction),
            precision_score(test_y, prediction, zero_division=0),
            recall_score(test_y, prediction, zero_division=0),
            f1_score(test_y, prediction, zero_division=0),
        ]
        note = " · ".join(f"{name}={value:.3f}" for name, value in zip(metric_names, values, strict=True))
        metric_cases.append(case(
            ru, kk, note, note,
            series("Метрики", "Метрикалар", "bar", range(4), values),
            ticks=[(name, name) for name in metric_names],
        ))

    roc_cases = []
    for ru, kk, scores in (
        ("Константный балл", "Тұрақты ұпай", constant),
        ("Логистическая регрессия", "Логистикалық регрессия", logistic_score),
        ("kNN", "kNN", neighbor_score),
    ):
        fpr, tpr, _ = roc_curve(test_y, scores)
        area = roc_auc_score(test_y, scores)
        permitted = np.max(tpr[fpr <= 0.1])
        note = f"AUC={area:.3f} · max TPR (FPR≤0.10)={permitted:.3f}"
        roc_cases.append(case(
            ru, kk, note, note,
            series("Случайный ориентир", "Кездейсоқ бағдар", "line", [0, 1], [0, 1]),
            series("ROC модели", "Модельдің ROC қисығы", "line", fpr, tpr),
        ))
    return {"topics": [matrix_cases, metric_cases, roc_cases]}


if __name__ == "__main__":
    print(json.dumps(build_lab(), ensure_ascii=False, allow_nan=False))
