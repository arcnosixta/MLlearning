"""Week 3 | python experiments.py [--plot]. Plot mode uses Matplotlib and Seaborn."""

import json
import sys

import numpy as np
import pandas as pd


def text(ru, kk):
    return {"ru": ru, "kk": kk}


def series(ru, kk, kind, x, y):
    return {"label": text(ru, kk), "kind": kind,
            "points": [[round(float(a), 4), round(float(b), 4)] for a, b in zip(x, y, strict=True)]}


def case(ru, kk, note_ru, note_kk, *curves):
    return {"label": text(ru, kk), "note": text(note_ru, note_kk), "series": curves}


def observations():
    rng = np.random.default_rng(41)
    counts = {"A": 36, "B": 48, "C": 16}
    station = np.repeat(list(counts), list(counts.values()))
    queue = rng.integers(1, 15, len(station))
    delay = np.clip(2 + queue * 0.9 + np.select([station == "B", station == "C"], [4, -1]) + rng.normal(0, 3, len(station)), 1, None)
    delay[[8, 47, 96]] += 21
    raw = pd.DataFrame({"station": station, "queue": queue, "wait_min": delay})
    raw.loc[[10, 42, 79], "wait_min"] = np.nan
    return pd.concat([raw, raw.iloc[[2]]], ignore_index=True)


def distribution(clean):
    y = clean["wait_min"].dropna()
    out = []
    for bins, ru, kk in [(5, "5 интервалов", "5 аралық"), (10, "10 интервалов", "10 аралық"), (20, "20 интервалов", "20 аралық")]:
        counts, edges = np.histogram(y, bins=bins)
        centers = (edges[1:] + edges[:-1]) / 2
        out.append(case(ru, kk, "Столбец считает наблюдения внутри интервала вокруг его центра.", "Баған өз ортасының айналасындағы аралыққа түскен бақылауларды санайды.", series("Частота", "Жиілік", "bar", centers, counts)))
    return out


def relationships(clean):
    valid = clean.dropna(subset=["wait_min"])
    trimmed = valid[valid["wait_min"] <= valid["wait_min"].quantile(0.95)]
    return [
        case("Все точки", "Барлық нүкте", "По облаку оцените направление связи и найдите необычные дни.", "Нүктелерден байланыс бағытын бағалап, ерекше күндерді табыңыз.", series("Наблюдения", "Бақылаулар", "scatter", valid["queue"], valid["wait_min"])),
        case("Цвет по станции", "Бекет бойынша түс", "При той же очереди станции могут различаться по времени ожидания.", "Кезек бірдей болса да, күту уақыты бекетке қарай өзгеруі мүмкін.", *(series(name, name, "scatter", group["queue"], group["wait_min"]) for name, group in valid.groupby("station"))),
        case("Без верхних 5%", "Ең жоғарғы 5% мәнсіз", "Это отдельный вид для проверки чувствительности. Исходные строки не удаляются.", "Бұл — сезімталдықты тексеретін бөлек көрініс. Бастапқы жолдар жойылмайды.", series("Ниже 95-го процентиля или на нём", "95-процентильден аспайтын мәндер", "scatter", trimmed["queue"], trimmed["wait_min"])),
    ]


def comparisons(clean):
    grouped = clean.groupby("station")["wait_min"]
    out = []
    for ru, kk, note_ru, note_kk, values in [
        ("Число записей", "Жазба саны", "size считает и строки с пропуском времени.", "size уақыт мәні жоқ жолдарды да санайды.", grouped.size()),
        ("Среднее ожидание", "Орташа күту уақыты", "Долгие ожидания сильнее сдвигают среднее, чем медиану.", "Ұзақ күту орташа мәнді медианадан көбірек өзгертеді.", grouped.mean()),
        ("Медиана ожидания", "Күту уақытының медианасы", "Половина известных наблюдений группы не больше медианы.", "Топтағы белгілі бақылаулардың кемінде жартысы медианадан аспайды.", grouped.median()),
    ]:
        positions = range(1, len(values) + 1)
        result = case(ru, kk, note_ru, note_kk, series(ru, kk, "bar", positions, values))
        result["xTicks"] = [{"value": i, "label": text(name, name)} for i, name in zip(positions, values.index)]
        out.append(result)
    return out


def diagnostics(raw, clean):
    def audit(frame):
        return [len(frame), int(frame["wait_min"].isna().sum()), int(frame.duplicated().sum())]

    items = [
        ("Исходные данные", "Бастапқы дерек", "Сначала зафиксируйте исходные объёмы.", "Алдымен бастапқы көлемді белгілеңіз.", raw),
        ("Точные дубликаты сняты", "Дәл көшірмелер алынды", "Удалена одна точная копия. Строки с пропусками сохранены.", "Бір дәл көшірме жойылды. Бос мәні бар жолдар сақталды.", clean),
        ("Только для графиков времени", "Тек уақыт графиктеріне", "График ожидания использует только записи с известным временем.", "Күту графигінде уақыты белгілі жазбалар ғана қолданылады.", clean.dropna(subset=["wait_min"])),
    ]
    out = []
    for ru, kk, note_ru, note_kk, frame in items:
        result = case(ru, kk, note_ru, note_kk, series("Аудит", "Тексеру", "bar", [1, 2, 3], audit(frame)))
        result["xTicks"] = [{"value": i, "label": text(r, k)} for i, (r, k) in enumerate([("Строки", "Жол"), ("Пропуски", "Бос мән"), ("Копии", "Көшірме")], start=1)]
        out.append(result)
    return out


if __name__ == "__main__":
    raw = observations()
    clean = raw.drop_duplicates()
    print(json.dumps({"topics": [distribution(clean), relationships(clean), comparisons(clean), diagnostics(raw, clean)]}))
    if "--plot" in sys.argv:
        import matplotlib.pyplot as plt
        import seaborn as sns

        fig, axes = plt.subplots(2, 2, figsize=(9, 6), layout="constrained")
        axes[0, 0].hist(clean["wait_min"].dropna(), bins=10)
        axes[0, 0].set(xlabel="Waiting time (minutes)", ylabel="Count")
        sns.scatterplot(data=clean, x="queue", y="wait_min", hue="station", ax=axes[0, 1])
        sns.boxplot(data=clean, x="station", y="wait_min", ax=axes[1, 0])
        sns.countplot(data=clean, x="station", ax=axes[1, 1])
        plt.show()
