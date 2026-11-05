"""SVM и kNN: две границы на одних учебных данных. python lab.py"""
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_circles
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

# Измени число соседей (например, 1, 5, 15) и запусти снова.
NEIGHBORS = 5
LANGUAGE = os.environ.get("IMLEARNING_LANG", "ru")


def text(ru, kk):
    return kk if LANGUAGE == "kk" else ru


# Два кольца — синтетические классы, а не реальные измерения.
x, y = make_circles(n_samples=120, factor=0.45, noise=0.12, random_state=8)
train_x, test_x, train_y, test_y = train_test_split(
    x, y, test_size=0.3, stratify=y, random_state=42
)
models = {"kNN": KNeighborsClassifier(n_neighbors=NEIGHBORS),
          "SVM (RBF)": SVC(kernel="rbf", C=1)}
axis = np.linspace(-1.4, 1.4, 70)
grid_x, grid_y = np.meshgrid(axis, axis)
grid = np.column_stack([grid_x.ravel(), grid_y.ravel()])
figure, plots = plt.subplots(1, 2, figsize=(9, 4), constrained_layout=True)
print(text("Учебные кольца: 84 точки для обучения, 36 для теста.",
           "Оқу сақиналары: оқытуға 84, тестке 36 нүкте."))
print(text("Точка = истинный класс; фон = прогноз модели.",
           "Нүкте = шынайы класс; фон = модель болжамы."))
for plot, (name, classifier) in zip(plots, models.items()):
    # Масштабирование обучается только на train.
    model = make_pipeline(StandardScaler(), classifier)
    model.fit(train_x, train_y)
    prediction = model.predict(grid).reshape(grid_x.shape)
    plot.contourf(grid_x, grid_y, prediction, levels=[-0.5, 0.5, 1.5],
                  colors=["#dbeafe", "#ffedd5"], alpha=0.8)
    for label, color in [(0, "#2563eb"), (1, "#c2410c")]:
        points = test_x[test_y == label]
        plot.scatter(points[:, 0], points[:, 1], color=color, edgecolors="white",
                     label=text(f"Класс {label}", f"{label}-класс"))
    score = model.score(test_x, test_y)
    print(f"{name}: " + text("доля верных ответов", "дұрыс жауаптар үлесі") + f" = {score:.1%}")
    plot.set(title=name, xlabel=text("Координата x₁", "x₁ координатасы"),
             ylabel=text("Координата x₂", "x₂ координатасы"), aspect="equal")
    plot.legend()
print(text("Малый учебный тест не доказывает превосходство алгоритма.",
           "Шағын оқу тесті алгоритмнің артықшылығын дәлелдемейді."))
plt.show()
