"""
GRAMTWIN - Temporal Change Detection Routes
Endpoints for comparing multi-temporal satellite imagery (T1 vs T2),
NDVI differencing, vegetation gain/loss, and built-up expansion.
"""

from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from backend.services.change_detection_service import analyze_temporal_changes

router = APIRouter(
    prefix="/api/change-detection",
    tags=["Temporal Change Detection"]
)

class ChangeDetectionRequest(BaseModel):
    village_id: str = "hiware_bazar"
    t1_date: str = "2025-10-15"
    t2_date: str = "2026-10-18"

@router.post("/analyze")
def analyze_change(req: ChangeDetectionRequest):
    """
    Executes multi-temporal comparison between T1 and T2.
    Calculates NDVI differencing, vegetation gain, vegetation loss,
    and identifies built-up expansion using deep learning segmentation.
    """
    try:
        result = analyze_temporal_changes(village_id=req.village_id)
        return {
            "status": "success",
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
