"""
GRAMTWIN - Sentinel-2 Satellite Multi-Spectral Data Synthesizer & Calibrator
Generates realistic multi-spectral surface reflectance bands (B2, B3, B4, B5, B8, B11)
matching Sentinel-2 MSI at 10m spatial resolution for temporal dates T1 and T2.
Includes land-cover ground-truth masks for supervised deep learning segmentation.
"""

import json
import os
from pathlib import Path
import cv2
import numpy as np

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "satellite_imagery"
DATA_DIR.mkdir(parents=True, exist_ok=True)
VILLAGES_DIR = BASE_DIR / "data" / "villages"

villages = json.loads((VILLAGES_DIR / "villages.json").read_text())

# Land-cover class definitions:
# 0: Background / No-data
# 1: Agricultural Land (Crops / Farmland)
# 2: Trees / Forest (Canopy, Orchards, Agroforestry)
# 3: Water Bodies (Ponds, Reservoirs, Streams, Tanks)
# 4: Built-up Areas (Settlements, Farm structures, Roads)
# 5: Bare Soil (Fallow, Barren land, Exposed soil)

CLASS_COLORS = {
    1: (34, 197, 94),    # Agri: Emerald Green
    2: (21, 128, 61),    # Forest: Deep Green
    3: (59, 130, 246),   # Water: Blue
    4: (239, 68, 68),    # Built-up: Red/Coral
    5: (217, 119, 6)     # Bare Soil: Amber/Brown
}

def generate_spatial_landscape(H=384, W=384, seed=42, village_type="semi_arid"):
    """
    Generates a realistic spatial pattern of village landscapes with agricultural fields,
    clusters of trees, streams/ponds, village settlement centers, and fallow soil.
    """
    np.random.seed(seed)
    mask = np.zeros((H, W), dtype=np.uint8)

    # 1. Base default: Agricultural fields (Class 1) and Bare soil (Class 5)
    # Generate field boundaries using Voronoi-like field patchwork
    num_fields = 70
    fx = np.random.randint(0, W, num_fields)
    fy = np.random.randint(0, H, num_fields)
    field_types = np.random.choice([1, 1, 1, 5], size=num_fields) # 75% agri, 25% bare/fallow

    # Simple field tessellation
    grid_y, grid_x = np.ogrid[:H, :W]
    distances = np.sqrt((grid_x[:, :, None] - fx)**2 + (grid_y[:, :, None] - fy)**2)
    closest_field = np.argmin(distances, axis=2)
    mask = field_types[closest_field].astype(np.uint8)

    # 2. Water Bodies (Class 3): A winding stream or canal and 1-2 percolation tanks/ponds
    # Stream
    stream_pts = []
    sx = int(W * 0.15)
    for y in range(0, H, 20):
        sx += int(np.random.normal(0, 8))
        sx = max(10, min(W - 10, sx))
        stream_pts.append([sx, y])
    stream_pts = np.array(stream_pts, np.int32).reshape((-1, 1, 2))
    cv2.polylines(mask, [stream_pts], isClosed=False, color=3, thickness=6)

    # 1-2 Ponds / Percolation Tanks
    p1_center = (int(W * 0.55), int(H * 0.45))
    cv2.circle(mask, p1_center, radius=int(W * 0.06), color=3, thickness=-1)
    if village_type != "arid":
        p2_center = (int(W * 0.25), int(H * 0.75))
        cv2.circle(mask, p2_center, radius=int(W * 0.04), color=3, thickness=-1)

    # 3. Trees / Forest / Orchards (Class 2): Riparian buffers along water + hillside clusters
    # Buffer along stream
    stream_tree_mask = np.zeros((H, W), dtype=np.uint8)
    cv2.polylines(stream_tree_mask, [stream_pts], isClosed=False, color=255, thickness=16)
    tree_locs = (stream_tree_mask == 255) & (mask != 3) & (np.random.rand(H, W) > 0.4)
    mask[tree_locs] = 2

    # Forest / Agroforestry clusters
    for _ in range(8):
        cx = np.random.randint(int(W*0.05), int(W*0.95))
        cy = np.random.randint(int(H*0.05), int(H*0.95))
        r = np.random.randint(int(W*0.04), int(W*0.09))
        c_mask = np.zeros((H, W), dtype=np.uint8)
        cv2.circle(c_mask, (cx, cy), r, 255, -1)
        cluster_locs = (c_mask == 255) & (mask != 3) & (np.random.rand(H, W) > 0.3)
        mask[cluster_locs] = 2

    # 4. Built-up Areas (Class 4): Village center settlement cluster and farm structures
    # Village nucleus near center
    n_cx, n_cy = int(W * 0.62), int(H * 0.58)
    settle_mask = np.zeros((H, W), dtype=np.uint8)
    cv2.circle(settle_mask, (n_cx, n_cy), int(W * 0.08), 255, -1)
    # Add rectangular roads/buildings
    for _ in range(12):
        bx = n_cx + np.random.randint(-int(W*0.07), int(W*0.07))
        by = n_cy + np.random.randint(-int(H*0.07), int(H*0.07))
        bw, bh = np.random.randint(6, 16), np.random.randint(6, 16)
        cv2.rectangle(settle_mask, (bx, by), (bx+bw, by+bh), 255, -1)
    
    # Roads connecting to borders
    cv2.line(settle_mask, (n_cx, n_cy), (0, int(H*0.5)), 255, 4)
    cv2.line(settle_mask, (n_cx, n_cy), (W, int(H*0.6)), 255, 4)
    cv2.line(settle_mask, (n_cx, n_cy), (int(W*0.6), 0), 255, 4)

    settle_locs = (settle_mask == 255) & (mask != 3)
    mask[settle_locs] = 4

    return mask

