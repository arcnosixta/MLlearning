"""Простой прогноз: средняя загрузка библиотеки по известным дням."""
import os
import matplotlib.pyplot as plt

LANGUAGE = os.environ.get("IMLEARNING_LANG", "ru")


def text(ru, kk):
    return kk if LANGUAGE == "kk" else ru


# Вымышленные данные: число занятых мест по дням. Измени одно число.
seats = [12, 15, 18, 22, 26, 29, 21, 27, 34]
TRAIN_DAYS = 6  # Измени на 5: какие дни станут проверочными?

train = seats[:TRAIN_DAYS]
test = seats[TRAIN_DAYS:]
if not train or not test:
    raise ValueError(text("Оставь хотя бы один день в train и test.",
                          "Train мен test ішінде кемінде бір күн қалдыр."))

# Базовая модель всегда предсказывает среднее только известных дней.
prediction = sum(train) / len(train)
mae = sum(abs(value - prediction) for value in test) / len(test)
print(text("Учебные данные: занятые места в библиотеке.",
           "Оқу деректері: кітапханадағы бос емес орындар."))
print(text("Известных дней:", "Белгілі күндер:"), len(train))
print(text("Новых дней:", "Жаңа күндер:"), len(test))
print(text("Прогноз на новый день:", "Жаңа күнге болжам:"), f"{prediction:.1f}")
print(text("Средняя ошибка на новых днях, мест:",
           "Жаңа күндердегі орташа қате, орын:"), f"{mae:.1f}")
print(text("Маленький пример, а не прогноз реальной библиотеки.",
           "Бұл шағын мысал, нақты кітапханаға болжам емес."))

plt.figure(figsize=(7, 4))
plt.scatter(range(1, TRAIN_DAYS + 1), train, label=text("Train: известные дни", "Train: белгілі күндер"))
plt.scatter(range(TRAIN_DAYS + 1, len(seats) + 1), test,
            label=text("Test: новые дни", "Test: жаңа күндер"), marker="s")
plt.axhline(prediction, color="gray", linestyle="--", label=text("Среднее train", "Train орташа мәні"))
plt.xlabel(text("День наблюдения", "Бақылау күні"))
plt.ylabel(text("Занятые места", "Бос емес орындар"))
plt.title(text("Базовый прогноз и проверка", "Базалық болжам және тексеру"))
plt.legend()
plt.tight_layout()
plt.show()
