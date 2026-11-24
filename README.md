# GRAMTWIN AI
## AI-Powered Satellite Imagery, Vegetation Intelligence & Temporal Change Detection Platform

GRAMTWIN AI is an intelligent geospatial platform designed for village-scale satellite monitoring, agricultural vegetation health analysis, deep learning land-cover classification, multi-temporal change detection, and automated agronomic insights.

---

## 🌟 Key Features & Core Modules

### 🛰️ Module A: Satellite Imagery Viewer
- **Multi-Village Selection:** High-resolution boundary definitions and multi-spectral satellite imagery for Indian agricultural model villages including **Hiware Bazar** (Maharashtra), **Ralegan Siddhi** (Maharashtra), **Piplantri** (Rajasthan), and **Pothanikkad** (Kerala).
- **Multi-Temporal Imagery:** Calibrated Sentinel-2 MSI Level-2A surface reflectance data across temporal passes:
  - **Time T1:** Baseline / previous season pass (e.g., October 2025).
  - **Time T2:** Recent comparative pass (e.g., October 2026).
- **Interactive Map Controls:** Zoom, pan, village boundary GeoJSON overlays, layer opacity slider, and dynamic metadata inspection (Sensor, Resolution: 10m/px, Cloud cover %, Centroid coordinates).

### 🌿 Module B & E: OpenCV Vegetation Intelligence (NDVI, NDRE, NDWI, SAVI)
- **Spectral Index Engine:** Safe mathematical calculation using Sentinel-2 spectral bands:
  - **NDVI** = $(NIR - RED) / (NIR + RED)$ (Sentinel-2 Band 8 and Band 4)
  - **NDRE** = $(NIR - RED\_EDGE) / (NIR + RED\_EDGE)$ (Band 8 and Band 5)
  - **NDWI** = $(GREEN - NIR) / (GREEN + NIR)$ (Band 3 and Band 8)
  - **SAVI** = $[(NIR - RED) / (NIR + RED + 0.5)] \times 1.5$ (Soil-Adjusted Vegetation Index)
- **Health Classification Zones:**
  - **High Health (0.66–1.00):** Emerald Green (`#16a34a`)
  - **Medium Health (0.40–0.66):** Yellow-Green (`#84cc16`)
  - **Low Health (0.20–0.40):** Orange (`#eab308`)
  - **Very Low / Harvest Stress (0.00–0.20):** Red (`#ef4444`)
  - **Water / Non-vegetated (< 0.00):** Blue (`#3b82f6`)
- **OpenCV Computer Vision Pipeline:**
  - Bilateral edge-preserving filter and Gaussian smoothing.
  - Sub-pixel image registration using OpenCV ECC (`cv2.findTransformECC`).
  - Stress hotspot detection using morphological opening/closing and contour extraction (`cv2.findContours`). Identifies cluster centroids, physical areas, and severity levels.
  - Histogram distribution (16 bins) for visual frequency analytics.

### 🧠 Module C: Deep Learning Land Cover Segmentation (PyTorch U-Net)
- **Neural Network Architecture:** Custom PyTorch U-Net with DoubleConv encoder blocks, bottleneck, skip connections, upsampling decoders, and a 6-class segmentation head.
- **5 Classified Classes:**
  1. **Agricultural Land** (Farmland / Active crops)
  2. **Trees / Forest** (Canopy, Orchards, Agroforestry)
  3. **Water Bodies** (Ponds, Reservoirs, Streams, Check dams)
  4. **Built-up Areas** (Settlements, Roads, Farm structures)
  5. **Bare Soil** (Fallow, Barren ground, Exposed soil)
- **Training Pipeline (`ml/src/train.py`):**
  - Combined loss: $0.6 \times \text{CrossEntropy} + 0.4 \times \text{DiceLoss}$.
  - Geographically separated splits (Train: 100 patches, Val: 50 patches, Test: 50 patches) strictly preventing spatial data leakage.
  - Data augmentations: Horizontal/vertical flips, 90° rotations, subtle sensor noise.
  - Model checkpoint saved at: `ml/models/checkpoints/best_unet_landcover.pth`.