def synthesize_spectral_bands(mask, H=384, W=384, noise_level=0.03, season="post_monsoon"):
    """
    Maps land cover classes to calibrated physical surface reflectance values
    across Sentinel-2 spectral bands: B2 (Blue), B3 (Green), B4 (Red), B5 (RedEdge), B8 (NIR), B11 (SWIR).
    Values represent surface reflectance in [0.0, 1.0].
    """
    # Base nominal reflectance per class: [B2, B3, B4, B5, B8, B11]
    # Water: low across all, very low NIR/SWIR
    # Agri: moderate B3, low B4 (absorption), high B8 (NIR scattering), moderate SWIR
    # Forest: very dark B2/B4, very high B8, low SWIR
    # Built-up: high B2/B3/B4 (concrete/roads), moderate B8, high B11
    # Bare Soil: moderate B2, higher B3/B4, moderate-high B8, highest B11
    
    signatures = {
        1: [0.035, 0.082, 0.045, 0.160, 0.520, 0.180],  # Agri
        2: [0.025, 0.055, 0.028, 0.140, 0.650, 0.140],  # Trees/Forest
        3: [0.050, 0.070, 0.035, 0.020, 0.015, 0.010],  # Water
        4: [0.140, 0.160, 0.180, 0.200, 0.240, 0.320],  # Built-up
        5: [0.110, 0.150, 0.210, 0.240, 0.290, 0.380]   # Bare Soil
    }

    bands = np.zeros((6, H, W), dtype=np.float32)

    for c, sig in signatures.items():
        locs = (mask == c)
        count = np.sum(locs)
        if count == 0:
            continue
        for b_idx in range(6):
            base_val = sig[b_idx]
            # Add spatial natural gradient and texture
            noise = np.random.normal(0, noise_level * base_val, (H, W))
            val_map = np.clip(base_val + noise, 0.005, 0.95)
            bands[b_idx][locs] = val_map[locs]

    # Smooth bands slightly with OpenCV GaussianBlur to mimic sensor PSF (Point Spread Function)
    for b_idx in range(6):
        bands[b_idx] = cv2.GaussianBlur(bands[b_idx], (3, 3), 0.8)

    return bands

