"""Дерево и лес: сравниваем обучение и тест. python lab.py"""
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_moons
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

# Попробуй глубину 1, 3, 10. Выбирай настройки по валидации, не по тесту.
MAX_DEPTH = 3
LANGUAGE = os.environ.get("IMLEARNING_LANG", "ru")


def text(ru, kk):
    return kk if LANGUAGE == "kk" else ru


# Шумные дуги — синтетические данные с двумя классами 0 и 1.
x, y = make_moons(n_samples=120, noise=0.25, random_state=9)
train_x, test_x, train_y, test_y = train_test_split(
    x, y, test_size=0.3, stratify=y, random_state=42
)
models = [DecisionTreeClassifier(max_depth=MAX_DEPTH, random_state=42),
          RandomForestClassifier(n_estimators=30, max_depth=MAX_DEPTH, random_state=42)]
names = [text("Дерево", "Ағаш"), text("Лес: 30 деревьев", "Орман: 30 ағаш")]
train_scores, test_scores = [], []
print(text("Учебные данные: две дуги. Обучение: 84, тест: 36.",
           "Оқу деректері: екі доға. Оқыту: 84, тест: 36."))
print(text("Модель                 Обучение    Тест", "Модель                  Оқыту     Тест"))
for name, model in zip(names, models):
    model.fit(train_x, train_y)
    train_score = model.score(train_x, train_y)
    test_score = model.score(test_x, test_y)
    train_scores.append(train_score)
    test_scores.append(test_score)
    print(f"{name:<23} {train_score:7.1%} {test_score:8.1%}")
print(text("Большой разрыв может указывать на переобучение. Один тест — не гарантия.",
           "Үлкен айырма артық үйренуді көрсетуі мүмкін. Бір тест кепілдік бермейді."))
positions = np.arange(len(names))
figure, plot = plt.subplots(figsize=(7, 4), constrained_layout=True)
plot.bar(positions - 0.18, train_scores, 0.36, label=text("Обучение", "Оқыту"))
plot.bar(positions + 0.18, test_scores, 0.36, label=text("Тест", "Тест"))
plot.set_xticks(positions, names)
plot.set(ylim=(0, 1.05), ylabel=text("Доля верных ответов", "Дұрыс жауаптар үлесі"),
         title=text(f"Максимальная глубина: {MAX_DEPTH}", f"Ең үлкен тереңдік: {MAX_DEPTH}"))
plot.legend()
plot.grid(axis="y", alpha=0.2)
plt.show()