- **Evaluation Performance (`ml/src/evaluate.py`):**
  - **Overall Pixel Accuracy:** `97.36%`
  - **Mean IoU (mIoU):** `0.8787`
  - **Macro F1-Score:** `0.9285`
  - **Macro Precision:** `0.9108`
  - **Macro Recall:** `0.9536`
  - Confusion matrix saved to `ml/outputs/evaluation/confusion_matrix.png`.

### ⏱️ Module D: Temporal Change Detection & Built-up Expansion
- **Multi-Temporal Differencing:** $\Delta \text{NDVI} = \text{NDVI}(T_2) - \text{NDVI}(T_1)$.
- **Change Classifications:**
  - Significant Vegetation Increase ($\Delta \ge +0.25$)
  - Moderate Vegetation Increase ($+0.10 \le \Delta < +0.25$)
  - Stable Vegetation ($-0.10 < \Delta < +0.10$)
  - Moderate Vegetation Decrease ($-0.25 < \Delta \le -0.10$)
  - Significant Vegetation Decrease ($\Delta \le -0.25$)
- **Interactive Swipe Comparison Slider:** Drag-and-compare visual interface comparing baseline T1 against current T2.
- **Deep Learning Built-up Expansion Tracking:** Pixel transitions from non-built-up in T1 to built-up in T2.
- **Physical Geospatial Area Calculations:** Accurate physical land areas in hectares calculated from 10m native spatial resolution ($10\text{m} \times 10\text{m} = 100\text{m}^2 = 0.01\text{ ha}$ per pixel).

### 📊 Module F & Reports: AI Analysis & Document Generation
- **Automated AI Agronomic Insights:** Synthesizes observations, interpretations, and prioritized field interventions.
- **Export Capabilities:**
  - **CSV Report:** Detailed tabular metrics, class breakdowns, and hotspot coordinates.
  - **PDF Report:** Multi-page report generated via ReportLab with executive tables, land cover statistics, and methodological notes.

### 💧 Preserved Water Modules
- All previous water intelligence capabilities remain 100% operational:
  - `GET /water/forecast`: XGBoost demand forecasting.
  - `POST /water/risk/predict`: Random forest pressure risk scoring.
  - `GET /water/resources/`: OpenStreetMap water infrastructure mapping.

---

## 🏗️ Repository Architecture

