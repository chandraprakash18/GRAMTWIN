
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

# Find the main project directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Load the trained XGBoost model
MODEL_PATH = BASE_DIR / "ml" / "saved_models" / "xgboost_model.pkl"

model = joblib.load(MODEL_PATH)

print("XGBoost water forecasting model loaded successfully!")


# Create the same features used during model training
def create_features(history, current_date):

    features = {}

    for lag in [1, 2, 3, 7, 14, 28]:
        features[f"lag_{lag}"] = history[-lag]

    for window in [7, 14, 28]:
        features[f"rolling_mean_{window}"] = np.mean(
            history[-window:]
        )

    features["day_of_week"] = current_date.day_of_week
    features["month"] = current_date.month
    features["day_of_year"] = current_date.day_of_year
    features["is_weekend"] = int(current_date.day_of_week >= 5)

    return features


# Predict future water demand
def forecast_water_demand(days=7):

    # Load historical water consumption data
    data_path = BASE_DIR / "data" / "processed" / "final_daily_water_demand.csv"

    df = pd.read_csv(data_path)

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    # Get historical consumption values
    history = df["daily_consumption"].tolist()

    if len(history) < 28:
        raise ValueError("At least 28 days of historical data are required.")

    last_date = df["date"].iloc[-1]

    predictions = []

    # Predict future demand one day at a time
    for i in range(1, days + 1):

        current_date = last_date + pd.Timedelta(days=i)

        features = create_features(history, current_date)

        input_data = pd.DataFrame([features])

        prediction = float(model.predict(input_data)[0])

        predictions.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "predicted_consumption": round(prediction, 2)
        })

        # Add prediction to history for the next day's forecast
        history.append(prediction)

    return predictions