def create_rgb_composite(bands):
    """
    Generates standard True Color RGB (B4=Red, B3=Green, B2=Blue)
    and stretches to 8-bit [0, 255] for visual display.
    """
    b2_blue = bands[0]
    b3_green = bands[1]
    b4_red = bands[2]

    rgb = np.stack([b4_red, b3_green, b2_blue], axis=-1)
    # 2% to 98% percentile contrast stretch
    p2, p98 = np.percentile(rgb, (2, 98))
    rgb_stretched = np.clip((rgb - p2) / (p98 - p2 + 1e-6), 0.0, 1.0)
    rgb_uint8 = (rgb_stretched * 255).astype(np.uint8)
    return rgb_uint8

def create_false_color_composite(bands):
    """
    Generates standard False Color Infrared (B8=NIR as Red, B4=Red as Green, B3=Green as Blue)
    which highlights vegetation vitality in brilliant shades of red.
    """
    b3_green = bands[1]
    b4_red = bands[2]
    b8_nir = bands[4]

    fc = np.stack([b8_nir, b4_red, b3_green], axis=-1)
    p2, p98 = np.percentile(fc, (2, 98))
    fc_stretched = np.clip((fc - p2) / (p98 - p2 + 1e-6), 0.0, 1.0)
    fc_uint8 = (fc_stretched * 255).astype(np.uint8)
    return fc_uint8

