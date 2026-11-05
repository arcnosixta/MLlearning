"""Логистическая регрессия: вероятность и порог — разные вещи."""
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

LANGUAGE = os.environ.get("IMLEARNING_LANG", "ru")


def text(ru, kk):
    return kk if LANGUAGE == "kk" else ru


# Синтетическая связь часов подготовки и результата. Это не оценка студентов.
THRESHOLD = 0.5  # Попробуй 0.3 и 0.7, не переобучая модель.
hours = np.array([1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11])
passed = np.array([0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1])
X_train, X_test, y_train, y_test = train_test_split(
    hours.reshape(-1, 1), passed, test_size=0.3, random_state=12, stratify=passed,
)
model = make_pipeline(StandardScaler(), LogisticRegression())
model.fit(X_train, y_train)
probability = model.predict_proba(X_test)[:, 1]
prediction = (probability >= THRESHOLD).astype(int)

print(text("Учебная классификация. 0 = не сдал, 1 = сдал.",
           "Оқу жіктеуі. 0 = тапсырмады, 1 = тапсырды."))
print(text("Порог:", "Шек:"), THRESHOLD)
print(text("Часы | Факт | Вероятность | Решение", "Сағат | Нақты | Ықтималдық | Шешім"))
for hour, actual, chance, result in zip(X_test[:, 0], y_test, probability, prediction):
    print(f"{hour:4d} | {actual:4d} | {chance:11.2f} | {result:7d}")
print(f"Accuracy (test, n={len(y_test)}) = {accuracy_score(y_test, prediction):.2f}")
print(text("Порог меняет решения, но не вероятности. Это маленький учебный набор.",
           "Шек шешімдерді өзгертеді, ықтималдықтарды өзгертпейді. Бұл шағын оқу жиыны."))

grid = np.linspace(hours.min(), hours.max(), 80).reshape(-1, 1)
plt.figure(figsize=(7, 4))
plt.scatter(X_train[:, 0], y_train, label=text("Train: известный класс", "Train: белгілі класс"), alpha=0.6)
plt.scatter(X_test[:, 0], y_test, marker="s", label=text("Test: известный класс", "Test: белгілі класс"))
plt.plot(grid[:, 0], model.predict_proba(grid)[:, 1], color="green",
         label=text("Вероятность класса 1", "1-класс ықтималдығы"))
plt.axhline(THRESHOLD, color="gray", linestyle="--", label=text("Порог", "Шек"))
plt.xlabel(text("Подготовка, часы", "Дайындық, сағат"))
plt.ylabel(text("Класс / вероятность", "Класс / ықтималдық"))
plt.title(text("Вероятность и решение по порогу", "Ықтималдық және шек бойынша шешім"))
plt.legend(fontsize=8)
plt.tight_layout()
plt.show()
