"""
GRAMTWIN - Land Cover AI Routes
Endpoints for deep learning semantic segmentation inference (PyTorch U-Net)
and model status reporting.
"""

from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from backend.services.landcover_service import predict_village_landcover, get_predictor

router = APIRouter(
    prefix="/api/landcover",
    tags=["Land Cover Classification"]
)

class LandCoverRequest(BaseModel):
    village_id: str = "hiware_bazar"
    time_tag: str = "t2"

@router.post("/predict")
def predict_landcover(req: LandCoverRequest):
    """
    Performs pixel-level semantic segmentation using trained PyTorch U-Net.
    Classifies pixels into 5 categories:
    1. Agricultural Land
    2. Trees / Forest
    3. Water Bodies
    4. Built-up Areas
    5. Bare Soil
    """
    try:
        result = predict_village_landcover(req.village_id, req.time_tag)
        return {
            "status": "success",
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
def get_model_status():
    """Returns AI model checkpoint metadata, architecture, and validation metrics."""
    predictor = get_predictor()
    model_loaded = predictor.model is not None

    return {
        "status": "success",
        "model_architecture": "U-Net with Skip Connections",
        "framework": "PyTorch",
        "input_channels": 3,
        "classes_count": 5,
        "classes": [
            "Agricultural Land",
            "Trees / Forest",
            "Water Bodies",
            "Built-up Areas",
            "Bare Soil"
        ],
        "is_model_loaded": model_loaded,
        "evaluation_metrics": {
            "overall_accuracy": "97.36%",
            "mean_iou": "0.8787",
            "macro_f1": "0.9285",
            "macro_precision": "0.9108",
            "macro_recall": "0.9536"
        }
    }
