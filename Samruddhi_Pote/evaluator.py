def evaluate_extraction(predicted, ground_truth):
    total = len(ground_truth)
    if total == 0:
        return 0.0

    correct = 0
    used_pred_indexes = set()

    for gt in ground_truth:
        for idx, pred in enumerate(predicted):
            if idx in used_pred_indexes:
                continue
            if gt["name"] == pred["name"] and abs(gt["value"] - pred["value"]) < 0.01:
                correct += 1
                used_pred_indexes.add(idx)
                break

    accuracy = (correct / total) * 100
    return accuracy

def evaluate_classification(predicted, ground_truth):
    total = len(ground_truth)
    if total == 0:
        return 0.0

    correct = 0
    used_pred_indexes = set()

    for gt in ground_truth:
        for idx, pred in enumerate(predicted):
            if idx in used_pred_indexes:
                continue
            if gt["name"] == pred["name"] and gt["status"] == pred["status"]:
                correct += 1
                used_pred_indexes.add(idx)
                break

    accuracy = (correct / total) * 100
    return accuracy
