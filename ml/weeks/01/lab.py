"""Week 1 | Run with Python or upload to Colab and run: !python lab.py"""

import json
import random
from statistics import mean


def text(ru, kk):
    return {"ru": ru, "kk": kk}


def series(ru, kk, kind, x_values, y_values):
    return {
        "label": text(ru, kk),
        "kind": kind,
        "points": [[x, round(y, 4)] for x, y in zip(x_values, y_values, strict=True)],
    }


def case(ru, kk, note_ru, note_kk, *curves):
    return {"label": text(ru, kk), "note": text(note_ru, note_kk), "series": curves}


def predictions():
    # One observation means one library day. Train on the first six days.
    groups = [1, 2, 2, 3, 4, 5, 3, 4, 6]
    seats = [12, 15, 18, 22, 26, 29, 21, 27, 34]
    train_x, train_y = groups[:6], seats[:6]
    average_x, average_y = mean(train_x), mean(train_y)
    slope = sum((x - average_x) * (y - average_y) for x, y in zip(train_x, train_y))
    slope /= sum((x - average_x) ** 2 for x in train_x)
    intercept = average_y - slope * average_x
    x_range = range(min(groups), max(groups) + 1)
    baseline = series("Среднее train", "Train орташа мәні", "line", x_range, [average_y] * len(x_range))
    trend = series("Обученная прямая", "Үйретілген түзу", "line", x_range, [intercept + slope * x for x in x_range])
    train = series("Обучающие дни", "Үйрету күндері", "scatter", train_x, train_y)
    test = series("Новые дни", "Жаңа күндер", "scatter", groups[6:], seats[6:])
    return [
        case("Только train", "Тек train", "Подберите правило по этим дням.", "Ережені осы күндерге сүйеніп таңдаңыз.", train),
        case("Базовый прогноз", "Базалық болжам", "Среднее по train постоянно. Сравните его с новыми днями.", "Train орташа мәні тұрақты. Оны жаңа күндермен салыстырыңыз.", train, test, baseline),
        case("Обученная модель", "Үйретілген модель", "Прямая обучена на тех же днях. Проверьте её на новых точках.", "Түзу сол күндерден үйретілді. Оны жаңа нүктелермен тексеріңіз.", train, test, trend),
    ]


def learning_types():
    rng = random.Random(14)
    hours = [rng.randint(1, 12) for _ in range(24)]
    exercises = [max(0, h // 2 + rng.randint(-2, 2)) for h in hours]
    passed = [3 * h + 4 * n >= 26 for h, n in zip(hours, exercises, strict=True)]
    labeled = []
    for value, ru, kk in [(False, "Пока не сдал", "Әлі тапсырмаған"), (True, "Сдал", "Тапсырған")]:
        rows = [(h, n) for h, n, result in zip(hours, exercises, passed) if result == value]
        x, y = zip(*rows)
        labeled.append(series(ru, kk, "scatter", x, y))

    # Two trial schedules, with the reward recorded only after the choice.
    reward = []
    for cadence, ru, kk in [(1, "Один подход", "Бір кезең"), (3, "Три подхода", "Үш кезең")]:
        attempts = range(1, 9)
        gains = [sum(rng.random() < (0.35 + 0.1 * cadence) for _ in range(6)) for _ in attempts]
        reward.append(series(ru, kk, "line", attempts, gains))
    return [
        case("Есть метки", "Жауаптар бар", "Цвет обозначает известный результат. Это задача классификации.", "Түс белгілі нәтижені көрсетеді. Бұл жіктеу есебі.", *labeled),
        case("Метки скрыты", "Жауаптар жасырылған", "Ищите группы по признакам. Сам по себе кластер ничего не говорит о сдаче.", "Топтарды белгілер бойынша іздеңіз. Кластердің өзі нәтиже туралы айтпайды.", series("Наблюдения", "Бақылаулар", "scatter", hours, exercises)),
        case("Награда за действие", "Әрекет үшін сыйақы", "По горизонтали номер попытки, по вертикали число решённых задач. Это наблюдения за двумя действиями, без обучения агента.", "Көлденең осьте талпыныс нөмірі, тік осьте шешілген есеп саны. Бұл екі әрекеттің бақылаулары, агент үйретілген жоқ.", *reward),
    ]


def notebook_state():
    def running_totals(values):
        return [sum(values[:end]) for end in range(1, len(values) + 1)]

    original = [15, 20, 10, 25]
    edited = [15, 20, 30, 25]
    steps = range(1, len(original) + 1)
    before = series("Вывод до изменения", "Өзгеріске дейінгі нәтиже", "line", steps, running_totals(original))
    after = series("Вывод после запуска", "Іске қосқаннан кейінгі нәтиже", "line", steps, running_totals(edited))
    return [
        case("Первый запуск", "Алғашқы іске қосу", "Выполнены ячейка с данными и ячейка с расчётом.", "Дерек ұяшығы мен есептеу ұяшығы орындалды.", before),
        case("Отредактировали код", "Кодты өзгерттік", "Старый вывод виден, пока ячейки ещё не выполнены заново.", "Ұяшықтар қайта орындалмайынша ескі нәтиже көрінеді.", before),
        case("Перезапустили всё", "Барлығын қайта орындадық", "После последовательного запуска изменение третьего занятия учтено в результате.", "Ретпен қайта орындағанда үшінші сабақтағы өзгеріс нәтижеге енді.", after),
    ]


def python_basics():
    minutes = [18, 30, 45, 15, 52, 28, 33]

    def running_counts(threshold):
        total, counts = 0, []
        for duration in minutes:
            if duration >= threshold:
                total += 1
            counts.append(total)
        return counts

    return [
        case(f"Порог {threshold}", f"Шек {threshold}", "Счётчик растёт, если время занятия достигает порога.", "Сабақ уақыты шекке жетсе, санауыш өседі.", series("Накопленный счётчик", "Жинақталған сан", "line", range(1, 8), running_counts(threshold)))
        for threshold in (20, 30, 40)
    ]


if __name__ == "__main__":
    print(json.dumps({"topics": [predictions(), learning_types(), notebook_state(), python_basics()]}))
