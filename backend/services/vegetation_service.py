"""
GRAMTWIN - Vegetation Intelligence Service
Handles NDVI, NDRE, NDWI, and SAVI calculations, health classification,
distribution histograms, and OpenCV vegetation stress hotspot mapping.
"""

import json
from pathlib import Path
import numpy as np
import cv2

from backend.services.cv_pipeline import (
    apply_noise_reduction,
    generate_ndvi_colormap,
    generate_health_class_map,
    detect_stress_hotspots_contours,
    encode_image_base64
)

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "backend" / "data" / "satellite_imagery"

def load_village_spectral_data(village_id: str, time_tag: str = "t2"):
    """Loads calibrated Sentinel-2 bands and metadata for a village."""
    v_dir = DATA_DIR / village_id
    if not v_dir.exists():
        # Fallback to Hiware Bazar
        v_dir = DATA_DIR / "hiware_bazar"

    npz_path = v_dir / f"{time_tag}_bands.npz"
    if not npz_path.exists():
        npz_path = v_dir / "t2_bands.npz"

    data = np.load(str(npz_path))
    bands = data["bands"] # (6, H, W): B2, B3, B4, B5, B8, B11
    mask = data["mask"]
    meta = json.loads(str(data["meta"]))

    return bands, mask, meta

def compute_spectral_index(band_a, band_b, c_const=0.0):
    """
    Computes normalized difference index: (band_a - band_b) / (band_a + band_b + c_const)
    Guards against division by zero and invalid floating point values.
    """
    numerator = band_a.astype(np.float32) - band_b.astype(np.float32)
    denominator = band_a.astype(np.float32) + band_b.astype(np.float32) + c_const

    # Safe division
    with np.errstate(divide='ignore', invalid='ignore'):
        index = np.where(denominator != 0, numerator / denominator, 0.0)

    index = np.nan_to_num(index, nan=0.0, posinf=1.0, neginf=-1.0)
    return np.clip(index, -1.0, 1.0)

