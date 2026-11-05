"""Выбираем C по кросс-валидации, затем один раз проверяем тест."""
import os
import matplotlib.pyplot as plt
from sklearn.datasets import load_wine
from sklearn.metrics import f1_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

# Настройки сравниваем только внутри обучающей выборки.
C_VALUES = [0.1, 1.0, 10.0]
LANGUAGE = os.environ.get("IMLEARNING_LANG", "ru")


def text(ru, kk):
    return kk if LANGUAGE == "kk" else ru


wine = load_wine()
# Для простоты: только алкоголь (%) и интенсивность цвета.
x, y = wine.data[:, [0, 9]], wine.target
train_x, test_x, train_y, test_y = train_test_split(
    x, y, test_size=0.3, stratify=y, random_state=42
)
pipeline = make_pipeline(StandardScaler(), SVC(kernel="linear"))
folds = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
search = GridSearchCV(pipeline, {"svc__C": C_VALUES}, cv=folds, scoring="f1_macro")
search.fit(train_x, train_y)
print(text("Wine: два химических признака, три сорта вина (классы 0–2).",
           "Wine: екі химиялық белгі, үш шарап сұрыпы (0–2 кластары)."))
print(text(f"Обучение: {len(train_y)} строк; отложенный тест: {len(test_y)}.",
           f"Оқыту: {len(train_y)} жол; бөлек тест: {len(test_y)}."))
print(text("C       Средний F1 по 3 фолдам ± разброс σ", "C       3 фолд бойынша орташа F1 ± шашырау σ"))
means = search.cv_results_["mean_test_score"]
deviations = search.cv_results_["std_test_score"]
for value, mean, deviation in zip(C_VALUES, means, deviations):
    print(f"{value:<7g} {mean:.3f} ± {deviation:.3f}")
print(text("Выбрано C", "Таңдалған C") + f" = {search.best_params_['svc__C']:g}")
prediction = search.predict(test_x)
print(text("Финальный тест, macro-F1", "Соңғы тест, macro-F1")
      + f" = {f1_score(test_y, prediction, average='macro'):.3f}")
print(text("Повторный подбор по тесту превращает его в валидацию.",
           "Тест бойынша қайта таңдау оны валидацияға айналдырады."))
figure, plot = plt.subplots(figsize=(7, 4), constrained_layout=True)
plot.errorbar(range(len(C_VALUES)), means, yerr=deviations, marker="o", capsize=5)
plot.set_xticks(range(len(C_VALUES)), [f"C={value:g}" for value in C_VALUES])
plot.set(ylim=(0, 1.05), xlabel=text("Настройка модели", "Модель баптауы"),
         ylabel=text("Macro-F1 на валидации", "Валидациядағы macro-F1"),
         title=text("Среднее и разброс по 3 фолдам", "3 фолдтың орташа мәні мен шашырауы"))
plot.grid(alpha=0.2)
plt.show()
