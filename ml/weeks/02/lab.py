"""Читаем маленький CSV, очищаем заказы и строим сводку pandas."""
import os
from io import StringIO
import pandas as pd
import matplotlib.pyplot as plt

LANGUAGE = os.environ.get("IMLEARNING_LANG", "ru")


def text(ru, kk):
    return kk if LANGUAGE == "kk" else ru


# Вымышленные заказы. Измени сумму или добавь строку с новым order_id.
CSV = """order_id,zone,total
1,A,1200
2,B,1800
3,A,1500
3,A,1500
4,B,?
5,B,2200
6,A,1700
"""
orders = pd.read_csv(StringIO(CSV))
orders["total"] = pd.to_numeric(orders["total"], errors="coerce")
duplicates = orders.duplicated(subset="order_id").sum()
orders = orders.drop_duplicates(subset="order_id")
missing = orders["total"].isna().sum()
# Без суммы нельзя считать выручку: исключаем строку, не подставляем ноль.
clean = orders.dropna(subset=["total"])
summary = clean.groupby("zone")["total"].agg(["count", "sum"])

print(text("Синтетические заказы: суммы в тенге.", "Жасанды тапсырыстар: сомалар теңгемен."))
print(text("Повторов удалено:", "Жойылған қайталаулар:"), duplicates)
print(text("Заказов без суммы исключено:", "Сомасыз алынып тасталған тапсырыстар:"), missing)
print(text("Очищенная таблица:", "Тазартылған кесте:"))
print(clean.rename(columns={"order_id": text("Заказ", "Тапсырыс"),
                            "zone": text("Зона", "Аймақ"),
                            "total": text("Сумма, ₸", "Сома, ₸")}).to_string(index=False))
print(text("Выручка относится только к заказам с известной суммой.",
           "Түсім тек сомасы белгілі тапсырыстарға қатысты."))

plt.figure(figsize=(7, 4))
labels = [text("Зона ", "Аймақ ") + zone for zone in summary.index]
plt.bar(labels, summary["sum"], color=["#2563eb", "#ea580c"])
plt.ylabel(text("Выручка известных заказов, ₸", "Белгілі тапсырыстар түсімі, ₸"))
plt.title(text("Сводка после очистки", "Тазартудан кейінгі қорытынды"))
plt.tight_layout()
plt.show()
