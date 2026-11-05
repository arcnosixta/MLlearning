"""Inspect bounding-box IoU, non-maximum suppression, and detector metrics."""

import json
from dataclasses import dataclass


@dataclass(frozen=True)
class Detection:
    category: str
    score: float
    box: tuple[int, int, int, int]


def localized(ru, kk):
    return {"ru": ru, "kk": kk}


def series(ru, kk, kind, points):
    return {"label": localized(ru, kk), "kind": kind,
            "points": [[round(x, 4), round(y, 4)] for x, y in points]}


def area(box):
    x1, y1, x2, y2 = box
    return max(0, x2 - x1) * max(0, y2 - y1)


def iou(a, b):
    overlap = area((max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])))
    union = area(a) + area(b) - overlap
    return overlap / union if union else 0.0


def frame(ru, kk, box, *, reference=False):
    x1, y1, x2, y2 = box
    outline = series(ru, kk, "line", [(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)])
    if reference:
        outline['dashed'] = True
    return outline


def overlap_cases():
    target = (1, 1, 5, 5)
    cases = []
    for prediction, ru, kk in (
        ((2, 1, 6, 5), "Сдвиг на 1", "1-ге ығысу"),
        ((3, 1, 7, 5), "Сдвиг на 2", "2-ге ығысу"),
        ((5, 1, 9, 5), "Касание краями", "Жиектердің жанасуы"),
    ):
        value = iou(target, prediction)
        cases.append({
            "label": localized(ru, kk),
            "note": localized(f"IoU = {value:.3f}. Рамки без толщины контура.",
                              f"IoU = {value:.3f}. Жақтау жиегінің қалыңдығы ескерілмейді."),
            "series": [frame("Эталон", "Шын жақтау", target, reference=True), frame("Прогноз", "Болжам", prediction)],
        })
    return cases


def nms(detections, threshold):
    kept = []
    for candidate in sorted(detections, key=lambda item: item.score, reverse=True):
        if any(item.category == candidate.category and iou(item.box, candidate.box) > threshold
               for item in kept):
            continue
        kept.append(candidate)
    return kept


def nms_cases(truth, predictions):
    scene = [prediction for prediction in predictions if prediction.score >= 0.25]
    cases = []
    for threshold, ru, kk in (
        (None, "До NMS", "NMS алдында"), (0.4, "IoU NMS 0,40", "NMS IoU 0,40"),
        (0.8, "IoU NMS 0,80", "NMS IoU 0,80"),
    ):
        selected = scene if threshold is None else nms(scene, threshold)
        shapes = [frame(f"Эталон {i}", f"{i}-шын жақтау", item.box, reference=True)
                  for i, item in enumerate(truth, 1)]
        shapes.extend(frame(f"{p.category}, {p.score:.2f}", f"{p.category}, {p.score:.2f}", p.box)
                      for p in selected)
        cases.append({
            "label": localized(ru, kk),
            "note": localized(f"Осталось {len(selected)} из {len(scene)} прогнозов при confidence ≥ 0,25.",
                              f"Confidence ≥ 0,25 кезінде {len(scene)} болжамның {len(selected)}-і қалды."),
            "series": shapes,
        })
    return cases


def precision_recall(truth, predictions, min_iou):
    used = set()
    hits = 0
    for p in sorted(predictions, key=lambda item: item.score, reverse=True):
        candidates = [(iou(t.box, p.box), i) for i, t in enumerate(truth)
                      if i not in used and t.category == p.category]
        overlap, index = max(candidates, default=(0, -1))
        if index >= 0 and overlap >= min_iou:
            used.add(index)
            hits += 1
    false_positives = len(predictions) - hits
    misses = len(truth) - hits
    return hits, false_positives, misses


def threshold_cases(truth, predictions):
    candidates = nms(predictions, 0.40)
    cases = []
    for confidence in (0.25, 0.60, 0.85):
        selected = [item for item in candidates if item.score >= confidence]
        hits, false_positives, misses = precision_recall(truth, selected, 0.50)
        precision = hits / len(selected) if selected else 0.0
        recall = hits / len(truth)
        cases.append({
            "label": localized(f"Confidence ≥ {confidence:.2f}", f"Confidence ≥ {confidence:.2f}"),
            "note": localized(f"При IoU оценки ≥ 0,50: TP={hits}, FP={false_positives}, FN={misses}.",
                              f"Бағалау IoU ≥ 0,50 кезінде: TP={hits}, FP={false_positives}, FN={misses}."),
            "series": [series("Доля", "Үлес", "bar", [(1, precision), (2, recall)])],
            "xTicks": [{"value": i, "label": localized(label, label)}
                       for i, label in enumerate(("Precision", "Recall"), 1)],
        })
    return cases


def main():
    truth = [Detection("box", 1, (1, 2, 5, 6)), Detection("box", 1, (7, 3, 10, 7)),
             Detection("bottle", 1, (4, 7, 6, 11))]
    predictions = [
        Detection("box", 0.94, (1, 2, 5, 6)), Detection("box", 0.82, (2, 2, 6, 6)),
        Detection("box", 0.72, (7, 3, 10, 8)), Detection("box", 0.66, (4, 7, 6, 11)),
        Detection("bottle", 0.55, (4, 8, 6, 11)), Detection("box", 0.51, (7, 3, 10, 9)),
        Detection("box", 0.32, (7, 0, 9, 2)),
    ]
    results = [overlap_cases(), nms_cases(truth, predictions), threshold_cases(truth, predictions)]
    print(json.dumps({"topics": results}, ensure_ascii=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
