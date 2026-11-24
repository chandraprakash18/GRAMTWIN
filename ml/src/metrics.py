"""
GRAMTWIN - Land Cover Segmentation Evaluation Metrics
Calculates IoU, Mean IoU (mIoU), Precision, Recall, F1-score, Pixel Accuracy,
and Confusion Matrix for semantic segmentation.
"""

import numpy as np
import torch

CLASS_NAMES = {
    1: "Agricultural Land",
    2: "Trees / Forest",
    3: "Water Bodies",
    4: "Built-up Areas",
    5: "Bare Soil"
}

def calculate_confusion_matrix(y_pred, y_true, num_classes=6):
    """
    Computes a num_classes x num_classes confusion matrix.
    Rows: Ground Truth, Columns: Predictions.
    """
    mask = (y_true >= 0) & (y_true < num_classes)
    hist = np.bincount(
        num_classes * y_true[mask].astype(int) + y_pred[mask].astype(int),
        minlength=num_classes ** 2
    ).reshape(num_classes, num_classes)
    return hist

def calculate_metrics_from_confusion_matrix(cm, num_classes=6, ignore_index=0):
    """
    Computes IoU, Precision, Recall, F1 per class and macro averages
    from a confusion matrix.
    """
    metrics = {
        "class_metrics": {},
        "macro_avg": {},
        "overall_pixel_accuracy": 0.0,
        "mean_iou": 0.0
    }

    total_correct = 0
    total_samples = 0

    ious = []
    precisions = []
    recalls = []
    f1s = []

    for c in range(1, num_classes):
        tp = cm[c, c]
        fn = np.sum(cm[c, :]) - tp
        fp = np.sum(cm[:, c]) - tp

        union = tp + fp + fn
        iou = float(tp / union) if union > 0 else 0.0

        precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
        recall = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        f1 = float(2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        name = CLASS_NAMES.get(c, f"Class_{c}")
        metrics["class_metrics"][name] = {
            "class_id": c,
            "iou": round(iou, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "total_pixels": int(np.sum(cm[c, :]))
        }

        ious.append(iou)
        precisions.append(precision)
        recalls.append(recall)
        f1s.append(f1)

        total_correct += tp
        total_samples += np.sum(cm[c, :])

    overall_acc = float(total_correct / total_samples) if total_samples > 0 else 0.0
    miou = float(np.mean(ious)) if len(ious) > 0 else 0.0

    metrics["overall_pixel_accuracy"] = round(overall_acc, 4)
    metrics["mean_iou"] = round(miou, 4)
    metrics["macro_avg"] = {
        "precision": round(float(np.mean(precisions)), 4),
        "recall": round(float(np.mean(recalls)), 4),
        "f1_score": round(float(np.mean(f1s)), 4),
        "iou": round(miou, 4)
    }

    # Confusion matrix for classes 1 to 5 (excluding background)
    sub_cm = cm[1:num_classes, 1:num_classes]
    metrics["confusion_matrix"] = sub_cm.tolist()
    metrics["classes"] = [CLASS_NAMES[i] for i in range(1, num_classes)]

    return metrics
