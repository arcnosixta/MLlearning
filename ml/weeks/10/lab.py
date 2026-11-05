"""Группы клиентов: сравниваем PCA и t-SNE. Данные рядом в data.csv."""
import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler

# Попробуй 2, 3 или 4 группы. Номера групп не означают категории людей.
CLUSTERS = 3
PERPLEXITY = 15  # Масштаб соседства t-SNE: попробуй 5, 15, 30 (меньше числа строк).
LANGUAGE = os.environ.get("IMLEARNING_LANG", "ru")


def text(ru, kk):
    return kk if LANGUAGE == "kk" else ru


data = pd.read_csv("data.csv")
if not 0 < PERPLEXITY < len(data):
    raise ValueError(text(f"PERPLEXITY должна быть больше 0 и меньше {len(data)}.",
                          f"PERPLEXITY 0-ден үлкен, {len(data)} мәнінен кіші болуы керек."))
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
pca_points = pca.fit_transform(scaled)
# Маленький набор позволяет использовать exact без параллельных потоков.
tsne_points = TSNE(n_components=2, perplexity=PERPLEXITY, method="exact",
                   init="pca", learning_rate="auto", max_iter=500,
                   random_state=42, n_jobs=1).fit_transform(scaled)
for group in range(CLUSTERS):
    mask = labels == group
    name = text(f"Группа {group + 1}", f"{group + 1}-топ")
    print(f"{name}: n={mask.sum()}, " + text("среднее визитов", "келулер орташа мәні")
          + f" = {data.loc[mask, 'visits'].mean():.1f}")
print(text("PCA: доля объяснённой дисперсии в 2 компонентах", "PCA: 2 компоненттегі түсіндірілген дисперсия үлесі")
      + f": {pca.explained_variance_ratio_.sum():.1%}")
print(text("PCA сжимает данные; видимые расстояния могут искажаться.",
           "PCA деректерді сығады; көрінетін арақашықтықтар бұрмалануы мүмкін."))
print(f"t-SNE: perplexity={PERPLEXITY}, random_state=42.")
print(text("Цвета — прежние группы KMeans по 4 признакам; t-SNE не создаёт новые группы.",
           "Түстер — 4 белгі бойынша бастапқы KMeans топтары; t-SNE жаңа топ құрмайды."))
print(text("t-SNE показывает локальное соседство, а не надёжные расстояния между облаками.",
           "t-SNE бұлттар арасындағы сенімді қашықтықты емес, жергілікті көршілікті көрсетеді."))

# Одни клиенты и цвета; две разные двумерные визуализации.
for method, points in [("PCA", pca_points), ("t-SNE", tsne_points)]:
    figure, plot = plt.subplots(figsize=(7, 4), constrained_layout=True)
    for group in range(CLUSTERS):
        mask = labels == group
        name = text(f"Группа {group + 1}", f"{group + 1}-топ")
        plot.scatter(points[mask, 0], points[mask, 1], label=f"{name} (n={mask.sum()})")
    plot.set(xlabel=f"{method} 1", ylabel=f"{method} 2", aspect="equal",
             title=text("Покупки: ", "Сатып алулар: ") + method
             + (f", perplexity={PERPLEXITY}" if method == "t-SNE" else ""))
    plot.legend()
plt.show()
