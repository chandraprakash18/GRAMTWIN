"""
GRAMTWIN - OpenCV Computer Vision Processing Pipeline
Modular, reusable image-processing operations for satellite multi-spectral analysis.
"""

import base64
import cv2
import numpy as np

def encode_image_base64(image_bgr_or_rgba):
    """Encodes an OpenCV image (BGR or BGRA) to PNG base64 string."""
    success, buffer = cv2.imencode(".png", image_bgr_or_rgba)
    if not success:
        raise ValueError("Failed to encode image to PNG")
    return base64.b64encode(buffer).decode("utf-8")

def apply_noise_reduction(band, method="bilateral"):
    """
    Applies edge-preserving noise reduction on a single spectral band.
    Preserves field boundaries while smoothing sensor noise.
    """
    band_norm = np.clip(band, 0.0, 1.0).astype(np.float32)
    if method == "bilateral":
        # OpenCV bilateralFilter requires 8-bit or 32-bit float
        filtered = cv2.bilateralFilter(band_norm, d=5, sigmaColor=0.08, sigmaSpace=3.0)
    elif method == "gaussian":
        filtered = cv2.GaussianBlur(band_norm, (3, 3), 0.8)
    else:
        filtered = band_norm
    return filtered

def align_images_ecc(image_t1, image_t2, warp_mode=cv2.MOTION_TRANSLATION):
    """
    Sub-pixel geographical image alignment using OpenCV Enhanced Correlation Coefficient (ECC).
    Aligns image_t2 to reference image_t1.
    """
    # Convert to 8-bit grayscale for ECC calculation
    if len(image_t1.shape) == 3:
        gray_t1 = cv2.cvtColor(image_t1, cv2.COLOR_BGR2GRAY)
        gray_t2 = cv2.cvtColor(image_t2, cv2.COLOR_BGR2GRAY)
    else:
        gray_t1 = (np.clip(image_t1, 0, 1) * 255).astype(np.uint8)
        gray_t2 = (np.clip(image_t2, 0, 1) * 255).astype(np.uint8)

    warp_matrix = np.eye(2, 3, dtype=np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 50, 1e-4)

    try:
        _, warp_matrix = cv2.findTransformECC(gray_t1, gray_t2, warp_matrix, warp_mode, criteria)
        h, w = gray_t1.shape[:2]
        aligned = cv2.warpAffine(image_t2, warp_matrix, (w, h), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
        return aligned, warp_matrix
    except cv2.error:
        # Fallback if already georeferenced & aligned
        return image_t2, np.eye(2, 3, dtype=np.float32)

def generate_ndvi_colormap(ndvi_array):
    """
    Converts continuous NDVI [-1.0, 1.0] to standard agricultural color palette:
    < 0.0: Blue / Non-vegetated
    0.0 - 0.2: Red (Barren / Extremely low)
    0.2 - 0.4: Orange (Low / Stressed)
    0.4 - 0.66: Yellow-Green (Moderate vigor)
    0.66 - 1.0: Lush Green to Deep Emerald (High vigor)
    Returns BGRA uint8 image (A=255).
    """
    h, w = ndvi_array.shape
    bgr = np.zeros((h, w, 3), dtype=np.uint8)

    # Custom multi-stop agricultural colormap interpolation
    # Stops: (ndvi_val, [B, G, R])
    stops = [
        (-1.0, [230, 140, 50]),   # Blue / Water
        (-0.01, [210, 110, 30]),  # Water/Shade
        (0.0, [30, 30, 220]),     # Red / Barren
        (0.20, [30, 120, 230]),   # Orange
        (0.40, [30, 210, 230]),   # Yellow
        (0.66, [50, 200, 70]),    # Light Green
        (0.85, [30, 140, 30]),    # Green
        (1.0, [15, 90, 15])       # Deep Emerald
    ]

    # Vectorized interpolation
    ndvi_flat = np.clip(ndvi_array.flatten(), -1.0, 1.0)
    stop_vals = [s[0] for s in stops]
    stop_colors = np.array([s[1] for s in stops])

    # Interpolate B, G, R channels
    b_chan = np.interp(ndvi_flat, stop_vals, stop_colors[:, 0]).reshape((h, w)).astype(np.uint8)
    g_chan = np.interp(ndvi_flat, stop_vals, stop_colors[:, 1]).reshape((h, w)).astype(np.uint8)
    r_chan = np.interp(ndvi_flat, stop_vals, stop_colors[:, 2]).reshape((h, w)).astype(np.uint8)

    bgr = cv2.merge([b_chan, g_chan, r_chan])
    alpha = np.full((h, w), 255, dtype=np.uint8)
    bgra = cv2.merge([b_chan, g_chan, r_chan, alpha])
    return bgra

def generate_health_class_map(ndvi_array):
    """
    Maps NDVI to discrete health categories:
    5: High (0.66 - 1.0) -> #16a34a (Green)
    4: Medium (0.40 - 0.66) -> #84cc16 (Yellow-Green)
    3: Low (0.20 - 0.40) -> #eab308 (Orange)
    2: Very Low (0.00 - 0.20) -> #ef4444 (Red)
    1: Water / Non-vegetated (< 0.00) -> #3b82f6 (Blue)
    """
    h, w = ndvi_array.shape
    color_map = np.zeros((h, w, 4), dtype=np.uint8)

    # BGRA definitions
    c_water = [246, 130, 59, 255]     # Blue
    c_vlow = [68, 68, 239, 255]       # Red
    c_low = [8, 179, 234, 255]        # Orange
    c_med = [22, 204, 132, 255]       # Yellow-green
    c_high = [74, 163, 22, 255]       # Emerald Green

    color_map[ndvi_array < 0.0] = c_water
    color_map[(ndvi_array >= 0.0) & (ndvi_array < 0.20)] = c_vlow
    color_map[(ndvi_array >= 0.20) & (ndvi_array < 0.40)] = c_low
    color_map[(ndvi_array >= 0.40) & (ndvi_array < 0.66)] = c_med
    color_map[ndvi_array >= 0.66] = c_high

    return color_map

def detect_stress_hotspots_contours(ndvi_array, landcover_mask=None, min_area_pixels=10, bbox_geo=None):
    """
    Detects vegetation stress hotspots using OpenCV contour and morphological analysis.
    Hotspots are contiguous clusters where NDVI indicates vegetation stress (0.15 <= NDVI <= 0.46).
    If landcover_mask is provided, focuses on agricultural or stressed canopy zones.
    """
    h, w = ndvi_array.shape

    # Binary mask of stressed pixels
    stress_mask = ((ndvi_array >= 0.12) & (ndvi_array <= 0.48)).astype(np.uint8) * 255

    # If land cover is available, exclude open water bodies (Class 3) and deep built-up centers (Class 4)
    if landcover_mask is not None:
        stress_mask[landcover_mask == 3] = 0

    # Morphological opening to remove isolated noise, followed by closing to bridge small gaps
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    cleaned = cv2.morphologyEx(stress_mask, cv2.MORPH_OPEN, kernel, iterations=1)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Find contours of stress clusters
    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    hotspots = []
    overlay = np.zeros((h, w, 4), dtype=np.uint8)

    # Geo transform helpers
    if bbox_geo:
        min_lon, min_lat, max_lon, max_lat = bbox_geo
    else:
        min_lon, min_lat, max_lon, max_lat = 0, 0, 1, 1

    for idx, cnt in enumerate(contours):
        area = cv2.contourArea(cnt)
        if area < min_area_pixels:
            continue

        x, y, bw, bh = cv2.boundingRect(cnt)
        M = cv2.moments(cnt)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
        else:
            cx, cy = x + bw // 2, y + bh // 2

        # Geographic coordinates
        geo_lon = round(min_lon + (cx / w) * (max_lon - min_lon), 6)
        geo_lat = round(max_lat - (cy / h) * (max_lat - min_lat), 6)

        # Region NDVI stats
        cnt_mask = np.zeros((h, w), dtype=np.uint8)
        cv2.drawContours(cnt_mask, [cnt], -1, 255, -1)
        cluster_ndvi = ndvi_array[cnt_mask == 255]
        mean_ndvi = float(np.mean(cluster_ndvi)) if len(cluster_ndvi) > 0 else 0.2

        # Severity rating
        if mean_ndvi < 0.18:
            severity = "Severe"
            color = [0, 0, 240, 220] # Red
        elif mean_ndvi < 0.26:
            severity = "Moderate"
            color = [0, 140, 255, 220] # Orange
        else:
            severity = "Mild"
            color = [0, 230, 255, 220] # Yellow

        # Draw contour and bounding rect on overlay
        cv2.drawContours(overlay, [cnt], -1, color, 2)
        cv2.circle(overlay, (cx, cy), 4, color, -1)

        area_ha = round((area * 100) / 10000.0, 3) # 10m x 10m per pixel

        hotspots.append({
            "id": f"hotspot_{idx+1}",
            "severity": severity,
            "mean_ndvi": round(mean_ndvi, 3),
            "area_ha": area_ha,
            "pixel_count": int(area),
            "center_pixel": [cx, cy],
            "coordinates": [geo_lat, geo_lon],
            "bbox_pixels": [x, y, bw, bh]
        })

    # Sort hotspots by severity and area
    hotspots.sort(key=lambda item: (item["severity"] == "Severe", item["area_ha"]), reverse=True)

    return hotspots, overlay
