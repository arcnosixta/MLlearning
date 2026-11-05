"""Один нейрон с линейным выходом: учим прогноз балла по часам подготовки."""
import os
import numpy as np
import matplotlib.pyplot as plt

LEARNING_RATE = 0.3  # Измени шаг обучения, например на 0.05.
EPOCHS = 400         # Измени число шагов, например на 40.
LANGUAGE = os.environ.get("IMLEARNING_LANG", "ru")


def text(ru, kk):
    return kk if LANGUAGE == "kk" else ru


# Учебные вымышленные наблюдения. Четыре строки отложены до обучения.
hours = np.arange(1, 11, dtype=float)
scores = np.array([14, 20, 29, 35, 43, 47, 55, 60, 69, 76])
is_test = np.array([False, True, False, False, True, False, False, True, False, True])
x_train, y_train = hours[~is_test] / 10, scores[~is_test]
x_test, y_test = hours[is_test] / 10, scores[is_test]

# Нейрон: прогноз = вес × вход + смещение. Деление на 10 — смена единиц.
weight, bias = 0.0, 0.0
losses = []
for epoch in range(EPOCHS + 1):
    error = weight * x_train + bias - y_train
    losses.append(np.mean(error ** 2))
    if epoch == EPOCHS:
        break
    weight -= LEARNING_RATE * 2 * np.mean(error * x_train)
    bias -= LEARNING_RATE * 2 * np.mean(error)

predictions = weight * x_test + bias
print(text("Учебные данные: 10 занятий; один линейный нейрон, без скрытых слоёв.",
           "Оқу деректері: 10 сабақ; жасырын қабатсыз бір сызықтық нейрон."))
print(text("Обучение: 6 строк; проверка: 4 новые строки.",
           "Оқыту: 6 жол; тексеру: 4 жаңа жол."))
print(text("Ошибка обучения MSE, балл²:", "Оқыту қатесі MSE, балл²:"),
      f"{losses[0]:.1f} → {losses[-1]:.1f}")
print(text("Средняя ошибка на проверке MAE, балл:", "Тексерудегі орташа қате MAE, балл:"),
      f"{np.mean(np.abs(y_test - predictions)):.1f}")

fig, axes = plt.subplots(1, 2, figsize=(9, 3.5))
axes[0].plot(losses)
axes[0].set(xlabel=text("Шаг обучения", "Оқыту қадамы"),
            ylabel=text("MSE, балл²", "MSE, балл²"),
            title=text("Нейрон уменьшает ошибку", "Нейрон қатені азайтады"))
axes[1].scatter(hours[~is_test], y_train, label=text("Обучение", "Оқыту"))
axes[1].scatter(hours[is_test], y_test, marker="x", label=text("Проверка", "Тексеру"))
axes[1].plot(hours, weight * hours / 10 + bias, label=text("Прогноз", "Болжам"))
axes[1].set(xlabel=text("Подготовка, ч", "Дайындық, сағ"),
            ylabel=text("Баллы", "Балл"), title=text("Обученная модель", "Оқытылған модель"))
axes[1].legend()
fig.tight_layout()
plt.show()