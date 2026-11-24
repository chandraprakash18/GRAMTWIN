"""
GRAMTWIN - PyTorch Dataset & DataLoader
Provides fast, augmented mini-batch loading for semantic segmentation training.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader

from ml.src.augmentation import SatelliteAugmentation

class SatelliteSegmentationDataset(Dataset):
    def __init__(self, npz_path, augment=False):
        data = np.load(str(npz_path))
        self.images = data["images"] # (N, H, W, 3) float32 in [0, 1]
        self.masks = data["masks"]   # (N, H, W) int64 in [0, 5]
        self.augment = SatelliteAugmentation() if augment else None

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img = self.images[idx].copy()
        mask = self.masks[idx].copy()

        if self.augment:
            img, mask = self.augment(img, mask)

        # Convert to PyTorch tensors
        # PyTorch expects (C, H, W) for image, (H, W) for mask
        img_t = torch.from_numpy(img).permute(2, 0, 1).float()
        mask_t = torch.from_numpy(mask).long()

        return img_t, mask_t

def get_dataloaders(dataset_dir, batch_size=8, num_workers=0):
    dataset_dir = Path(dataset_dir)
    train_ds = SatelliteSegmentationDataset(dataset_dir / "train.npz", augment=True)
    val_ds = SatelliteSegmentationDataset(dataset_dir / "val.npz", augment=False)
    test_ds = SatelliteSegmentationDataset(dataset_dir / "test.npz", augment=False)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers)

    return train_loader, val_loader, test_loader
