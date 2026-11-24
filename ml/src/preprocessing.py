"""
GRAMTWIN - Preprocessing and Dataset Preparation
Extracts normalized spatial patches from satellite scenes to build
training, validation, and testing sets with geographic separation.
"""

import os
from pathlib import Path
import numpy as np
import cv2

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_SAT_DIR = BASE_DIR / "backend" / "data" / "satellite_imagery"
DATASET_DIR = BASE_DIR / "ml" / "datasets" / "processed"

def extract_patches_from_scene(rgb_or_bands, mask, patch_size=128, stride=64):
    """
    Extracts overlapping patches from a satellite scene and mask.
    rgb_or_bands: (H, W, C)
    mask: (H, W)
    """
    h, w, c = rgb_or_bands.shape
    patches_x = []
    patches_y = []

    for y in range(0, h - patch_size + 1, stride):
        for x in range(0, w - patch_size + 1, stride):
            patch_img = rgb_or_bands[y:y+patch_size, x:x+patch_size]
            patch_mask = mask[y:y+patch_size, x:x+patch_size]
            patches_x.append(patch_img)
            patches_y.append(patch_mask)

    return np.array(patches_x, dtype=np.float32), np.array(patches_y, dtype=np.int64)

def prepare_landcover_dataset(patch_size=128, stride=64):
    """
    Prepares training, validation, and test datasets from the multi-temporal village scenes.
    Geographically separated splits:
    - Train: Hiware Bazar (T1, T2) + Ralegan Siddhi (T1) + Pothanikkad (T1)
    - Val: Ralegan Siddhi (T2) + Piplantri (T1)
    - Test: Piplantri (T2) + Pothanikkad (T2)
    This strictly prevents spatial data leakage across geographic locations.
    """
    DATASET_DIR.mkdir(parents=True, exist_ok=True)

    splits = {
        "train": [
            ("hiware_bazar", "t1"),
            ("hiware_bazar", "t2"),
            ("ralegan_siddhi", "t1"),
            ("pothanikkad", "t1")
        ],
        "val": [
            ("ralegan_siddhi", "t2"),
            ("piplantri", "t1")
        ],
        "test": [
            ("piplantri", "t2"),
            ("pothanikkad", "t2")
        ]
    }

    dataset_summary = {}

    for split_name, scene_list in splits.items():
        all_x = []
        all_y = []

        for v_id, t_tag in scene_list:
            v_dir = RAW_SAT_DIR / v_id
            npz_file = v_dir / f"{t_tag}_bands.npz"
            if not npz_file.exists():
                continue

            data = np.load(str(npz_file))
            bands = data["bands"] # (6, H, W)
            mask = data["mask"]   # (H, W)

            # Use RGB normalized channels: Red (B4, idx 2), Green (B3, idx 1), Blue (B2, idx 0)
            # Transpose to (H, W, 3)
            rgb = np.stack([bands[2], bands[1], bands[0]], axis=-1).astype(np.float32)

            # Normalize [0, 1]
            p2, p98 = np.percentile(rgb, (2, 98))
            rgb_norm = np.clip((rgb - p2) / (p98 - p2 + 1e-6), 0.0, 1.0)

            px, py = extract_patches_from_scene(rgb_norm, mask, patch_size=patch_size, stride=stride)
            all_x.append(px)
            all_y.append(py)

        concat_x = np.concatenate(all_x, axis=0)
        concat_y = np.concatenate(all_y, axis=0)

        out_path = DATASET_DIR / f"{split_name}.npz"
        np.savez_compressed(str(out_path), images=concat_x, masks=concat_y)
        dataset_summary[split_name] = {
            "num_patches": len(concat_x),
            "patch_shape": list(concat_x[0].shape),
            "scenes": [f"{s[0]}_{s[1]}" for s in scene_list]
        }
        print(f"Created {split_name} split with {len(concat_x)} patches of shape {concat_x[0].shape}.")

    return dataset_summary
