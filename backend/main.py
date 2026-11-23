from backend.routes.water_risk import router as water_risk_router
from backend.routes.water_resources import router as resources_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.water import router as water_router

app = FastAPI(
    title="GRAMTWIN2.0 API",
    description="Village Digital Twin Backend",
    version="1.0.0"
)

# Allow React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect water forecasting routes
app.include_router(water_router)
app.include_router(resources_router)
app.include_router(water_risk_router)

@app.get("/")
def home():
    return {
        "message": "Welcome to GRAMTWIN2.0",
        "status": "Backend is running successfully"
    }
