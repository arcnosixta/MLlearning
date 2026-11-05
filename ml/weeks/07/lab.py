"""Сравниваем пороги: какие ошибки скрывает accuracy?"""
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

LANGUAGE = os.environ.get("IMLEARNING_LANG", "ru")


def text(ru, kk):
    return kk if LANGUAGE == "kk" else ru


# Вымышленные ответы и уже заданные вероятности: здесь модель не обучаем.
# 1 означает важное сообщение, 0 — обычное. Меняй THRESHOLD.
THRESHOLD = 0.5
actual = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1])
probability = np.array([0.05, 0.10, 0.15, 0.20, 0.25, 0.35, 0.45, 0.55, 0.75, 0.40, 0.65, 0.90])

print(text("Учебный пример: 12 сообщений, из них 3 важных.",
           "Оқу мысалы: 12 хабарлама, оның 3-еуі маңызды."))
print(text("Порог | Accuracy | Precision | Recall | F1", "Шек   | Accuracy | Precision | Recall | F1"))
for threshold in sorted(set([0.3, THRESHOLD, 0.7])):
    predicted = (probability >= threshold).astype(int)
    print(f"{threshold:5.2f} | {accuracy_score(actual, predicted):8.2f} | "
          f"{precision_score(actual, predicted, zero_division=0):9.2f} | "
          f"{recall_score(actual, predicted, zero_division=0):6.2f} | "
          f"{f1_score(actual, predicted, zero_division=0):.2f}")

predicted = (probability >= THRESHOLD).astype(int)
matrix = confusion_matrix(actual, predicted, labels=[0, 1])
tn, fp, fn, tp = matrix.ravel()
print(text("При выбранном пороге:", "Таңдалған шекте:"), f"FP={fp}, FN={fn}")
print(text("FP: обычное помечено важным; FN: важное пропущено.",
           "FP: кәдімгі хабарлама маңызды деп белгіленді; FN: маңызды хабарлама жіберілді."))
print(text("Это сравнение на одних данных, не выбор порога для реальной системы.",
           "Бұл бір деректердегі салыстыру, нақты жүйеге шек таңдау емес."))

labels = [text("Обычное", "Кәдімгі"), text("Важное", "Маңызды")]
plt.figure(figsize=(6, 4))
plt.imshow(matrix, cmap="Blues", vmin=0)
for row in range(2):
    for column in range(2):
        plt.text(column, row, str(matrix[row, column]), ha="center", va="center", fontsize=18,
                 color="white" if matrix[row, column] > matrix.max() / 2 else "black")
plt.xticks([0, 1], labels)
plt.yticks([0, 1], labels)
plt.xlabel(text("Прогноз", "Болжам"))
plt.ylabel(text("Факт", "Нақты"))
plt.title(text("Матрица ошибок, порог = ", "Қателер матрицасы, шек = ") + str(THRESHOLD))
plt.tight_layout()
plt.show()
