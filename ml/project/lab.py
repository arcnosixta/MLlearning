"""Reproduce the ML 3305 capstone on the bundled synthetic dataset."""

import csv
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

DATA = Path(__file__).with_name('data.csv')
FEATURES = ('days_active', 'tickets', 'monthly_fee')


def split():
    with DATA.open(encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream))
    x = np.array([[float(row[key]) for key in FEATURES] for row in rows])
    y = np.array([int(row['churn']) for row in rows])
    x_dev, x_test, y_dev, y_test = train_test_split(x, y, test_size=.2, stratify=y, random_state=42)
    x_train, x_valid, y_train, y_valid = train_test_split(x_dev, y_dev, test_size=.25, stratify=y_dev, random_state=43)
    return x_train, x_valid, x_test, y_train, y_valid, y_test


def pipeline(c=1):
    return make_pipeline(StandardScaler(), LogisticRegression(C=c, random_state=42))


def train():
    x_train, _, _, y_train, _, _ = split()
    return pipeline().fit(x_train, y_train)


def label(ru, kk):
    return {'ru': ru, 'kk': kk}


def bars(name, values):
    return {'label': name, 'kind': 'bar', 'points': [[i + 1, round(float(v), 4)] for i, v in enumerate(values)]}


def experiment(name, note, series, ticks=None):
    result = {'label': name, 'note': note, 'series': [series]}
    if ticks:
        result['xTicks'] = [{'value': i + 1, 'label': label(tick, tick)} for i, tick in enumerate(ticks)]
    return result


def results():
    x_train, x_valid, x_test, y_train, y_valid, y_test = split()
    cv_cases = []
    for c in (.01, 1, 100):
        scores = cross_val_score(pipeline(c), x_train, y_train, scoring='roc_auc', cv=StratifiedKFold(4, shuffle=True, random_state=9))
        cv_cases.append(experiment(label(f'C = {c}', f'C = {c}'),
                                   label(f'Средний ROC-AUC {scores.mean():.3f} на четырёх фолдах.', f'Төрт фолдтағы орташа ROC-AUC {scores.mean():.3f}.'),
                                   bars(label('ROC-AUC на фолде', 'Фолдтағы ROC-AUC'), scores)))
    model = train()
    prob_valid = model.predict_proba(x_valid)[:, 1]
    threshold_cases = []
    for threshold in (.25, .50, .75):
        pred = prob_valid >= threshold
        scores = [metric(y_valid, pred, zero_division=0) for metric in (precision_score, recall_score, f1_score)]
        threshold_cases.append(experiment(label(f'Порог {threshold:.2f}', f'{threshold:.2f} шегі'),
                                          label(f'На валидации положительных прогнозов {pred.sum()} из {len(pred)}.', f'Валидацияда {len(pred)} болжамның {pred.sum()}-і оң.'),
                                          bars(label('Значение метрики', 'Метрика мәні'), scores), ['Precision', 'Recall', 'F1']))
    probes = []
    for offset in (0, 7, 14):
        sample = x_test[offset:offset + 7]
        values = model.predict_proba(sample)[:, 1]
        probes.append(experiment(label(f'Запросы {offset + 1}–{offset + len(sample)}', f'{offset + 1}–{offset + len(sample)} сұрау'),
                                 label(f'Порог зафиксирован на 0.50. Положительных прогнозов {sum(values >= .5)} из {len(values)}.', f'Шек 0.50 болып бекітілді. {len(values)} болжамның {sum(values >= .5)}-і оң.'),
                                 bars(label('Вероятность оттока', 'Кету ықтималдығы'), values)))
    auc = roc_auc_score(y_test, model.predict_proba(x_test)[:, 1])
    baseline = DummyClassifier(strategy='prior').fit(x_train, y_train)
    baseline_auc = roc_auc_score(y_test, baseline.predict_proba(x_test)[:, 1])
    return {'topics': [cv_cases, threshold_cases, probes], 'heldOutAUC': round(float(auc), 4), 'baselineAUC': round(float(baseline_auc), 4)}


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    print(json.dumps(results(), ensure_ascii=False, indent=2, allow_nan=False))
