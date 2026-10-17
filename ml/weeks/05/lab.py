"""Week 05: compare models and inspect their errors on synthetic trips.

Run: python lab.py. Requires numpy and scikit-learn.
"""
import json

import numpy as np
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

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


def scores(y, prediction):
    mae = mean_absolute_error(y, prediction)
    mse = mean_squared_error(y, prediction)
    return f"MAE={mae:.2f} · MSE={mse:.2f} · RMSE={mse**0.5:.2f} · R²={r2_score(y, prediction):.2f}"


def build_lab():
    rng = np.random.default_rng(3305)
    distance = rng.uniform(1, 18, 120)
    stops = rng.integers(0, 7, distance.size)
    minutes = 6 + 2.6 * distance + 3 * stops + rng.normal(0, 1.8, distance.size)
    features = np.column_stack((distance, stops))
    train_x, test_x, train_y, test_y = train_test_split(
        features, minutes, test_size=0.3, random_state=12,
    )
    one = LinearRegression().fit(train_x[:, :1], train_y)
    both = LinearRegression().fit(train_x, train_y)
    baseline = DummyRegressor(strategy="mean").fit(train_x, train_y)

    train_distance = train_x[:, 0]
    limits = [train_distance.min(), train_distance.max()]
    training_points = series("Поездки train", "Оқу сапарлары", "scatter", train_distance, train_y)
    line_cases = []
    for ru, kk, slope, intercept in (
        ("Среднее train", "Train орташа мәні", 0, train_y.mean()),
        ("Обученная прямая", "Оқытылған түзу", one.coef_[0], one.intercept_),
        ("Слишком крутой наклон", "Тым үлкен көлбеулік", 5.5, one.intercept_),
    ):
        mse = mean_squared_error(train_y, intercept + slope * train_distance)
        note = f"w={slope:.2f} · b={intercept:.2f} · MSE={mse:.2f}"
        line_cases.append(case(
            ru, kk, note, note, training_points,
            series("Прогноз", "Болжам", "line", limits, [intercept + slope * x for x in limits]),
        ))

    test_cases = []
    reference = [min(test_y) - 2, max(test_y) + 2]
    two_predictions = both.predict(test_x)
    for ru, kk, prediction in (
        ("Базовый прогноз", "Базалық болжам", baseline.predict(test_x)),
        ("Только расстояние", "Тек қашықтық", one.predict(test_x[:, :1])),
        ("Расстояние и остановки", "Қашықтық пен аялдамалар", two_predictions),
    ):
        note = f"n={test_y.size} · {scores(test_y, prediction)}"
        test_cases.append(case(
            ru, kk, note, note,
            series("Идеальный прогноз", "Мінсіз болжам", "line", reference, reference),
            series("Поездки test", "Сынақ сапарлары", "scatter", test_y, prediction),
        ))

    outlier = two_predictions.copy()
    outlier[0] += 35
    residual_cases = []
    for ru, kk, prediction in (
        ("Без вмешательства", "Өзгеріссіз", two_predictions),
        ("Один большой промах", "Бір үлкен қате", outlier),
        ("Сдвиг на 8 минут", "8 минуттық ығысу", two_predictions + 8),
    ):
        note = scores(test_y, prediction)
        residual_cases.append(case(
            ru, kk, note, note,
            series("Нулевой остаток", "Нөлдік қалдық", "line", [min(prediction), max(prediction)], [0, 0]),
            series("Остатки", "Қалдықтар", "scatter", prediction, test_y - prediction),
        ))
    return {"topics": [line_cases, test_cases, residual_cases]}


if __name__ == "__main__":
    print(json.dumps(build_lab(), ensure_ascii=False, allow_nan=False))
