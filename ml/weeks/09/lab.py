"""Week 09: decision trees, forests, boosting and a text baseline.

Run: python lab.py
Optional comparison: install xgboost, then run python lab.py --xgboost
"""
import argparse
import json

import numpy as np
from sklearn.datasets import load_iris, make_classification
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

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


def classification_cases():
    iris = load_iris()
    train_x, test_x, train_y, test_y = train_test_split(
        iris.data[:, 2:], iris.target, test_size=0.3, stratify=iris.target, random_state=3305,
    )
    length = np.linspace(1, 7, 121)
    width = 1.4
    grid = np.column_stack((length, np.full(length.size, width)))
    cases = []
    for depth in (1, 2, 5):
        tree = DecisionTreeClassifier(max_depth=depth, random_state=3305).fit(train_x, train_y)
        p = tree.predict_proba(grid)
        scores = f"train acc.={tree.score(train_x, train_y):.3f} · test acc.={tree.score(test_x, test_y):.3f}"
        cases.append(case(
            f"Глубина {depth}", f"Тереңдік {depth}",
            f"Листьев={tree.get_n_leaves()} · ширина={width} см · {scores}",
            f"Жапырақ саны={tree.get_n_leaves()} · ені={width} см · {scores}",
            *[series(name, name, "line", length, p[:, i]) for i, name in enumerate(iris.target_names)],
        ))
    return cases


def regression_data():
    rng = np.random.default_rng(3305)
    load = np.sort(rng.uniform(0, 12, 180))
    energy = 7 + 1.2 * load + 3.6 * np.sin(load) + rng.normal(0, 2.1, load.size)
    return train_test_split(load[:, None], energy, test_size=0.35, random_state=41)


def regression_cases():
    train_x, test_x, train_y, test_y = regression_data()
    grid = np.linspace(-1, 14, 160)
    cases = []
    for minimum in (1, 5, 15):
        tree = DecisionTreeRegressor(min_samples_leaf=minimum, random_state=3305).fit(train_x, train_y)
        train_error = mean_absolute_error(train_y, tree.predict(train_x))
        test_error = mean_absolute_error(test_y, tree.predict(test_x))
        scores = f"train MAE={train_error:.2f} · test MAE={test_error:.2f}"
        cases.append(case(
            f"Минимум в листе {minimum}", f"Жапырақ минимумы {minimum}",
            f"Листьев={tree.get_n_leaves()} · {scores}",
            f"Жапырақ саны={tree.get_n_leaves()} · {scores}",
            series("Фактические значения test", "Нақты test мәндері", "scatter", test_x[:, 0], test_y),
            series("Прогноз дерева", "Ағаш болжамы", "line", grid, tree.predict(grid[:, None])),
        ))
    return cases


def forest_cases():
    x, y = make_classification(
        n_samples=420, n_features=8, n_informative=5, n_redundant=1,
        class_sep=0.8, flip_y=0.1, random_state=41,
    )
    train_x, test_x, train_y, test_y = train_test_split(
        x, y, test_size=0.35, stratify=y, random_state=3305,
    )
    seeds = (17, 42, 93)
    cases = []
    for count in (1, 15, 80):
        scores = []
        for seed in seeds:
            forest = RandomForestClassifier(n_estimators=count, random_state=seed, n_jobs=1)
            forest.fit(train_x, train_y)
            scores.append(forest.score(test_x, test_y))
        row = " · ".join(f"seed {seed}: {score:.3f}" for seed, score in zip(seeds, scores, strict=True))
        spread = max(scores) - min(scores)
        cases.append(case(
            f"Деревья: {count}", f"Ағаш саны: {count}",
            f"{row} · среднее={np.mean(scores):.3f} · размах={spread:.3f}",
            f"{row} · орташа={np.mean(scores):.3f} · ауқым={spread:.3f}",
            series("Test accuracy", "Test accuracy", "bar", range(len(seeds)), scores),
            ticks=[(str(seed), str(seed)) for seed in seeds],
        ))
    return cases


def boosting_cases():
    train_x, valid_x, train_y, valid_y = regression_data()
    model = GradientBoostingRegressor(
        n_estimators=250, max_depth=2, learning_rate=0.08, random_state=3305,
    ).fit(train_x, train_y)
    train_error = [mean_absolute_error(train_y, guess) for guess in model.staged_predict(train_x)]
    valid_error = [mean_absolute_error(valid_y, guess) for guess in model.staged_predict(valid_x)]
    cases = []
    for count in (10, 60, 250):
        steps = range(1, count + 1)
        best = int(np.argmin(valid_error[:count])) + 1
        row = f"train MAE={train_error[count - 1]:.2f} · validation MAE={valid_error[count - 1]:.2f}"
        cases.append(case(
            f"{count} шагов", f"{count} қадам",
            f"{row} · лучший шаг validation={best}",
            f"{row} · validation үздік қадамы={best}",
            series("Train", "Train", "line", steps, train_error[:count]),
            series("Validation", "Validation", "line", steps, valid_error[:count]),
        ))
    return cases


def bayes_cases():
    documents = [
        "warranty check repair", "warranty service repair", "broken device repair",
        "repair ticket service", "parcel shipping address", "shipping parcel tracking",
        "parcel delivery time", "delivery address check",
    ]
    model = make_pipeline(CountVectorizer(), MultinomialNB(alpha=1.0))
    model.fit(documents, [0, 0, 0, 0, 1, 1, 1, 1])
    queries = ["warranty repair", "parcel delivery", "music concert"]
    probabilities = model.predict_proba(queries)
    token_counts = np.asarray(model[0].transform(queries).sum(axis=1)).ravel()
    cases = []
    for message, p, count in zip(queries, probabilities, token_counts, strict=True):
        cases.append(case(
            message, message,
            f"Знакомых токенов={count} · ремонт={p[0]:.3f} · доставка={p[1]:.3f}",
            f"Таныс токендер={count} · жөндеу={p[0]:.3f} · жеткізу={p[1]:.3f}",
            series("Вероятность", "Ықтималдық", "bar", [0, 1], p),
            ticks=[("Ремонт", "Жөндеу"), ("Доставка", "Жеткізу")],
        ))
    return cases


def xgboost_comparison():
    from xgboost import XGBRegressor

    train_x, valid_x, train_y, valid_y = regression_data()
    model = XGBRegressor(
        n_estimators=250, max_depth=2, learning_rate=0.08, random_state=3305, n_jobs=1,
    ).fit(train_x, train_y)
    return {
        steps: mean_absolute_error(valid_y, model.predict(valid_x, iteration_range=(0, steps)))
        for steps in (10, 60, 250)
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xgboost", action="store_true", help="Print optional XGBoost validation MAE")
    args = parser.parse_args()
    if args.xgboost:
        result = {"xgboost_validation_mae": xgboost_comparison()}
    else:
        result = {"topics": [
            classification_cases(), regression_cases(), forest_cases(), boosting_cases(), bayes_cases(),
        ]}
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))
