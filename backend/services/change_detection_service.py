"""
GRAMTWIN - Temporal Change Detection Service
Compares multi-temporal satellite imagery (Time T1 vs Time T2),
calculates NDVI difference, classifies vegetation gain/loss,
detects built-up expansion, and computes geospatial land area metrics.
"""

import json
from pathlib import Path
import cv2
import numpy as np

from backend.services.cv_pipeline import (
    apply_noise_reduction,
    align_images_ecc,
    generate_ndvi_colormap,
    encode_image_base64
)
from backend.services.vegetation_service import load_village_spectral_data, compute_spectral_index
from backend.services.landcover_service import get_predictor

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "backend" / "data" / "satellite_imagery"

def analyze_temporal_changes(village_id: str = "hiware_bazar"):
    """
    Performs complete satellite comparison between Time T1 (2025-10-15) and Time T2 (2026-10-18).
    """
    # 1. Load multi-spectral data for T1 and T2
    bands_t1, mask_t1_gt, meta_t1 = load_village_spectral_data(village_id, "t1")
    bands_t2, mask_t2_gt, meta_t2 = load_village_spectral_data(village_id, "t2")

    # Spectral bands: B2 (0), B3 (1), B4 (2), B5 (3), B8 (4), B11 (5)
    red_t1 = apply_noise_reduction(bands_t1[2])
    nir_t1 = apply_noise_reduction(bands_t1[4])

    red_t2 = apply_noise_reduction(bands_t2[2])
    nir_t2 = apply_noise_reduction(bands_t2[4])

    # Geographic alignment check using OpenCV ECC
    aligned_red_t2, _ = align_images_ecc(red_t1, red_t2)
    aligned_nir_t2, _ = align_images_ecc(nir_t1, nir_t2)

    # 2. Compute NDVI at T1 and T2
    ndvi_t1 = compute_spectral_index(nir_t1, red_t1)
    ndvi_t2 = compute_spectral_index(aligned_nir_t2, aligned_red_t2)

    # 3. NDVI Difference: NDVI(T2) - NDVI(T1)
    ndvi_diff = ndvi_t2 - ndvi_t1

    h, w = ndvi_diff.shape
    pixel_area_ha = (meta_t1.get("pixel_size_m", 10.0) ** 2) / 10000.0
    total_pixels = h * w
    total_area_ha = round(float(total_pixels * pixel_area_ha), 2)

    # 4. Classify changes:
    # Significant vegetation increase (NDVI change >= +0.25)
    # Moderate vegetation increase (+0.10 <= NDVI change < +0.25)
    # Stable vegetation (-0.10 <= NDVI change < +0.10)
    # Moderate vegetation decrease (-0.25 < NDVI change <= -0.10)
    # Significant vegetation decrease (NDVI change <= -0.25)

    sig_inc = (ndvi_diff >= 0.25)
    mod_inc = (ndvi_diff >= 0.10) & (ndvi_diff < 0.25)
    stable = (ndvi_diff > -0.10) & (ndvi_diff < 0.10)
    mod_dec = (ndvi_diff <= -0.10) & (ndvi_diff > -0.25)
    sig_dec = (ndvi_diff <= -0.25)

    # Physical Area Counts
    n_sig_inc = int(np.sum(sig_inc))
    n_mod_inc = int(np.sum(mod_inc))
    n_stable = int(np.sum(stable))
    n_mod_dec = int(np.sum(mod_dec))
    n_sig_dec = int(np.sum(sig_dec))

    total_gain_px = n_sig_inc + n_mod_inc
    total_loss_px = n_sig_dec + n_mod_dec

    veg_gain_ha = round(float(total_gain_px * pixel_area_ha), 2)
    veg_loss_ha = round(float(total_loss_px * pixel_area_ha), 2)
    net_change_ha = round(float(veg_gain_ha - veg_loss_ha), 2)

    veg_gain_pct = round(float(total_gain_px / total_pixels) * 100, 2)
    veg_loss_pct = round(float(total_loss_px / total_pixels) * 100, 2)
    net_change_pct = round(float((total_gain_px - total_loss_px) / total_pixels) * 100, 2)

    # T1 and T2 baseline vegetation area (NDVI >= 0.30)
    veg_t1_px = int(np.sum(ndvi_t1 >= 0.30))
    veg_t2_px = int(np.sum(ndvi_t2 >= 0.30))
    veg_t1_ha = round(float(veg_t1_px * pixel_area_ha), 2)
    veg_t2_ha = round(float(veg_t2_px * pixel_area_ha), 2)
    veg_t1_pct = round(float(veg_t1_px / total_pixels) * 100, 2)
    veg_t2_pct = round(float(veg_t2_px / total_pixels) * 100, 2)

    # 5. Land Cover Model Inference for Built-up Expansion
    v_dir = DATA_DIR / village_id
    if not v_dir.exists():
        v_dir = DATA_DIR / "hiware_bazar"

    rgb_t1 = cv2.imread(str(v_dir / "t1_rgb.png"))
    rgb_t2 = cv2.imread(str(v_dir / "t2_rgb.png"))

    predictor = get_predictor()
    pred_t1 = predictor.predict(cv2.cvtColor(rgb_t1, cv2.COLOR_BGR2RGB))
    pred_t2 = predictor.predict(cv2.cvtColor(rgb_t2, cv2.COLOR_BGR2RGB))

    mask_t1 = pred_t1["mask"]
    mask_t2 = pred_t2["mask"]

    # Built-up expansion: where T1 was NOT built-up (class != 4) and T2 IS built-up (class == 4)
    builtup_expansion = (mask_t1 != 4) & (mask_t2 == 4)
    builtup_increase_px = int(np.sum(builtup_expansion))
    builtup_increase_ha = round(float(builtup_increase_px * pixel_area_ha), 2)
    builtup_increase_pct = round(float(builtup_increase_px / total_pixels) * 100, 2)

    # 6. Generate Colored Difference Maps & Overlays
    # Difference map (BGRA)
    diff_overlay = np.zeros((h, w, 4), dtype=np.uint8)
    diff_overlay[sig_inc] = [21, 128, 61, 230]      # Deep Green
    diff_overlay[mod_inc] = [34, 197, 94, 220]      # Light Green
    diff_overlay[stable] = [8, 179, 234, 160]       # Yellow
    diff_overlay[mod_dec] = [22, 115, 249, 220]     # Orange
    diff_overlay[sig_dec] = [68, 68, 239, 240]      # Red

    # Gain-only map overlay
    gain_overlay = np.zeros((h, w, 4), dtype=np.uint8)
    gain_overlay[sig_inc] = [21, 128, 61, 235]
    gain_overlay[mod_inc] = [34, 197, 94, 220]

    # Loss-only map overlay
    loss_overlay = np.zeros((h, w, 4), dtype=np.uint8)
    loss_overlay[sig_dec] = [68, 68, 239, 240]
    loss_overlay[mod_dec] = [22, 115, 249, 220]

    # Built-up change map overlay (Magenta/Rose: #e11d48)
    builtup_overlay = np.zeros((h, w, 4), dtype=np.uint8)
    builtup_overlay[builtup_expansion] = [72, 29, 225, 240]

    # NDVI T1 and T2 colormaps
    ndvi_t1_bgra = generate_ndvi_colormap(ndvi_t1)
    ndvi_t2_bgra = generate_ndvi_colormap(ndvi_t2)

    categories = [
        {"name": "Significant Vegetation Increase", "range": ">= +0.25", "color": "#15803d", "pixels": n_sig_inc, "area_ha": round(float(n_sig_inc * pixel_area_ha), 2), "percentage": round(float(n_sig_inc / total_pixels) * 100, 2)},
        {"name": "Moderate Vegetation Increase", "range": "+0.10 to +0.25", "color": "#22c55e", "pixels": n_mod_inc, "area_ha": round(float(n_mod_inc * pixel_area_ha), 2), "percentage": round(float(n_mod_inc / total_pixels) * 100, 2)},
        {"name": "Relatively Stable Vegetation", "range": "-0.10 to +0.10", "color": "#eab308", "pixels": n_stable, "area_ha": round(float(n_stable * pixel_area_ha), 2), "percentage": round(float(n_stable / total_pixels) * 100, 2)},
        {"name": "Moderate Vegetation Decrease", "range": "-0.25 to -0.10", "color": "#f97316", "pixels": n_mod_dec, "area_ha": round(float(n_mod_dec * pixel_area_ha), 2), "percentage": round(float(n_mod_dec / total_pixels) * 100, 2)},
        {"name": "Significant Vegetation Decrease", "range": "<= -0.25", "color": "#ef4444", "pixels": n_sig_dec, "area_ha": round(float(n_sig_dec * pixel_area_ha), 2), "percentage": round(float(n_sig_dec / total_pixels) * 100, 2)}
    ]

    stats = {
        "total_area_ha": total_area_ha,
        "previous_vegetation_ha": veg_t1_ha,
        "previous_vegetation_pct": veg_t1_pct,
        "current_vegetation_ha": veg_t2_ha,
        "current_vegetation_pct": veg_t2_pct,
        "vegetation_gain_ha": veg_gain_ha,
        "vegetation_gain_pct": veg_gain_pct,
        "vegetation_loss_ha": veg_loss_ha,
        "vegetation_loss_pct": veg_loss_pct,
        "net_vegetation_change_ha": net_change_ha,
        "net_vegetation_change_pct": net_change_pct,
        "builtup_increase_ha": builtup_increase_ha,
        "builtup_increase_pct": builtup_increase_pct,
        "stable_vegetation_ha": round(float(n_stable * pixel_area_ha), 2),
        "stable_vegetation_pct": round(float(n_stable / total_pixels) * 100, 2),
        "mean_ndvi_t1": round(float(np.mean(ndvi_t1)), 3),
        "mean_ndvi_t2": round(float(np.mean(ndvi_t2)), 3),
        "mean_ndvi_diff": round(float(np.mean(ndvi_diff)), 3)
    }

    return {
        "village_id": village_id,
        "village_name": meta_t1.get("village_name", village_id),
        "t1": {"date": meta_t1.get("date", "2025-10-15"), "satellite": meta_t1.get("satellite")},
        "t2": {"date": meta_t2.get("date", "2026-10-18"), "satellite": meta_t2.get("satellite")},
        "stats": stats,
        "categories": categories,
        "overlays": {
            "t1_rgb": f"data:image/png;base64,{encode_image_base64(rgb_t1)}",
            "t2_rgb": f"data:image/png;base64,{encode_image_base64(rgb_t2)}",
            "t1_ndvi": f"data:image/png;base64,{encode_image_base64(ndvi_t1_bgra)}",
            "t2_ndvi": f"data:image/png;base64,{encode_image_base64(ndvi_t2_bgra)}",
            "ndvi_difference": f"data:image/png;base64,{encode_image_base64(diff_overlay)}",
            "vegetation_gain": f"data:image/png;base64,{encode_image_base64(gain_overlay)}",
            "vegetation_loss": f"data:image/png;base64,{encode_image_base64(loss_overlay)}",
            "builtup_change": f"data:image/png;base64,{encode_image_base64(builtup_overlay)}"
        }
    }
