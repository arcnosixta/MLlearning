"""EDA: проверяем небольшую таблицу ожидания на остановках."""
import os
import pandas as pd
import matplotlib.pyplot as plt

LANGUAGE = os.environ.get("IMLEARNING_LANG", "ru")


def text(ru, kk):
    return kk if LANGUAGE == "kk" else ru


# Учебные наблюдения, не реальные данные транспортной службы.
data = pd.DataFrame({
    "stop": ["A"] * 5 + ["B"] * 5 + ["C"] * 5,
    "delay": [0, 1, 2, 3, 4, 1, 2, 3, 4, 6, 0, 1, 3, 5, 10],
    "wait": [3, 4, 5, 7, 8, 4, 6, 7, 8, 10, 2, 3, 6, 9, 24],
})
# Измени ожидание 24: как изменятся среднее и медиана?
print(text("Наблюдений:", "Бақылаулар:"), len(data))
print(text("Пропусков:", "Бос мәндер:"), int(data.isna().sum().sum()))
print(text("Среднее ожидание, мин:", "Орташа күту, мин:"), f"{data['wait'].mean():.1f}")
print(text("Медиана ожидания, мин:", "Күту медианасы, мин:"), f"{data['wait'].median():.1f}")
summary = data.groupby("stop")["wait"].agg(["count", "median"])
print(summary.rename(columns={"count": text("Число", "Саны"),
                              "median": text("Медиана, мин", "Медиана, мин")})
      .rename_axis(text("Остановка", "Аялдама")).to_string())
print(text("По 5 наблюдений на остановку: выводы предварительные.",
           "Әр аялдамада 5 бақылау: қорытындылар алдын ала."))

plt.figure(figsize=(7, 4))
plt.hist(data["wait"], bins=[0, 5, 10, 15, 20, 25], edgecolor="white")
plt.xlabel(text("Время ожидания, мин", "Күту уақыты, мин"))
plt.ylabel(text("Число наблюдений", "Бақылаулар саны"))
plt.title(text("Распределение ожидания", "Күту уақытының таралуы"))
plt.tight_layout()
plt.show()

plt.figure(figsize=(7, 4))
for stop, group in data.groupby("stop"):
    plt.scatter(group["delay"], group["wait"], label=text("Остановка ", "Аялдама ") + stop)
plt.xlabel(text("Задержка автобуса, мин", "Автобустың кешігуі, мин"))
plt.ylabel(text("Время ожидания, мин", "Күту уақыты, мин"))
plt.title(text("Связь не доказывает причину", "Байланыс себепті дәлелдемейді"))
plt.legend()
plt.tight_layout()
plt.show()