def build_temporal_pair_for_village(v):
    """
    Generates synchronized T1 (2025-10-15) and T2 (2026-10-18) Sentinel-2 imagery
    with realistic temporal vegetation growth, crop rotations, and minor built-up expansion.
    """
    v_id = v["id"]
    H, W = 384, 384
    seed_base = abs(int(v["center"][0] * 1000 + v["center"][1] * 1000)) % 10000

    # T1 Base Landscape
    mask_t1 = generate_spatial_landscape(H, W, seed=seed_base, village_type="semi_arid")

    # T2 Landscape Evolution:
    # 1. Some bare soil converted to healthy agricultural crops (vegetation gain ~ 8-12%)
    # 2. Some agricultural fields harvested or suffered moisture stress (vegetation loss ~ 4-6%)
    # 3. Slight village settlement expansion (built-up increase ~ 1.5%)
    mask_t2 = mask_t1.copy()
    np.random.seed(seed_base + 101)

    # Conversion of bare soil (5) to Agri (1)
    bare_locs = np.argwhere(mask_t1 == 5)
    if len(bare_locs) > 0:
        gain_choice = np.random.choice(len(bare_locs), size=int(len(bare_locs) * 0.45), replace=False)
        for idx in gain_choice:
            r, c = bare_locs[idx]
            # grow small patch
            mask_t2[max(0, r-2):min(H, r+3), max(0, c-2):min(W, c+3)] = 1

    # Conversion of some Agri (1) to Bare/Fallow (5) (crop harvesting)
    agri_locs = np.argwhere(mask_t1 == 1)
    if len(agri_locs) > 0:
        loss_choice = np.random.choice(len(agri_locs), size=int(len(agri_locs) * 0.15), replace=False)
        for idx in loss_choice:
            r, c = agri_locs[idx]
            mask_t2[max(0, r-2):min(H, r+3), max(0, c-2):min(W, c+3)] = 5

    # Slight built-up expansion (4) at edges of existing settlements
    settle_locs = np.argwhere(mask_t1 == 4)
    if len(settle_locs) > 0:
        exp_choice = np.random.choice(len(settle_locs), size=int(len(settle_locs) * 0.20), replace=False)
        for idx in exp_choice:
            r, c = settle_locs[idx]
            mask_t2[max(0, r-1):min(H, r+2), max(0, c-1):min(W, c+2)] = 4

    # Keep water persistent
    mask_t2[mask_t1 == 3] = 3

    # Generate spectral bands for T1 and T2
    bands_t1 = synthesize_spectral_bands(mask_t1, H, W, noise_level=0.03, season="t1")
    bands_t2 = synthesize_spectral_bands(mask_t2, H, W, noise_level=0.03, season="t2")

    # Generate True Color and False Color RGB images
    rgb_t1 = create_rgb_composite(bands_t1)
    rgb_t2 = create_rgb_composite(bands_t2)
    fc_t1 = create_false_color_composite(bands_t1)
    fc_t2 = create_false_color_composite(bands_t2)

    # Save images to disk
    v_dir = DATA_DIR / v_id
    v_dir.mkdir(parents=True, exist_ok=True)

    cv2.imwrite(str(v_dir / "t1_rgb.png"), cv2.cvtColor(rgb_t1, cv2.COLOR_RGB2BGR))
    cv2.imwrite(str(v_dir / "t2_rgb.png"), cv2.cvtColor(rgb_t2, cv2.COLOR_RGB2BGR))
    cv2.imwrite(str(v_dir / "t1_false_color.png"), cv2.cvtColor(fc_t1, cv2.COLOR_RGB2BGR))
    cv2.imwrite(str(v_dir / "t2_false_color.png"), cv2.cvtColor(fc_t2, cv2.COLOR_RGB2BGR))

    # Save colored ground truth masks for visualization
    mask_vis_t1 = np.zeros((H, W, 3), dtype=np.uint8)
    mask_vis_t2 = np.zeros((H, W, 3), dtype=np.uint8)
    for c, col in CLASS_COLORS.items():
        mask_vis_t1[mask_t1 == c] = col
        mask_vis_t2[mask_t2 == c] = col
    cv2.imwrite(str(v_dir / "t1_ground_truth_mask.png"), cv2.cvtColor(mask_vis_t1, cv2.COLOR_RGB2BGR))
    cv2.imwrite(str(v_dir / "t2_ground_truth_mask.png"), cv2.cvtColor(mask_vis_t2, cv2.COLOR_RGB2BGR))

    # Save multi-band arrays & metadata
    # Bands ordering: [B2, B3, B4, B5, B8, B11]
    meta_t1 = {
        "village_id": v_id,
        "village_name": v["name"],
        "date": "2025-10-15",
        "satellite": "Sentinel-2B MSI (L2A)",
        "spatial_resolution": "10m/pixel",
        "cloud_percentage": 0.4,
        "coordinates": v["center"],
        "bbox": v["bbox"],
        "width": W,
        "height": H,
        "pixel_size_m": 10.0,
        "total_area_ha": round((W * 10 * H * 10) / 10000.0, 2),
        "bands": ["B2_Blue", "B3_Green", "B4_Red", "B5_RedEdge", "B8_NIR", "B11_SWIR"]
    }

    meta_t2 = {
        "village_id": v_id,
        "village_name": v["name"],
        "date": "2026-10-18",
        "satellite": "Sentinel-2A MSI (L2A)",
        "spatial_resolution": "10m/pixel",
        "cloud_percentage": 0.8,
        "coordinates": v["center"],
        "bbox": v["bbox"],
        "width": W,
        "height": H,
        "pixel_size_m": 10.0,
        "total_area_ha": round((W * 10 * H * 10) / 10000.0, 2),
        "bands": ["B2_Blue", "B3_Green", "B4_Red", "B5_RedEdge", "B8_NIR", "B11_SWIR"]
    }

    np.savez_compressed(
        str(v_dir / "t1_bands.npz"),
        bands=bands_t1,
        mask=mask_t1,
        meta=json.dumps(meta_t1)
    )

    np.savez_compressed(
        str(v_dir / "t2_bands.npz"),
        bands=bands_t2,
        mask=mask_t2,
        meta=json.dumps(meta_t2)
    )

    (v_dir / "metadata.json").write_text(json.dumps({
        "village": v,
        "t1": meta_t1,
        "t2": meta_t2
    }, indent=2))

    print(f"Generated Sentinel-2 multi-spectral dataset for {v['name']} ({v_id}).")

def main():
    print("Synthesizing multi-spectral calibrated Sentinel-2 bands for villages...")
    for v in villages:
        build_temporal_pair_for_village(v)
    print("Done! All satellite datasets generated.")

if __name__ == "__main__":
    main()
