"""
GRAMTWIN - Satellite API Routes
Handles village search, boundary retrieval, available imagery dates, and image upload.
"""

import json
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

BASE_DIR = Path(__file__).resolve().parents[2]
VILLAGES_DIR = BASE_DIR / "backend" / "data" / "villages"
UPLOADS_DIR = BASE_DIR / "backend" / "data" / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter(
    prefix="/api/satellite",
    tags=["Satellite Imagery"]
)

@router.get("/villages")
def list_villages():
    """Lists all available Indian agricultural monitoring villages."""
    meta_file = VILLAGES_DIR / "villages.json"
    if not meta_file.exists():
        raise HTTPException(status_code=404, detail="Villages database not found.")
    villages = json.loads(meta_file.read_text())
    return {
        "status": "success",
        "count": len(villages),
        "villages": villages
    }

@router.get("/village/{village_id}/geojson")
def get_village_geojson(village_id: str):
    """Retrieves the official boundary GeoJSON for a village."""
    geojson_file = VILLAGES_DIR / f"{village_id}.geojson"
    if not geojson_file.exists():
        # Fallback to Hiware Bazar
        geojson_file = VILLAGES_DIR / "hiware_bazar.geojson"
    geojson_data = json.loads(geojson_file.read_text())
    return geojson_data

@router.get("/images")
def get_available_images(village_id: str = "hiware_bazar"):
    """
    Retrieves available multi-spectral Sentinel-2 satellite passes
    and temporal comparison options for the selected village.
    """
    v_dir = BASE_DIR / "backend" / "data" / "satellite_imagery" / village_id
    if not v_dir.exists():
        v_dir = BASE_DIR / "backend" / "data" / "satellite_imagery" / "hiware_bazar"

    meta_file = v_dir / "metadata.json"
    meta = json.loads(meta_file.read_text()) if meta_file.exists() else {}

    images = [
        {
            "id": f"{village_id}_t1",
            "time_tag": "t1",
            "date": meta.get("t1", {}).get("date", "2025-10-15"),
            "label": "T1: Previous Season (Post-Monsoon)",
            "satellite": "Sentinel-2B MSI (Level-2A)",
            "spatial_resolution": "10m/pixel",
            "cloud_percentage": 0.4,
            "bands_available": ["B2", "B3", "B4", "B5", "B8", "B11"]
        },
        {
            "id": f"{village_id}_t2",
            "time_tag": "t2",
            "date": meta.get("t2", {}).get("date", "2026-10-18"),
            "label": "T2: Recent Comparative Pass",
            "satellite": "Sentinel-2A MSI (Level-2A)",
            "spatial_resolution": "10m/pixel",
            "cloud_percentage": 0.8,
            "bands_available": ["B2", "B3", "B4", "B5", "B8", "B11"]
        }
    ]

    return {
        "village_id": village_id,
        "village_name": meta.get("village", {}).get("name", village_id),
        "available_passes": images,
        "default_t1": "t1",
        "default_t2": "t2",
        "imagery_provider": "Copernicus Sentinel-2 Surface Reflectance (L2A)"
    }

@router.post("/upload")
async def upload_satellite_image(
    file: UploadFile = File(...),
    village_name: str = Form("Uploaded Village")
):
    """Allows uploading custom satellite scene or GeoTIFF for processing."""
    file_path = UPLOADS_DIR / file.filename
    contents = await file.read()
    file_path.write_bytes(contents)

    return {
        "status": "success",
        "message": f"Satellite imagery {file.filename} uploaded successfully.",
        "filename": file.filename,
        "size_bytes": len(contents),
        "target_village": village_name
    }
