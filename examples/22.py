from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score
y = [0, 0, 0, 0, 1, 1, 1, 1]
p = [0.1, 0.2, 0.6, 0.4, 0.3, 0.7, 0.8, 0.9]
for threshold in [0.5, 0.75]:
    pred = [int(v >= threshold) for v in p]
    print("Threshold:", threshold)
    print(confusion_matrix(y, pred, labels=[0, 1]))
    print("P/R/F1:", precision_score(y, pred, zero_division=0),
          recall_score(y, pred, zero_division=0), f1_score(y, pred, zero_division=0))