def compute_vegetation_analysis(village_id: str = "hiware_bazar", time_tag: str = "t2", aoi_bbox: list = None):
    """
    Performs full vegetation intelligence on the selected village imagery.
    Sentinel-2 Bands:
      B2: Blue (idx 0)
      B3: Green (idx 1)
      B4: Red (idx 2)
      B5: Red Edge (idx 3)
      B8: NIR (idx 4)
      B11: SWIR (idx 5)
    """
    bands, landcover_gt, meta = load_village_spectral_data(village_id, time_tag)

    b_blue = apply_noise_reduction(bands[0])
    b_green = apply_noise_reduction(bands[1])
    b_red = apply_noise_reduction(bands[2])
    b_rededge = apply_noise_reduction(bands[3])
    b_nir = apply_noise_reduction(bands[4])
    b_swir = apply_noise_reduction(bands[5])

    # 1. NDVI = (NIR - RED) / (NIR + RED)
    ndvi = compute_spectral_index(b_nir, b_red)

    # 2. NDRE = (NIR - RED_EDGE) / (NIR + RED_EDGE)
    ndre = compute_spectral_index(b_nir, b_rededge)

    # 3. NDWI = (GREEN - NIR) / (GREEN + NIR)
    ndwi = compute_spectral_index(b_green, b_nir)

    # 4. SAVI = ((NIR - RED) / (NIR + RED + L)) * (1 + L) with L = 0.5
    L = 0.5
    savi_raw = ((b_nir - b_red) / (b_nir + b_red + L + 1e-6)) * (1.0 + L)
    savi = np.clip(savi_raw, -1.0, 1.0)

    # If AOI bounding box is passed [min_x_pct, min_y_pct, max_x_pct, max_y_pct]
    h, w = ndvi.shape
    pixel_area_ha = (meta.get("pixel_size_m", 10.0) ** 2) / 10000.0

    if aoi_bbox and len(aoi_bbox) == 4:
        x0, y0, x1, y1 = [int(p) for p in aoi_bbox]
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(w, x1), min(h, y1)
        sub_ndvi = ndvi[y0:y1, x0:x1]
    else:
        sub_ndvi = ndvi

    total_pixels = sub_ndvi.size
    total_area_ha = round(total_pixels * pixel_area_ha, 2)

    # Classification counts and percentages
    v_high = np.sum(sub_ndvi >= 0.66)
    v_med = np.sum((sub_ndvi >= 0.40) & (sub_ndvi < 0.66))
    v_low = np.sum((sub_ndvi >= 0.20) & (sub_ndvi < 0.40))
    v_vlow = np.sum((sub_ndvi >= 0.00) & (sub_ndvi < 0.20))
    v_water = np.sum(sub_ndvi < 0.00)

    # Vegetated area is medium + high + low
    total_veg_pixels = int(v_high + v_med + v_low)
    veg_coverage_pct = round(float(total_veg_pixels / total_pixels) * 100, 2)
    healthy_pct = round(float(v_high / total_pixels) * 100, 2)
    stressed_pct = round(float((v_low + v_vlow) / total_pixels) * 100, 2)
    water_pct = round(float(v_water / total_pixels) * 100, 2)

    categories = [
        {"name": "High Health (0.66–1.00)", "range": "0.66 - 1.00", "color": "#16a34a", "pixels": int(v_high), "area_ha": round(float(v_high * pixel_area_ha), 2), "percentage": round(float(v_high / total_pixels) * 100, 2)},
        {"name": "Medium Health (0.40–0.66)", "range": "0.40 - 0.66", "color": "#84cc16", "pixels": int(v_med), "area_ha": round(float(v_med * pixel_area_ha), 2), "percentage": round(float(v_med / total_pixels) * 100, 2)},
        {"name": "Low Health (0.20–0.40)", "range": "0.20 - 0.40", "color": "#eab308", "pixels": int(v_low), "area_ha": round(float(v_low * pixel_area_ha), 2), "percentage": round(float(v_low / total_pixels) * 100, 2)},
        {"name": "Very Low (0.00–0.20)", "range": "0.00 - 0.20", "color": "#ef4444", "pixels": int(v_vlow), "area_ha": round(float(v_vlow * pixel_area_ha), 2), "percentage": round(float(v_vlow / total_pixels) * 100, 2)},
        {"name": "Water / Non-vegetated (<0.00)", "range": "< 0.00", "color": "#3b82f6", "pixels": int(v_water), "area_ha": round(float(v_water * pixel_area_ha), 2), "percentage": round(float(v_water / total_pixels) * 100, 2)}
    ]

    # Histogram distribution (20 bins between -0.2 and 1.0)
    hist, bin_edges = np.histogram(sub_ndvi, bins=16, range=(-0.2, 1.0))
    distribution = []
    for i in range(len(hist)):
        b_start = round(float(bin_edges[i]), 2)
        b_end = round(float(bin_edges[i+1]), 2)
        distribution.append({
            "bin": f"{b_start} - {b_end}",
            "count": int(hist[i]),
            "percentage": round(float(hist[i] / total_pixels) * 100, 2)
        })

    # OpenCV Stress Hotspots detection
    hotspots, hotspot_overlay = detect_stress_hotspots_contours(
        ndvi,
        landcover_mask=landcover_gt,
        min_area_pixels=12,
        bbox_geo=meta.get("bbox")
    )

    # Generate Image Overlays
    ndvi_colormap_bgra = generate_ndvi_colormap(ndvi)
    health_class_bgra = generate_health_class_map(ndvi)

    # RGB and False Color images
    v_dir = DATA_DIR / village_id
    if not v_dir.exists():
        v_dir = DATA_DIR / "hiware_bazar"
    rgb_img = cv2.imread(str(v_dir / f"{time_tag}_rgb.png"))
    fc_img = cv2.imread(str(v_dir / f"{time_tag}_false_color.png"))

    # Summary statistics
    stats = {
        "mean_ndvi": round(float(np.mean(sub_ndvi)), 3),
        "min_ndvi": round(float(np.min(sub_ndvi)), 3),
        "max_ndvi": round(float(np.max(sub_ndvi)), 3),
        "std_ndvi": round(float(np.std(sub_ndvi)), 3),
        "mean_ndre": round(float(np.mean(ndre)), 3),
        "mean_ndwi": round(float(np.mean(ndwi)), 3),
        "mean_savi": round(float(np.mean(savi)), 3),
        "total_area_ha": total_area_ha,
        "vegetation_coverage_pct": veg_coverage_pct,
        "healthy_vegetation_pct": healthy_pct,
        "stressed_vegetation_pct": stressed_pct,
        "water_coverage_pct": water_pct,
        "hotspots_count": len(hotspots),
        "total_stress_area_ha": round(sum(h["area_ha"] for h in hotspots), 2)
    }

    return {
        "village_id": village_id,
        "village_name": meta.get("village_name", village_id),
        "time_tag": time_tag,
        "date": meta.get("date"),
        "satellite": meta.get("satellite"),
        "cloud_percentage": meta.get("cloud_percentage"),
        "coordinates": meta.get("coordinates"),
        "bbox": meta.get("bbox"),
        "stats": stats,
        "categories": categories,
        "distribution": distribution,
        "hotspots": hotspots[:15], # top 15 most prominent hotspots
        "overlays": {
            "ndvi_heatmap": f"data:image/png;base64,{encode_image_base64(ndvi_colormap_bgra)}",
            "health_classification": f"data:image/png;base64,{encode_image_base64(health_class_bgra)}",
            "stress_hotspots": f"data:image/png;base64,{encode_image_base64(hotspot_overlay)}",
            "true_color": f"data:image/png;base64,{encode_image_base64(rgb_img)}" if rgb_img is not None else "",
            "false_color": f"data:image/png;base64,{encode_image_base64(fc_img)}" if fc_img is not None else ""
        }
    }