```
GRAMTWIN/
├── backend/
│   ├── main.py                          # FastAPI application & route registration
│   ├── routes/
│   │   ├── satellite.py                 # Village metadata, GeoJSON, image passes
│   │   ├── vegetation.py                # NDVI, NDRE, NDWI, SAVI, health zones
│   │   ├── landcover.py                 # U-Net land cover inference & status
│   │   ├── change_detection.py          # Temporal T1 vs T2 comparison
│   │   ├── analytics.py                 # Metric cards, trends, AI insights
│   │   ├── reports.py                   # PDF and CSV download endpoints
│   │   ├── water.py                     # Preserved water forecast routes
│   │   ├── water_resources.py           # Preserved OSM resource routes
│   │   └── water_risk.py                # Preserved water risk routes
│   ├── services/
│   │   ├── cv_pipeline.py               # Modular OpenCV filters, colormaps, contours
│   │   ├── vegetation_service.py        # Spectral index engine & hotspot analysis
│   │   ├── landcover_service.py         # PyTorch inference wrapper
│   │   ├── change_detection_service.py  # Temporal differencing & built-up tracking
│   │   ├── ai_analysis_service.py       # Factual findings & agronomic recommendations
│   │   ├── report_service.py            # ReportLab PDF & CSV generation
│   │   ├── water_service.py             # Preserved water service
│   │   └── water_risk_service.py        # Preserved water risk service
│   ├── data/
│   │   ├── villages/                    # GeoJSON boundaries & metadata
│   │   └── satellite_imagery/           # Multi-spectral Sentinel-2 rasters (T1, T2)
│   └── tests/
│       └── test_e2e_pipeline.py         # Automated integration test suite
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AgriDashboard.jsx        # Master agricultural dashboard
│   │   │   ├── AgriDashboard.css        # Professional dark navy & emerald styling
│   │   │   ├── SatelliteMapViewer.jsx   # Interactive Leaflet viewer & pixel inspector
│   │   │   ├── AnalyticsCards.jsx       # 8 KPI summary cards
│   │   │   ├── VegetationCharts.jsx     # Recharts histogram, pie, line charts
│   │   │   ├── TemporalComparisonPanel.jsx # Swipe comparison slider
│   │   │   ├── AIInsightsPanel.jsx      # AI findings & export controls
│   │   │   ├── Sidebar.jsx              # App navigation
│   │   │   ├── WaterForecast.jsx        # Preserved water forecast view
│   │   │   ├── WaterRisk.jsx            # Preserved water risk view
│   │   │   └── WaterResourcesMap.jsx    # Preserved OSM map view
│   │   ├── services/
│   │   │   └── api.js                   # Axios client for all API routes
│   │   ├── App.jsx                      # Main app shell & router
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── ml/
│   ├── src/
│   │   ├── unet.py                      # PyTorch U-Net architecture
│   │   ├── deeplabv3.py                 # DeepLabV3+ with ASPP
│   │   ├── dataset.py                   # PyTorch dataset & augmentation
│   │   ├── data_loader.py               # DataLoader factories
│   │   ├── preprocessing.py             # Geographically separated patch generator
│   │   ├── augmentation.py              # Geometric & spectral augmentations
│   │   ├── metrics.py                   # IoU, mIoU, Precision, Recall, F1, CM
│   │   ├── train.py                     # Full training loop & checkpointing
│   │   ├── evaluate.py                  # Test split evaluation & CM plotting
│   │   └── predict.py                   # Production inference engine
│   ├── models/checkpoints/              # Saved model weights (best_unet_landcover.pth)
│   ├── outputs/                         # Training curves, history & evaluation metrics
│   └── requirements.txt
├── requirements.txt                     # Python dependencies
├── .env.example                         # Environment configuration template
└── README.md
```

---

## 🚀 Running the Project Locally

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 2. Backend Setup
```bash
# In the root repository directory:
pip install -r requirements.txt

# Start the FastAPI backend:
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
Backend API will be accessible at: `http://127.0.0.1:8000`  
Interactive Swagger API docs: `http://127.0.0.1:8000/docs`

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open your browser at: `http://localhost:5173`

### 4. Running Model Training & Evaluation
To retrain or evaluate the U-Net model:
```bash
# Train U-Net model on satellite patches:
python ml/src/train.py

# Evaluate checkpoint on held-out test split:
python ml/src/evaluate.py
```

### 5. Running Automated Verification Suite
```bash
python backend/tests/test_e2e_pipeline.py
```

---

## 📡 Key API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/satellite/villages` | List available villages and metadata |
| `GET` | `/api/satellite/village/{id}/geojson` | Retrieve boundary GeoJSON |
| `GET` | `/api/satellite/images` | Query available Sentinel-2 acquisition dates |
| `POST` | `/api/vegetation/ndvi` | Compute NDVI, health zones, and stress hotspots |
| `POST` | `/api/vegetation/indices` | Calculate multi-index suite (NDVI, NDRE, NDWI, SAVI) |
| `POST` | `/api/landcover/predict` | Run PyTorch U-Net 5-class segmentation |
| `GET` | `/api/landcover/status` | Model architecture, weights, and test metrics |
| `POST` | `/api/change-detection/analyze` | Multi-temporal T1 vs T2 change analysis |
| `GET` | `/api/analytics/summary` | Top-level KPI cards data |
| `GET` | `/api/analytics/ai-insights` | Synthesized AI observations & recommendations |
| `GET` | `/api/reports/download/pdf` | Download formatted ReportLab PDF report |
| `GET` | `/api/reports/download/csv` | Download complete tabular CSV dataset |
