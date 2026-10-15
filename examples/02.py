def mean(values):
    if not values:
        raise ValueError("Нужен хотя бы один элемент")
    return sum(values) / len(values)

scores = [7, 8, 10, 9]
summary = {"count": len(scores), "mean": mean(scores)}
for key, value in summary.items():
    print(key, value)
