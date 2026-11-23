
from fastapi import APIRouter
from backend.services.water_service import forecast_water_demand

router = APIRouter(
    prefix="/water",
    tags=["Water Forecasting"]
)


@router.get("/")
def water_home():
    return {
        "message": "Water forecasting API is ready!"
    }


@router.get("/forecast")
def get_water_forecast(days: int = 7):

    if days < 1 or days > 30:
        return {
            "error": "Days must be between 1 and 30"
        }

    predictions = forecast_water_demand(days)

    return {
        "model": "XGBoost",
        "forecast_days": days,
        "predictions": predictions
    }

@router.get("/comparison")
def get_water_comparison():
    import pandas as pd
    from pathlib import Path

    base_dir = Path(__file__).resolve().parents[2]

    file_path = (
        base_dir
        / "results"
        / "forecasts"
        / "xgboost_predictions.csv"
    )

    df = pd.read_csv(file_path)

    return df.to_dict(orient="records")
