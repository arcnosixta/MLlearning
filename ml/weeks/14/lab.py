"""IoU и NMS: убираем повторные рамки одного класса по степени перекрытия."""
import os
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

IOU_THRESHOLD = 0.5  # Попробуй 0.8: две похожие рамки сохранятся.
LANGUAGE = os.environ.get("IMLEARNING_LANG", "ru")


def text(ru, kk):
    return kk if LANGUAGE == "kk" else ru


def iou(a, b):
    # Рамка: [лево, верх, право, низ]. Площадь пересечения / площадь объединения.
    intersection = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    intersection *= max(0, min(a[3], b[3]) - max(a[1], b[1]))
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    return intersection / (area_a + area_b - intersection)


# Учебные кандидаты одного класса: координаты в пикселях и условные оценки.
boxes = [(1, 1, 5, 5), (1.5, 1, 5.5, 5), (6, 2, 9, 5)]
scores = [0.95, 0.85, 0.75]
kept = []
for index in sorted(range(len(boxes)), key=lambda i: scores[i], reverse=True):
    if all(iou(boxes[index], boxes[other]) <= IOU_THRESHOLD for other in kept):
        kept.append(index)

print(text("Учебные рамки одного класса; это не запуск YOLO.",
           "Бір кластың оқу жақтаулары; бұл YOLO іске қосуы емес."))
print(text("Перекрытие IoU рамок 1 и 2:", "1 және 2 жақтауларының IoU қабаттасуы:"),
      f"{iou(boxes[0], boxes[1]):.2f}")
print(text("Порог NMS:", "NMS шегі:"), f"{IOU_THRESHOLD:.2f}")
print(text("Оставлены рамки:", "Сақталған жақтаулар:"),
      ", ".join(str(index + 1) for index in kept))
print(text("Оценки кандидатов заданы вручную; они не являются проверенной вероятностью.",
           "Кандидат бағалары қолмен берілген; олар тексерілген ықтималдық емес."))

fig, axes = plt.subplots(1, 2, figsize=(8, 3.5))
for axis, indices, title in zip(axes, [range(3), kept],
        [text("До NMS", "NMS дейін"), text("После NMS", "NMS кейін")]):
    for index in indices:
        left, top, right, bottom = boxes[index]
        color = ["tab:blue", "tab:orange", "tab:green"][index]
        axis.add_patch(Rectangle((left, top), right - left, bottom - top,
                                 fill=False, edgecolor=color, linewidth=2))
        axis.text(left, top - 0.15, f"{index + 1}: {scores[index]:.2f}", color=color)
    axis.set(xlim=(0, 10), ylim=(7, 0), aspect="equal", title=title,
             xlabel=text("X, пиксели", "X, пиксель"),
             ylabel=text("Y, пиксели", "Y, пиксель"))
fig.tight_layout()
plt.show()