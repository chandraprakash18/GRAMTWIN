"""
GRAMTWIN - Model Evaluation Script
Evaluates the trained checkpoint on the held-out test split,
computes precision, recall, F1, IoU per class, macro-average, and confusion matrix.
"""

import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import numpy as np
import torch
import matplotlib.pyplot as plt

from ml.src.unet import UNet
from ml.src.data_loader import get_dataloaders
from ml.src.metrics import calculate_confusion_matrix, calculate_metrics_from_confusion_matrix, CLASS_NAMES
CHECKPOINT_PATH = BASE_DIR / "ml" / "models" / "checkpoints" / "best_unet_landcover.pth"
DATASET_DIR = BASE_DIR / "ml" / "datasets" / "processed"
EVAL_DIR = BASE_DIR / "ml" / "outputs" / "evaluation"
EVAL_DIR.mkdir(parents=True, exist_ok=True)

def evaluate_test_set():
    if not CHECKPOINT_PATH.exists():
        raise FileNotFoundError(f"Checkpoint not found at {CHECKPOINT_PATH}. Run train.py first.")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Loading checkpoint from {CHECKPOINT_PATH} on {device}...")

    checkpoint = torch.load(str(CHECKPOINT_PATH), map_location=device, weights_only=False)
    model = UNet(in_channels=3, num_classes=6, base_channels=32).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    _, _, test_loader = get_dataloaders(DATASET_DIR, batch_size=8)
    all_preds = []
    all_targets = []

    with torch.no_grad():
        for images, masks in test_loader:
            images = images.to(device)
            outputs = model(images)
            preds = torch.argmax(outputs, dim=1).cpu().numpy()
            all_preds.append(preds.flatten())
            all_targets.append(masks.numpy().flatten())

    y_pred = np.concatenate(all_preds)
    y_true = np.concatenate(all_targets)

    cm = calculate_confusion_matrix(y_pred, y_true, num_classes=6)
    results = calculate_metrics_from_confusion_matrix(cm, num_classes=6)

    # Save JSON report
    out_json = EVAL_DIR / "evaluation_metrics.json"
    out_json.write_text(json.dumps(results, indent=2))
    print(f"Saved evaluation metrics to {out_json.name}")

    # Plot Confusion Matrix
    classes = results["classes"]
    cm_matrix = np.array(results["confusion_matrix"])

    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(cm_matrix, interpolation='nearest', cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax)
    ax.set(xticks=np.arange(cm_matrix.shape[1]),
           yticks=np.arange(cm_matrix.shape[0]),
           xticklabels=classes, yticklabels=classes,
           title="Test Set Confusion Matrix - Land Cover Classes",
           ylabel='True label',
           xlabel='Predicted label')

    plt.setp(ax.get_xticklabels(), rotation=30, ha="right", rotation_mode="anchor")

    # Loop over data dimensions and create text annotations
    thresh = cm_matrix.max() / 2.
    for i in range(cm_matrix.shape[0]):
        for j in range(cm_matrix.shape[1]):
            val = int(cm_matrix[i, j])
            ax.text(j, i, f"{val:,}",
                    ha="center", va="center",
                    color="white" if cm_matrix[i, j] > thresh else "black",
                    fontsize=8)
    fig.tight_layout()
    plt.savefig(str(EVAL_DIR / "confusion_matrix.png"), dpi=150)
    plt.close()

    print("\n--- Test Evaluation Summary ---")
    print(f"Overall Accuracy: {results['overall_pixel_accuracy']*100:.2f}%")
    print(f"Mean IoU (mIoU):  {results['mean_iou']:.4f}")
    print(f"Macro F1-Score:   {results['macro_avg']['f1_score']:.4f}")
    print(f"Macro Precision:  {results['macro_avg']['precision']:.4f}")
    print(f"Macro Recall:     {results['macro_avg']['recall']:.4f}")
    print("\nPer-Class Breakdown:")
    for cname, cstat in results["class_metrics"].items():
        print(f"  - {cname:18s} | IoU: {cstat['iou']:.4f} | F1: {cstat['f1_score']:.4f} | Prec: {cstat['precision']:.4f} | Rec: {cstat['recall']:.4f}")

    return results

if __name__ == "__main__":
    evaluate_test_set()
