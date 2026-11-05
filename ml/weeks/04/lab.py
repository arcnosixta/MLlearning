"""Pipeline: заполняем пропуски и кодируем категории только по train."""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

LANGUAGE = os.environ.get("IMLEARNING_LANG", "ru")


def text(ru, kk):
    return kk if LANGUAGE == "kk" else ru


# Вымышленные поездки. Первые 8 строк — train, последние 4 — test.
data = pd.DataFrame({
    "km": [1, 2, 3, 4, np.nan, 6, 7, 8, 2, 5, 9, np.nan],
    "mode": ["bus", "tram", "bus", "tram", "bus", "tram", "bus", "tram",
             "bus", "tram", "metro", "bus"],
    "minutes": [9, 12, 15, 18, 19, 25, 27, 30, 14, 22, 32, 17],
})
X = data[["km", "mode"]]
y = data["minutes"]
X_train, X_test = X.iloc[:8], X.iloc[8:]
y_train, y_test = y.iloc[:8], y.iloc[8:]

numeric = make_pipeline(SimpleImputer(strategy="median"), StandardScaler())
prepare = ColumnTransformer([
    ("distance", numeric, ["km"]),
    ("transport", OneHotEncoder(handle_unknown="ignore"), ["mode"]),
])
model = make_pipeline(prepare, LinearRegression())
model.fit(X_train, y_train)  # Test не участвует в подборе преобразований.
prediction = model.predict(X_test)
baseline = np.full(len(y_test), y_train.mean())

print(text("Учебные поездки: train=8, test=4.", "Оқу сапарлары: train=8, test=4."))
print(text("Пропуски заполнены по train; metro — новая категория test.",
           "Бос мәндер train бойынша толтырылды; metro — test жаңа санаты."))
print(text("MAE среднего train, мин:", "Train орташа мәнінің MAE, мин:"),
      f"{mean_absolute_error(y_test, baseline):.2f}")
print(text("MAE Pipeline, мин:", "Pipeline MAE, мин:"),
      f"{mean_absolute_error(y_test, prediction):.2f}")
print(text("Всего 4 проверки: надёжность в реальном мире не измерена.",
           "Бар болғаны 4 тексеру: нақты өмірдегі сенімділік өлшенбеген."))

positions = np.arange(len(y_test))
plt.figure(figsize=(7, 4))
plt.bar(positions - 0.18, y_test, width=0.36, label=text("Факт", "Нақты"))
plt.bar(positions + 0.18, prediction, width=0.36, label=text("Прогноз", "Болжам"))
plt.xticks(positions, ["1", "2", "3 (metro)", "4"])
plt.xlabel(text("Поездка test", "Test сапары"))
plt.ylabel(text("Длительность, мин", "Ұзақтығы, мин"))
plt.title(text("Прогноз после предобработки", "Алдын ала өңдеуден кейінгі болжам"))
plt.legend()
plt.tight_layout()
plt.show()
