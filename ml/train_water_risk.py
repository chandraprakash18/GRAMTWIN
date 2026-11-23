import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

import joblib
import os


# Project directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Dataset path
DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "final_daily_water_demand.csv"
)

# Load dataset
df = pd.read_csv(DATA_PATH)

# Display dataset information
print("\nDataset loaded successfully!")
print("\nFirst 5 records:")
print(df.head())

print("\nDataset shape:", df.shape)

print("\nMissing values:")
print(df.isnull().sum())


print("\nWater Consumption Statistics:")

print(df["daily_consumption"].describe())

print("\nConsumption Percentiles:")

print(df["daily_consumption"].quantile([
    0.50,
    0.60,
    0.75,
    0.85,
    0.90
]))


# Define next day's water consumption
df["next_day_consumption"] = df["daily_consumption"].shift(-1)

# Remove the final row because it has no next-day value
df = df.dropna().copy()

# Create risk categories
def classify_risk(consumption):

    if consumption <= 54139:
        return "Low"

    elif consumption <= 61398:
        return "Medium"

    else:
        return "High"


df["risk_level"] = df["next_day_consumption"].apply(classify_risk)

# Display risk category distribution
print("\nWater Demand Pressure Risk Distribution:")

print(df["risk_level"].value_counts())

print("\nRisk percentages:")

print(
    df["risk_level"].value_counts(normalize=True) * 100
)


# Convert date into useful numerical features
df["date"] = pd.to_datetime(df["date"])

df["month"] = df["date"].dt.month
df["day_of_week"] = df["date"].dt.day_of_week

# Select input features
features = [
    "daily_consumption",
    "avg_temperature",
    "daily_rain",
    "daily_sun_total",
    "avg_sun",
    "hourly_records",
    "month",
    "day_of_week"
]

X = df[features]
y = df["risk_level"]

# Chronological 80:20 split
split_index = int(len(df) * 0.80)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]

print("\nTraining and Testing Data:")
print("Training records:", len(X_train))
print("Testing records:", len(X_test))
print("Number of features:", len(features))


# Train Random Forest Classifier
model = RandomForestClassifier(
    n_estimators=300,
    max_depth=10,
    random_state=42,
    class_weight="balanced"
)

print("\nTraining Random Forest model...")

model.fit(X_train, y_train)

# Predict risk levels
y_pred = model.predict(X_test)

# Evaluate model
accuracy = accuracy_score(y_test, y_pred)

print("\nModel Training Completed!")

print("\nModel Accuracy:", round(accuracy * 100, 2), "%")

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))


# Save trained model
MODEL_DIR = os.path.join(BASE_DIR, "ml", "saved_models")

os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "water_risk_model.pkl"
)

joblib.dump(
    {
        "model": model,
        "features": features,
        "risk_thresholds": {
            "low_max": 54139,
            "medium_max": 61398
        }
    },
    MODEL_PATH
)

print("\nWater Risk Model saved successfully!")
print("Saved at:", MODEL_PATH)

