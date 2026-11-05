"""Cluster synthetic customers, compare k and check what PCA preserves."""

import csv
import json
from pathlib import Path

import numpy as np
from sklearn.cluster import KMeans
from sklearn.datasets import make_classification
from sklearn.decomposition import PCA
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, silhouette_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits


def localized(ru, kk):
    return {"ru": ru, "kk": kk}


def series(ru, kk, kind, x, y):
    return {
        "label": localized(ru, kk),
        "kind": kind,
        "points": [[round(float(a), 4), round(float(b), 4)] for a, b in zip(x, y)],
    }


def read_customers():
    with Path(__file__).with_name("data.csv").open(encoding="utf-8", newline="") as file:
        rows = csv.DictReader(file)
        return np.array([[int(row[key]) for key in ("visits", "spend", "items", "recency")]
                         for row in rows], dtype=float)


def group_series(points, groups):
    return [
        series(f"Кластер {group + 1}", f"{group + 1}-кластер", "scatter",
               points[groups == group, 0], points[groups == group, 1])
        for group in np.unique(groups)
    ]


def cluster_cases(customers, models):
    cases = []
    for k in (2, 3, 5):
        groups = models[k].labels_
        sizes = ", ".join(map(str, np.bincount(groups)))
        cases.append({
            "label": localized(f"k = {k}", f"k = {k}"),
            "note": localized(f"Размеры групп: {sizes}. Обучение использовало все четыре признака.",
                              f"Топ өлшемдері: {sizes}. Оқытуға төрт белгінің бәрі қолданылды."),
            "series": group_series(customers, groups),
        })
    return cases


def quality_cases(scaled, models):
    values = list(models)
    inertias = [models[k].inertia_ for k in values]
    silhouettes = [silhouette_score(scaled, models[k].labels_) for k in values]
    best_k = values[int(np.argmax(silhouettes))]
    return [
        {"label": localized("Инерция", "Инерция"),
         "note": localized(f"От k=2 до k=6 инерция падает с {inertias[0]:.1f} до {inertias[-1]:.1f}.",
                           f"k=2-ден k=6-ға дейін инерция {inertias[0]:.1f}-ден {inertias[-1]:.1f}-ге түседі."),
         "series": [series("Инерция", "Инерция", "line", values, inertias)]},
        {"label": localized("Силуэт", "Силуэт"),
         "note": localized(f"На этом наборе лучший силуэт при k={best_k}: {max(silhouettes):.3f}.",
                           f"Осы деректе ең жоғары силуэт k={best_k} кезінде: {max(silhouettes):.3f}."),
         "series": [series("Средний силуэт", "Орташа силуэт", "line", values, silhouettes)]},
        {"label": localized("Размер малой группы", "Ең кіші топ"),
         "note": localized("При большом k проверьте, остаются ли сегменты достаточно крупными для применения.",
                           "k үлкен болса, сегменттер іс жүзінде қолдануға жеткілікті ме, тексеріңіз."),
         "series": [series("Клиентов в малой группе", "Кіші топтағы клиент саны", "bar", values,
                           [np.bincount(models[k].labels_).min() for k in values])]},
    ]


def projection_cases(customers, scaled, groups):
    cases = []
    for name, title, matrix in (
        ("Без стандартизации", "Стандарттаусыз", customers),
        ("Со стандартизацией", "Стандарттаудан кейін", scaled),
    ):
        model = PCA(n_components=2, svd_solver="full")
        projection = model.fit_transform(matrix)
        explained = model.explained_variance_ratio_.sum() * 100
        cases.append({"label": localized(name, title),
                      "note": localized(f"Две оси объясняют {explained:.1f}% вариации в выбранном масштабе.",
                                        f"Екі ось осы масштабтағы өзгергіштіктің {explained:.1f}%-ын түсіндіреді."),
                      "series": group_series(projection, groups)})
    model = PCA(n_components=1, svd_solver="full")
    projection = model.fit_transform(scaled)
    plane = np.column_stack([projection[:, 0], np.zeros(len(projection))])
    variance = 100 * model.explained_variance_ratio_[0]
    cases.append({"label": localized("Одна компонента", "Бір компонент"),
                  "note": localized(f"Остаётся {variance:.1f}% вариации, вторая координата равна нулю.",
                                    f"Өзгергіштіктің {variance:.1f}%-ы қалады, екінші координата нөлге тең."),
                  "series": group_series(plane, groups)})
    return cases


def imbalance_cases():
    features, labels = make_classification(
        n_samples=700, n_features=8, n_informative=4, weights=[0.92, 0.08],
        class_sep=0.9, random_state=3305,
    )
    train_x, test_x, train_y, test_y = train_test_split(
        features, labels, test_size=0.3, stratify=labels, random_state=7,
    )
    cases = []
    ticks = ("Accuracy", "Precision", "Recall")
    for ru, kk, model in (
        ("Только частый класс", "Жиі класс қана", DummyClassifier(strategy="most_frequent")),
        ("Логистическая регрессия", "Логистикалық регрессия",
         make_pipeline(StandardScaler(), LogisticRegression())),
        ("С весами классов", "Класс салмақтарымен",
         make_pipeline(StandardScaler(), LogisticRegression(class_weight="balanced"))),
    ):
        predicted = model.fit(train_x, train_y).predict(test_x)
        accuracy = accuracy_score(test_y, predicted)
        precision = precision_score(test_y, predicted, zero_division=0)
        recall = recall_score(test_y, predicted)
        detected = np.sum((test_y == 1) & (predicted == 1))
        total = test_y.sum()
        cases.append({
            "label": localized(ru, kk),
            "note": localized(f"Обнаружено {detected} из {total} редких объектов. "
                              f"Accuracy {accuracy:.3f}, precision {precision:.3f}, recall {recall:.3f}.",
                              f"{total} сирек объектінің {detected}-і табылды. "
                              f"Accuracy {accuracy:.3f}, precision {precision:.3f}, recall {recall:.3f}."),
            "series": [series("Оценка", "Баға", "bar", (1, 2, 3), (accuracy, precision, recall))],
            "xTicks": [{"value": i, "label": localized(name, name)} for i, name in enumerate(ticks, 1)],
        })
    return cases


def main():
    customers = read_customers()
    scaled = StandardScaler().fit_transform(customers)
    with threadpool_limits(limits=1):
        models = {k: KMeans(n_clusters=k, n_init=20, random_state=3305).fit(scaled)
                  for k in range(2, 7)}
    topics = [cluster_cases(customers, models), quality_cases(scaled, models),
              projection_cases(customers, scaled, models[3].labels_), imbalance_cases()]
    print(json.dumps({"topics": topics}, ensure_ascii=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
