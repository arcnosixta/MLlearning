"""Группы клиентов и проекция PCA. Данные лежат рядом в data.csv."""
import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Попробуй 2, 3 или 4 группы. Номера групп не означают категории людей.
CLUSTERS = 3
LANGUAGE = os.environ.get("IMLEARNING_LANG", "ru")


def text(ru, kk):
    return kk if LANGUAGE == "kk" else ru


data = pd.read_csv("data.csv")
columns = ["visits", "spend", "items", "recency"]
names = [text("Визиты", "Келулер"), text("Траты, усл. ед.", "Шығын, шартты бірлік"),
         text("Товары", "Тауарлар"), text("Дней без покупки", "Сатып алусыз күндер")]
print(text(f"Учебные синтетические клиенты: {len(data)} строк. Первые 5:",
           f"Оқу үшін жасалған клиенттер: {len(data)} жол. Алғашқы 5:"))
print(data[columns].head(5).set_axis(names, axis="columns").to_string(index=False))
# Это описание всего набора без целевой переменной и оценки предсказаний.
scaled = StandardScaler().fit_transform(data[columns])
labels = KMeans(n_clusters=CLUSTERS, random_state=42, n_init=10).fit_predict(scaled)
pca = PCA(n_components=2)
points = pca.fit_transform(scaled)
figure, plot = plt.subplots(figsize=(7, 4), constrained_layout=True)
for group in range(CLUSTERS):
    mask = labels == group
    name = text(f"Группа {group + 1}", f"{group + 1}-топ")
    plot.scatter(points[mask, 0], points[mask, 1], label=f"{name} (n={mask.sum()})")
    print(f"{name}: n={mask.sum()}, " + text("среднее визитов", "келулер орташа мәні")
          + f" = {data.loc[mask, 'visits'].mean():.1f}")
plot.set(xlabel=text("Компонента PCA 1", "PCA 1-компоненті"),
         ylabel=text("Компонента PCA 2", "PCA 2-компоненті"),
         title=text("Похожесть покупок: проекция 4 признаков", "Сатып алу ұқсастығы: 4 белгінің проекциясы"))
print(text("В двух компонентах доля дисперсии", "Екі компоненттегі дисперсия үлесі")
      + f": {pca.explained_variance_ratio_.sum():.1%}")
print(text("PCA сжимает данные; видимые расстояния могут искажаться.",
           "PCA деректерді сығады; көрінетін арақашықтықтар бұрмалануы мүмкін."))
plot.legend()
plt.show()
