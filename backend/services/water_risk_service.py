
import os
import joblib
import pandas as pd

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "ml",
    "saved_models",
    "water_risk_model.pkl"
)

# Load trained Random Forest model
saved_data = joblib.load(MODEL_PATH)

model = saved_data["model"]
features = saved_data["features"]


def predict_water_risk(input_data):

    # Prepare input in the same format used during training
    input_df = pd.DataFrame(
        [input_data],
        columns=features
    )

    # Predict risk category
    prediction = model.predict(input_df)[0]

    # Get prediction confidence
    probabilities = model.predict_proba(input_df)[0]

    confidence = max(probabilities) * 100

    return {
        "risk_level": prediction,
        "confidence": round(float(confidence), 2)
    }
