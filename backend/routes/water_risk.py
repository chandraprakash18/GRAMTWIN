
from fastapi import APIRouter
from pydantic import BaseModel

from backend.services.water_risk_service import predict_water_risk

router = APIRouter(
    prefix="/water/risk",
    tags=["Water Risk"]
)


class WaterRiskInput(BaseModel):
    daily_consumption: float
    avg_temperature: float
    daily_rain: float
    daily_sun_total: float
    avg_sun: float
    hourly_records: int
    month: int
    day_of_week: int


@router.post("/predict")
def get_water_risk(data: WaterRiskInput):

    input_data = {
        "daily_consumption": data.daily_consumption,
        "avg_temperature": data.avg_temperature,
        "daily_rain": data.daily_rain,
        "daily_sun_total": data.daily_sun_total,
        "avg_sun": data.avg_sun,
        "hourly_records": data.hourly_records,
        "month": data.month,
        "day_of_week": data.day_of_week
    }

    result = predict_water_risk(input_data)

    return {
        "status": "success",
        "message": "Water demand pressure risk predicted successfully",
        **result
    }
