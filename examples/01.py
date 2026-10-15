areas = [30, 45, 60, 75]
prices = [60, 90, 120, 150]  # условные единицы
# Учебная модель с нулевым свободным членом: y = weight * x
weight = sum(x*y for x, y in zip(areas, prices)) / sum(x*x for x in areas)
print("Цена для 50 м²:", weight * 50)
