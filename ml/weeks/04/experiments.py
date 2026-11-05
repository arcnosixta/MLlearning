"""Week 4 | python experiments.py. All observations are synthetic."""

import json

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, OrdinalEncoder, StandardScaler


def text(ru, kk):
    return {"ru": ru, "kk": kk}


def series(ru, kk, kind, x, y):
    return {"label": text(ru, kk), "kind": kind,
            "points": [[round(float(a), 4), round(float(b), 4)] for a, b in zip(x, y, strict=True)]}


def case(ru, kk, note_ru, note_kk, *curves):
    return {"label": text(ru, kk), "note": text(note_ru, note_kk), "series": curves}


def missing_values():
    x = np.array([12, 15, np.nan, 17, 22, np.nan, 32, 95]).reshape(-1, 1)
    rows = np.arange(1, len(x) + 1)
    known = np.isfinite(x[:, 0])
    observed = series("Известно", "Белгілі", "scatter", rows[known], x[known, 0])
    out = [case("Оставить пропуски", "Бос мәндерді сақтау", "У третьей и шестой записей измерения нет, поэтому точки не рисуются.", "Үшінші және алтыншы жазбада өлшем жоқ, сондықтан нүкте салынбайды.", observed)]
    for method, ru, kk in [("mean", "Заполнить средним", "Орташа мәнмен толтыру"), ("median", "Заполнить медианой", "Медианамен толтыру")]:
        filled = SimpleImputer(strategy=method).fit_transform(x)[:, 0]
        out.append(case(ru, kk, "Подставленное значение показано отдельно. Сравните влияние большого наблюдения.", "Қойылған мән бөлек көрсетілген. Үлкен бақылаудың әсерін салыстырыңыз.", observed, series("Восстановлено", "Толтырылған", "scatter", rows[~known], filled[~known])))
    return out


def encoding():
    train = np.array(["A", "B", "C", "B"]).reshape(-1, 1)
    test = np.array(["C", "A", "B", "D"]).reshape(-1, 1)
    rows = np.arange(1, len(train) + 1)
    ordinal = OrdinalEncoder().fit_transform(train)[:, 0]
    encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False).fit(train)

    def flags(data):
        matrix = encoder.transform(data)
        return [series(f"Категория {label}", f"{label} санаты", "line", rows, matrix[:, i])
                for i, label in enumerate(encoder.categories_[0])]

    return [
        case("Целые коды", "Бүтін кодтар", "Коды 0, 1, 2 создают расстояния между условными названиями.", "0, 1, 2 кодтары шартты атаулардың арасына қашықтық енгізеді.", series("Код", "Код", "bar", rows, ordinal)),
        case("One-hot на train", "Train дерегіндегі one-hot", "У каждой известной категории свой индикатор.", "Әр белгілі санаттың жеке индикаторы бар.", *flags(train)),
        case("Новая категория на test", "Test дерегіндегі жаңа санат", "У четвёртой записи категория D, которой не было при обучении. Все три индикатора равны нулю.", "Төртінші жазбадағы D санаты үйрету кезінде кездеспеді. Үш индикатор да нөл.", *flags(test)),
    ]


def scaling():
    train = np.array([12, 15, 17, 22, 32, 42]).reshape(-1, 1)
    test = np.array([51, 7]).reshape(-1, 1)
    rows = np.arange(1, len(train) + len(test) + 1)
    scaled = [
        ("Исходный масштаб", "Бастапқы масштаб", "Это одна и та же числовая колонка. Последние два значения были отложены.", "Бұл бір сандық баған. Соңғы екі мән бөлек қалдырылды.", train, test),
    ]
    for scaler, ru, kk, note_ru, note_kk in [
        (StandardScaler(), "StandardScaler", "StandardScaler", "Вычитается среднее train, затем значение делится на стандартное отклонение train.", "Train орташа мәні алынады, содан кейін train стандартты ауытқуына бөлінеді."),
        (MinMaxScaler(), "MinMaxScaler", "MinMaxScaler", "Диапазон train стал от 0 до 1. Новые значения могут выйти за этот диапазон.", "Train ауқымы 0 мен 1 арасына түсті. Жаңа мәндер осы ауқымнан шығуы мүмкін."),
    ]:
        scaled.append((ru, kk, note_ru, note_kk, scaler.fit_transform(train), scaler.transform(test)))
    return [case(ru, kk, note_ru, note_kk, series("Train", "Train", "scatter", rows[:len(train)], a[:, 0]),
                 series("Test", "Test", "scatter", rows[len(train):], b[:, 0]))
            for ru, kk, note_ru, note_kk, a, b in scaled]


def pipelines():
    train = pd.DataFrame({"minutes": [12, 15, 18, np.nan, 27, 34, 38, 44],
                          "zone": ["A", "B", "A", "A", "B", "A", "B", "B"]})
    test = pd.DataFrame({"minutes": [65, np.nan, 72, 70], "zone": ["A", "B", "C", "B"]})
    train_y = [8, 12, 10, 14, 15, 17, 21, 24]
    test_y = [32, 15, 35, 37]

    def preprocessing():
        numeric = Pipeline([("impute", SimpleImputer(strategy="median")),
                            ("scale", StandardScaler())])
        category = Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                             ("onehot", OneHotEncoder(handle_unknown="ignore"))])
        return ColumnTransformer([("number", numeric, ["minutes"]), ("category", category, ["zone"])])

    clean = Pipeline([("prepare", preprocessing()), ("regression", LinearRegression())]).fit(train, train_y)
    # Deliberately wrong comparison: test statistics inform fitted preprocessing.
    leaked = preprocessing().fit(pd.concat([train, test], ignore_index=True))
    leaked_model = LinearRegression().fit(leaked.transform(train), train_y)
    rows = np.arange(1, len(test) + 1)
    observed = series("Факт test", "Нақты test", "scatter", rows, test_y)
    return [
        case("Простой ориентир", "Қарапайым бағдар", "Среднее целевой переменной на train служит базовым прогнозом.", "Train мақсатты мәндерінің орташа саны базалық болжам болады.", observed, series("Среднее train", "Train орташа мәні", "line", rows, [np.mean(train_y)] * len(test))),
        case("Разделение до fit", "fit алдында бөлу", "Pipeline обучает преобразования только на train. На test вызывается predict.", "Pipeline түрлендірулерді тек train дерегінде үйретеді. Test дерегіне predict қолданылады.", observed, series("Прогноз без утечки", "Дерек ағуынсыз болжам", "scatter", rows, clean.predict(test))),
        case("Утечка для сравнения", "Салыстыруға арналған дерек ағуы", "Обработка видела test. Даже если ошибки случайно меньше, такую оценку нельзя использовать.", "Өңдеу test дерегін көрді. Қателер кездейсоқ аз болса да, бұл бағалауды қолдануға болмайды.", observed, series("Прогноз с утечкой", "Дерек ағуы бар болжам", "scatter", rows, leaked_model.predict(leaked.transform(test)))),
    ]


if __name__ == "__main__":
    print(json.dumps({"topics": [missing_values(), encoding(), scaling(), pipelines()]}))
