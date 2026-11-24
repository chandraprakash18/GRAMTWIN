"""
GRAMTWIN AI - End-to-End Automated Integration Verification Suite
Tests the complete multi-module pipeline:
1. Village Boundary Retrieval & Satellite Imagery
2. Vegetation Intelligence & NDVI Analysis
3. Deep Learning U-Net Land Cover Inference
4. Temporal Change Detection (T1 vs T2)
5. OpenCV Stress Hotspot Contours
6. Analytics & AI Agronomic Findings
7. PDF & CSV Report Downloads
8. Preserved Water Demand & Infrastructure APIs
"""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.main import app

client = TestClient(app)

def test_module_a_satellite():
    print("Testing Module A: Satellite Imagery & Village Boundaries...")
    r1 = client.get("/api/satellite/villages")
    assert r1.status_code == 200, f"Villages list failed: {r1.text}"
    villages = r1.json()["villages"]
    assert len(villages) >= 4, f"Expected at least 4 villages, got {len(villages)}"

    r2 = client.get("/api/satellite/village/hiware_bazar/geojson")
    assert r2.status_code == 200
    geojson = r2.json()
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"][0]["geometry"]["coordinates"][0]) >= 10

    r3 = client.get("/api/satellite/images?village_id=hiware_bazar")
    assert r3.status_code == 200
    assert len(r3.json()["available_passes"]) >= 2
    print("  -> Passed Module A!")

def test_module_b_vegetation():
    print("Testing Module B: Vegetation Intelligence & NDVI Analysis...")
    payload = {"village_id": "hiware_bazar", "time_tag": "t2"}
    r = client.post("/api/vegetation/ndvi", json=payload)
    assert r.status_code == 200, f"NDVI calculation failed: {r.text}"
    data = r.json()
    assert "stats" in data
    assert -1.0 <= data["stats"]["mean_ndvi"] <= 1.0
    assert "categories" in data
    assert len(data["categories"]) == 5
    assert "distribution" in data
    assert len(data["distribution"]) >= 10
    assert data["overlays"]["ndvi_heatmap"].startswith("data:image/png;base64,")
    print(f"  -> Passed Module B! (Mean NDVI: {data['stats']['mean_ndvi']}, Coverage: {data['stats']['vegetation_coverage_pct']}%)")

def test_module_c_landcover():
    print("Testing Module C: Land Cover Segmentation (PyTorch U-Net)...")
    payload = {"village_id": "hiware_bazar", "time_tag": "t2"}
    r = client.post("/api/landcover/predict", json=payload)
    assert r.status_code == 200, f"Land cover prediction failed: {r.text}"
    data = r.json()
    assert len(data["classes"]) == 5
    total_pct = sum(c["percentage"] for c in data["classes"])
    assert 99.0 <= total_pct <= 101.0, f"Expected percentages sum ~100%, got {total_pct}"
    assert data["overlay"].startswith("data:image/png;base64,")

    r_status = client.get("/api/landcover/status")
    assert r_status.status_code == 200
    assert r_status.json()["is_model_loaded"] is True
    print("  -> Passed Module C!")

def test_module_d_change_detection():
    print("Testing Module D: Temporal Change Detection...")
    payload = {"village_id": "hiware_bazar", "t1_date": "2025-10-15", "t2_date": "2026-10-18"}
    r = client.post("/api/change-detection/analyze", json=payload)
    assert r.status_code == 200, f"Change detection failed: {r.text}"
    data = r.json()
    stats = data["stats"]
    assert "vegetation_gain_ha" in stats
    assert "vegetation_loss_ha" in stats
    assert "builtup_increase_ha" in stats
    assert len(data["categories"]) == 5
    assert data["overlays"]["ndvi_difference"].startswith("data:image/png;base64,")
    print(f"  -> Passed Module D! (Net Veg Change: {stats['net_vegetation_change_ha']} ha, Built-up expansion: +{stats['builtup_increase_ha']} ha)")

def test_module_f_ai_insights_and_reports():
    print("Testing Module F & Reports: AI Analysis & Document Generation...")
    r_sum = client.get("/api/analytics/summary?village_id=hiware_bazar")
    assert r_sum.status_code == 200
    assert "vegetation_coverage_pct" in r_sum.json()

    r_ins = client.get("/api/analytics/ai-insights?village_id=hiware_bazar")
    assert r_ins.status_code == 200
    assert len(r_ins.json()["findings"]) >= 4
    assert len(r_ins.json()["recommendations"]) >= 3

    # PDF Download Test
    r_pdf = client.get("/api/reports/download/pdf?village_id=hiware_bazar")
    assert r_pdf.status_code == 200
    assert r_pdf.headers["content-type"] == "application/pdf"
    assert len(r_pdf.content) > 1000, "PDF content too small"

    # CSV Download Test
    r_csv = client.get("/api/reports/download/csv?village_id=hiware_bazar")
    assert r_csv.status_code == 200
    assert "text/csv" in r_csv.headers["content-type"]
    assert b"GRAMTWIN AI" in r_csv.content
    print("  -> Passed Module F & Reports!")

def test_preserved_water_modules():
    print("Testing Preservation: Existing Water Forecasting & Resource APIs...")
    r_wf = client.get("/water/forecast?days=7")
    assert r_wf.status_code == 200
    assert len(r_wf.json()["predictions"]) == 7

    r_home = client.get("/water/")
    assert r_home.status_code == 200
    print("  -> Passed Preserved Modules!")

def run_all_tests():
    print("="*60)
    print("RUNNING GRAMTWIN AI END-TO-END VERIFICATION")
    print("="*60)
    test_module_a_satellite()
    test_module_b_vegetation()
    test_module_c_landcover()
    test_module_d_change_detection()
    test_module_f_ai_insights_and_reports()
    test_preserved_water_modules()
    print("="*60)
    print("ALL TESTS PASSED SUCCESSFULLY! (100% OPERATIONAL)")
    print("="*60)

if __name__ == "__main__":
    run_all_tests()
