"""Week 2 | python experiments.py [--plot]. The CSV fixture is embedded for Colab."""

from io import StringIO
import json
import sys

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


CSV = """day,zone,minutes,orders
1,north,18,8
2,south,24,10
3,north,27,12
3,north,27,12
4,south,,14
5, North ,35,16
6,south,unknown,17
7,north,48,21
8,south,50,22
9,north,61,26
10,south,62,27
"""


def text(ru, kk):
    return {"ru": ru, "kk": kk}


def series(ru, kk, kind, x, y):
    return {"label": text(ru, kk), "kind": kind,
            "points": [[round(float(a), 4), round(float(b), 4)] for a, b in zip(x, y, strict=True)]}


def case(ru, kk, note_ru, note_kk, *curves):
    return {"label": text(ru, kk), "note": text(note_ru, note_kk), "series": curves}


def arrays():
    values = np.array([[3, 7, 2], [6, 9, 4], [5, 10, 6], [8, 11, 8]])
    cases = [
        ("Среднее столбцов", "Бағандардың орташа мәні", "axis=0 сводит строки, остаётся по значению на столбец.", "axis=0 жолдарды біріктіреді, әр бағанға бір мән қалады.", values.mean(axis=0)),
        ("Среднее строк", "Жолдардың орташа мәні", "axis=1 сводит столбцы, остаётся по значению на строку.", "axis=1 бағандарды біріктіреді, әр жолға бір мән қалады.", values.mean(axis=1)),
        ("После порога", "Шекті қолданған соң", "np.maximum поднимает значения меньше 6 до 6. Посчитано среднее столбцов.", "np.maximum 6-дан кіші мәндерді 6-ға көтереді. Бағандардың орташа мәні есептелді.", np.maximum(values, 6).mean(axis=0)),
    ]
    return [case(ru, kk, note_ru, note_kk, series("Среднее", "Орташа мән", "bar", range(1, len(y) + 1), y))
            for ru, kk, note_ru, note_kk, y in cases]


def tables(raw):
    cleaned = raw.assign(zone=raw["zone"].str.strip().str.lower(),
                         minutes=pd.to_numeric(raw["minutes"], errors="coerce")).drop_duplicates()
    counts = cleaned.groupby("zone")["day"].size()
    means = cleaned.groupby("zone")["minutes"].mean()
    values = [
        (raw.groupby("zone").size(), "Как прочитано", "Оқылған күйі", "Пробелы и регистр разбивают северную зону на две группы, а повторы считаются дважды.", "Бос орын мен әріп регистрі солтүстік аймақты екі топқа бөледі, көшірмелер екі рет саналады."),
        (counts, "После очистки", "Тазалаған соң", "Подписи нормализованы и точные дубликаты удалены.", "Атаулар біріздендірілді және дәл көшірмелер жойылды."),
        (means, "Средние минуты", "Орташа минут", "При расчёте среднего pandas пропускает NaN. Сравните группы с учётом числа наблюдений.", "pandas орташа мәнді есептегенде NaN мәндерін өткізіп жібереді. Топтарды бақылау санын ескеріп салыстырыңыз."),
    ]
    labels = {" North ": (" North (исходная)", " North (бастапқы)"),
              "north": ("Север", "Солтүстік"), "south": ("Юг", "Оңтүстік")}
    examples = []
    for y, ru, kk, note_ru, note_kk in values:
        positions = range(1, len(y) + 1)
        result = case(ru, kk, note_ru, note_kk, series(ru, kk, "bar", positions, y))
        result["xTicks"] = [{"value": i, "label": text(*labels[zone])} for i, zone in zip(positions, y.index)]
        examples.append(result)
    return cleaned, examples


def models(cleaned):
    data = cleaned.dropna(subset=["minutes"])
    train, test = data.loc[data["day"] <= 7], data.loc[data["day"] > 7]
    # Double brackets keep a 2D feature matrix with shape (n_samples, 1).
    model = LinearRegression().fit(train[["minutes"]], train["orders"])
    grid = pd.DataFrame({"minutes": np.arange(15, 66, 5)})
    train_points = series("Обучающие дни", "Үйрету күндері", "scatter", train["minutes"], train["orders"])
    test_points = series("Новые дни", "Жаңа күндер", "scatter", test["minutes"], test["orders"])
    mean_prediction = [train["orders"].mean()] * len(grid)
    return [
        case("Обучающая выборка", "Үйрету іріктемесі", "Каждая точка — день с известным временем и числом заказов.", "Әр нүкте — уақыты мен тапсырыс саны белгілі күн.", train_points),
        case("Среднее train", "Train орташа мәні", "Базовый метод возвращает одно число независимо от времени.", "Базалық әдіс уақытқа қарамай бір сан береді.", train_points, test_points, series("Базовый прогноз", "Базалық болжам", "line", grid["minutes"], mean_prediction)),
        case("LinearRegression", "LinearRegression", "Модель обучена до седьмого дня включительно, последние три дня отложены.", "Модель жетінші күнді қоса үйретілді, соңғы үш күн тексеруге қалдырылды.", train_points, test_points, series("Прогноз", "Болжам", "line", grid["minutes"], model.predict(grid))),
    ]


def charts(cleaned):
    return [
        case("Изменение по дням", "Күн сайынғы өзгеріс", "Линия соединяет измерения по времени.", "Сызық өлшемдерді уақыт бойынша қосады.", series("Заказы", "Тапсырыстар", "line", cleaned["day"], cleaned["orders"])),
        case("Отдельные дни", "Жеке күндер", "Точки показывают отдельные наблюдения без соединения.", "Нүктелер жеке бақылауларды сызықсыз көрсетеді.", series("Заказы", "Тапсырыстар", "scatter", cleaned["day"], cleaned["orders"])),
        case("Пропуски по дням", "Күндердегі бос мәндер", "Единица обозначает отсутствие измерения времени.", "Бір саны уақыт өлшемінің жоқ екенін білдіреді.", series("Пропуск минут", "Минут мәні жоқ", "bar", cleaned["day"], cleaned["minutes"].isna().astype(int))),
    ]


if __name__ == "__main__":
    raw = pd.read_csv(StringIO(CSV))
    cleaned, table_cases = tables(raw)
    print(json.dumps({"topics": [arrays(), table_cases, models(cleaned), charts(cleaned)]}))
    if "--plot" in sys.argv:
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(8, 3), layout="constrained")
        axes[0].plot(cleaned["day"], cleaned["orders"], marker="o")
        axes[0].set(xlabel="Day", ylabel="Orders")
        axes[1].bar(cleaned["day"], cleaned["minutes"].isna().astype(int))
        axes[1].set(xlabel="Day", ylabel="Missing minutes")
        plt.show()
