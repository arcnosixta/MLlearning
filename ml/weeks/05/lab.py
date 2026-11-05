"""Линейная регрессия: предсказываем минуты поездки по километрам."""
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

LANGUAGE = os.environ.get("IMLEARNING_LANG", "ru")


def text(ru, kk):
    return kk if LANGUAGE == "kk" else ru


# Небольшие вымышленные поездки. Измени минуты, а затем запусти заново.
SEED = 12
km = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])
minutes = np.array([9, 13, 14, 19, 20, 25, 25, 30, 33, 34, 39, 40, 45, 46, 52, 52])
X_train, X_test, y_train, y_test = train_test_split(
    km.reshape(-1, 1), minutes, test_size=0.25, random_state=SEED,
)
model = LinearRegression()
model.fit(X_train, y_train)
prediction = model.predict(X_test)
baseline = np.full(len(y_test), y_train.mean())
mae = mean_absolute_error(y_test, prediction)
rmse = mean_squared_error(y_test, prediction) ** 0.5

print(text("Учебные поездки. Train:", "Оқу сапарлары. Train:"), len(y_train),
      text("Test:", "Test:"), len(y_test))
print(text("Наклон, мин/км:", "Көлбеулік, мин/км:"), f"{model.coef_[0]:.2f}")
print(text("Начальное значение, мин:", "Бастапқы мән, мин:"), f"{model.intercept_:.2f}")
print(text("MAE базового среднего, мин:", "Базалық орташа MAE, мин:"),
      f"{mean_absolute_error(y_test, baseline):.2f}")
print(f"MAE = {mae:.2f}; RMSE = {rmse:.2f} " + text("мин", "мин"))
print(f"R² = {r2_score(y_test, prediction):.2f}")
print(text("Всего 4 поездки test; другой seed может изменить оценку.",
           "Test ішінде 4 сапар ғана; басқа seed бағалауды өзгерте алады."))

line = np.linspace(km.min(), km.max(), 50).reshape(-1, 1)
plt.figure(figsize=(7, 4))
plt.scatter(X_train[:, 0], y_train, label=text("Train: обучение", "Train: оқыту"))
plt.scatter(X_test[:, 0], y_test, label=text("Test: проверка", "Test: тексеру"), marker="s")
plt.plot(line[:, 0], model.predict(line), color="green", label=text("Модель по train", "Train бойынша модель"))
plt.xlabel(text("Расстояние, км", "Қашықтық, км"))
plt.ylabel(text("Длительность, мин", "Ұзақтығы, мин"))
plt.title(text("Линия обучена без test", "Түзу test деректерінсіз оқытылды"))
plt.legend()
plt.tight_layout()
plt.show()
