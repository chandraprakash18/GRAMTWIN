"""
GRAMTWIN - Vegetation Intelligence Routes
Endpoints for NDVI calculation, multi-spectral indices (NDRE, NDWI, SAVI),
health classification, histograms, and OpenCV stress hotspots.
"""

from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from backend.services.vegetation_service import compute_vegetation_analysis

router = APIRouter(
    prefix="/api/vegetation",
    tags=["Vegetation Intelligence"]
)

class VegetationRequest(BaseModel):
    village_id: str = "hiware_bazar"
    time_tag: str = "t2"
    aoi_bbox: Optional[List[float]] = None

@router.post("/ndvi")
def analyze_ndvi(req: VegetationRequest):
    """
    Computes NDVI = (NIR - RED) / (NIR + RED) using Sentinel-2 B8 (NIR) and B4 (Red).
    Generates health zones, OpenCV stress hotspots, and colormap overlays.
    """
    try:
        result = compute_vegetation_analysis(
            village_id=req.village_id,
            time_tag=req.time_tag,
            aoi_bbox=req.aoi_bbox
        )
        return {
            "status": "success",
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/indices")
def analyze_spectral_indices(req: VegetationRequest):
    """
    Calculates multiple spectral indices:
    - NDVI: (B8 - B4) / (B8 + B4)
    - NDRE: (B8 - B5) / (B8 + B5)
    - NDWI: (B3 - B8) / (B3 + B8)
    - SAVI: ((B8 - B4) / (B8 + B4 + 0.5)) * 1.5
    """
    try:
        result = compute_vegetation_analysis(
            village_id=req.village_id,
            time_tag=req.time_tag,
            aoi_bbox=req.aoi_bbox
        )
        return {
            "status": "success",
            "village_id": req.village_id,
            "indices": {
                "ndvi": {"name": "Normalized Difference Vegetation Index", "mean": result["stats"]["mean_ndvi"], "formula": "(B8 - B4) / (B8 + B4)"},
                "ndre": {"name": "Normalized Difference Red Edge Index", "mean": result["stats"]["mean_ndre"], "formula": "(B8 - B5) / (B8 + B5)"},
                "ndwi": {"name": "Normalized Difference Water Index", "mean": result["stats"]["mean_ndwi"], "formula": "(B3 - B8) / (B3 + B8)"},
                "savi": {"name": "Soil Adjusted Vegetation Index", "mean": result["stats"]["mean_savi"], "formula": "((B8 - B4) / (B8 + B4 + 0.5)) * 1.5"}
            },
            "stats": result["stats"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
