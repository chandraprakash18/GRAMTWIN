from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Existing routes (Preserved)
from backend.routes.water import router as water_router
from backend.routes.water_resources import router as resources_router
from backend.routes.water_risk import router as water_risk_router

# New Satellite & Geospatial Intelligence routes
from backend.routes.satellite import router as satellite_router
from backend.routes.vegetation import router as vegetation_router
from backend.routes.landcover import router as landcover_router
from backend.routes.change_detection import router as change_detection_router
from backend.routes.analytics import router as analytics_router
from backend.routes.reports import router as reports_router

app = FastAPI(
    title="GRAMTWIN AI — Geospatial & Satellite Intelligence API",
    description="Village Digital Twin & Satellite Imagery Monitoring Platform",
    version="2.0.0"
)

# Allow React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect preserved existing routes
app.include_router(water_router)
app.include_router(resources_router)
app.include_router(water_risk_router)

# Connect new satellite & geospatial intelligence routes
app.include_router(satellite_router)
app.include_router(vegetation_router)
app.include_router(landcover_router)
app.include_router(change_detection_router)
app.include_router(analytics_router)
app.include_router(reports_router)

@app.get("/")
def home():
    return {
        "platform": "GRAMTWIN AI",
        "version": "2.0.0",
        "description": "Satellite Imagery, Vegetation Intelligence & Temporal Change Detection Platform",
        "status": "System operational",
        "modules": [
            "Satellite Viewer",
            "Vegetation Intelligence (NDVI, NDRE, NDWI, SAVI)",
            "Land Cover Segmentation (PyTorch U-Net)",
            "Temporal Change Detection (T1 vs T2)",
            "OpenCV Computer Vision Pipeline",
            "Automated AI Agronomic Insights",
            "PDF & CSV Report Generator",
            "Water Demand Forecasting (Preserved)",
            "Water Resources & Infrastructure (Preserved)"
        ]
    }
