"""Свёртка на маленьком изображении: смотрим, какие границы выделяет фильтр."""
import os
import numpy as np
import matplotlib.pyplot as plt

DIRECTION = "vertical"  # Измени на "horizontal", чтобы повернуть фильтр.
LANGUAGE = os.environ.get("IMLEARNING_LANG", "ru")


def text(ru, kk):
    return kk if LANGUAGE == "kk" else ru


# 0 — тёмный пиксель, 1 — светлый. Измени положение светлого квадрата.
image = np.zeros((8, 8))
image[2:6, 2:6] = 1
kernel = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])
if DIRECTION == "horizontal":
    kernel = kernel.T
elif DIRECTION != "vertical":
    raise ValueError(text("DIRECTION: выбери vertical или horizontal.",
                          "DIRECTION: vertical не horizontal таңда."))

# Как в CNN: окно умножается на ядро без переворота (кросс-корреляция).
response = np.zeros((6, 6))
for row in range(6):
    for column in range(6):
        window = image[row:row + 3, column:column + 3]
        response[row, column] = np.sum(window * kernel)

print(text("Изображение: 8 × 8; ядро: 3 × 3; отклик без padding: 6 × 6.",
           "Кескін: 8 × 8; ядро: 3 × 3; padding жоқ жауап: 6 × 6."))
print(text("Направление:", "Бағыт:"),
      text("вертикальные границы", "тік жиектер") if DIRECTION == "vertical"
      else text("горизонтальные границы", "көлденең жиектер"))
print(text("Максимальный модуль отклика:", "Жауаптың ең үлкен модулі:"),
      f"{np.max(np.abs(response)):.1f}")
print(text("Это фиксированный фильтр: обучение CNN и распознавание здесь не выполняются.",
           "Бұл тұрақты сүзгі: мұнда CNN оқытылмайды және тану орындалмайды."))

fig, axes = plt.subplots(1, 3, figsize=(9, 3.2))
axes[0].imshow(image, cmap="gray", vmin=0, vmax=1)
axes[0].set_title(text("Исходные пиксели", "Бастапқы пиксельдер"))
axes[1].imshow(kernel, cmap="coolwarm", vmin=-1, vmax=1)
axes[1].set_title(text("Ядро фильтра", "Сүзгі ядросы"))
for row in range(3):
    for column in range(3):
        axes[1].text(column, row, str(kernel[row, column]), ha="center", va="center")
plot = axes[2].imshow(response, cmap="coolwarm", vmin=-3, vmax=3)
axes[2].set_title(text("Отклик фильтра", "Сүзгі жауабы"))
fig.colorbar(plot, ax=axes[2], shrink=0.7)
for axis in axes:
    axis.set_xlabel(text("Столбец", "Баған"))
    axis.set_ylabel(text("Строка", "Жол"))
fig.tight_layout()
plt.show()