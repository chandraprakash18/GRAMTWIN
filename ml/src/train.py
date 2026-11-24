"""
GRAMTWIN - Land Cover Model Training Pipeline
Trains U-Net on satellite imagery using Combined CrossEntropy + Dice Loss.
Evaluates validation metrics, performs checkpointing, and logs training history.
"""

import os
import sys
import json
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt

from ml.src.unet import UNet
from ml.src.data_loader import get_dataloaders
from ml.src.preprocessing import prepare_landcover_dataset
from ml.src.metrics import calculate_confusion_matrix, calculate_metrics_from_confusion_matrix
CHECKPOINT_DIR = BASE_DIR / "ml" / "models" / "checkpoints"
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR = BASE_DIR / "ml" / "outputs" / "training_history"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DATASET_DIR = BASE_DIR / "ml" / "datasets" / "processed"

class DiceLoss(nn.Module):
    def __init__(self, num_classes=6, smooth=1e-5):
        super().__init__()
        self.num_classes = num_classes
        self.smooth = smooth

    def forward(self, logits, targets):
        probs = torch.softmax(logits, dim=1)
        # One-hot encode targets
        targets_onehot = torch.zeros_like(probs).scatter_(1, targets.unsqueeze(1), 1)

        dice_per_class = []
        for c in range(1, self.num_classes): # Ignore class 0
            p = probs[:, c, :, :]
            t = targets_onehot[:, c, :, :]
            intersection = torch.sum(p * t)
            cardinality = torch.sum(p + t)
            dice = (2.0 * intersection + self.smooth) / (cardinality + self.smooth)
            dice_per_class.append(dice)

        return 1.0 - torch.mean(torch.stack(dice_per_class))

def train_epoch(model, dataloader, optimizer, criterion_ce, criterion_dice, device):
    model.train()
    running_loss = 0.0
    total_batches = 0

    for images, masks in dataloader:
        images = images.to(device)
        masks = masks.to(device)

        optimizer.zero_grad()
        outputs = model(images)

        loss_ce = criterion_ce(outputs, masks)
        loss_dice = criterion_dice(outputs, masks)
        loss = 0.6 * loss_ce + 0.4 * loss_dice

        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        total_batches += 1

    return running_loss / max(1, total_batches)

def validate(model, dataloader, criterion_ce, criterion_dice, device, num_classes=6):
    model.eval()
    running_loss = 0.0
    total_batches = 0
    all_preds = []
    all_targets = []

    with torch.no_grad():
        for images, masks in dataloader:
            images = images.to(device)
            masks = masks.to(device)

            outputs = model(images)
            loss_ce = criterion_ce(outputs, masks)
            loss_dice = criterion_dice(outputs, masks)
            loss = 0.6 * loss_ce + 0.4 * loss_dice
            running_loss += loss.item()
            total_batches += 1

            preds = torch.argmax(outputs, dim=1).cpu().numpy()
            all_preds.append(preds.flatten())
            all_targets.append(masks.cpu().numpy().flatten())

    val_loss = running_loss / max(1, total_batches)
    y_pred = np.concatenate(all_preds)
    y_true = np.concatenate(all_targets)

    cm = calculate_confusion_matrix(y_pred, y_true, num_classes=num_classes)
    metrics = calculate_metrics_from_confusion_matrix(cm, num_classes=num_classes)
    metrics["val_loss"] = round(val_loss, 4)

    return metrics

def run_training(epochs=12, batch_size=8, lr=0.001):
    print("="*60)
    print("GRAMTWIN - Starting U-Net Land Cover Segmentation Training")
    print("="*60)

    # 1. Check if dataset exists or prepare it
    if not (DATASET_DIR / "train.npz").exists():
        print("Preparing geographically separated patch dataset...")
        prepare_landcover_dataset(patch_size=128, stride=64)

    # 2. Setup Device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Executing on hardware device: {device}")

    # 3. DataLoaders
    train_loader, val_loader, test_loader = get_dataloaders(DATASET_DIR, batch_size=batch_size)
    print(f"Train batches: {len(train_loader)} | Val batches: {len(val_loader)} | Test batches: {len(test_loader)}")

    # 4. Initialize Model
    model = UNet(in_channels=3, num_classes=6, base_channels=32).to(device)
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    criterion_ce = nn.CrossEntropyLoss()
    criterion_dice = DiceLoss(num_classes=6)

    best_miou = 0.0
    history = {
        "epoch": [],
        "train_loss": [],
        "val_loss": [],
        "val_accuracy": [],
        "val_miou": [],
        "val_f1": []
    }

    start_time = time.time()

    for ep in range(1, epochs + 1):
        t0 = time.time()
        tr_loss = train_epoch(model, train_loader, optimizer, criterion_ce, criterion_dice, device)
        scheduler.step()

        val_metrics = validate(model, val_loader, criterion_ce, criterion_dice, device, num_classes=6)
        v_loss = val_metrics["val_loss"]
        v_acc = val_metrics["overall_pixel_accuracy"]
        v_miou = val_metrics["mean_iou"]
        v_f1 = val_metrics["macro_avg"]["f1_score"]
        ep_duration = round(time.time() - t0, 2)

        history["epoch"].append(ep)
        history["train_loss"].append(round(tr_loss, 4))
        history["val_loss"].append(v_loss)
        history["val_accuracy"].append(v_acc)
        history["val_miou"].append(v_miou)
        history["val_f1"].append(v_f1)

        print(f"Epoch [{ep:02d}/{epochs:02d}] ({ep_duration}s) | Train Loss: {tr_loss:.4f} | Val Loss: {v_loss:.4f} | Val Acc: {v_acc*100:.2f}% | mIoU: {v_miou:.4f} | F1: {v_f1:.4f}")

        # Checkpoint saving
        if v_miou > best_miou:
            best_miou = v_miou
            checkpoint_path = CHECKPOINT_DIR / "best_unet_landcover.pth"
            torch.save({
                "epoch": ep,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_miou": best_miou,
                "val_metrics": val_metrics,
                "in_channels": 3,
                "num_classes": 6
            }, str(checkpoint_path))
            print(f"  -> Best model checkpoint saved to {checkpoint_path.name} (mIoU: {best_miou:.4f})")

    total_duration = round(time.time() - start_time, 2)
    print(f"\nTraining completed in {total_duration}s. Best validation mIoU: {best_miou:.4f}")

    # Save training history JSON
    history_file = OUTPUT_DIR / "history.json"
    history_file.write_text(json.dumps(history, indent=2))

    # Plot loss and accuracy curves
    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    plt.plot(history["epoch"], history["train_loss"], label="Train Loss", color="#ef4444", lw=2)
    plt.plot(history["epoch"], history["val_loss"], label="Val Loss", color="#f97316", lw=2)
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title("Training & Validation Loss")
    plt.grid(True, alpha=0.3)
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(history["epoch"], history["val_accuracy"], label="Pixel Accuracy", color="#3b82f6", lw=2)
    plt.plot(history["epoch"], history["val_miou"], label="Mean IoU", color="#10b981", lw=2)
    plt.xlabel("Epoch")
    plt.ylabel("Score")
    plt.title("Validation Accuracy & mIoU")
    plt.grid(True, alpha=0.3)
    plt.legend()

    plt.tight_layout()
    plt.savefig(str(OUTPUT_DIR / "training_curves.png"), dpi=150)
    plt.close()

    return best_miou, history

if __name__ == "__main__":
    run_training(epochs=8, batch_size=8, lr=0.001)
