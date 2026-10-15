from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
texts = ["футбол команда гол", "хоккей команда матч", "спорт победа футбол",
         "код программа python", "python данные код", "программа алгоритм данные"]
y = ["спорт"] * 3 + ["код"] * 3
model = make_pipeline(TfidfVectorizer(), LogisticRegression())
model.fit(texts, y)
print(model.predict(["команда футбол", "данные python"]))
print("Vocabulary:", model.named_steps["tfidfvectorizer"].get_feature_names_out())
