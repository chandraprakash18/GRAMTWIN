import React, { useState, useEffect, useCallback } from "react";
import {
    satelliteAPI,
    vegetationAPI,
    landcoverAPI,
    changeDetectionAPI,
    analyticsAPI,
    reportsAPI
} from "../services/api";

import SatelliteMapViewer from "./SatelliteMapViewer";
import AnalyticsCards from "./AnalyticsCards";
import VegetationCharts from "./VegetationCharts";
import TemporalComparisonPanel from "./TemporalComparisonPanel";
import AIInsightsPanel from "./AIInsightsPanel";

import {
    Map,
    SplitSquareVertical,
    Sparkles,
    Calendar,
    Satellite,
    FileSpreadsheet,
    FileText,
    RefreshCw,
    AlertCircle,
    CheckCircle2
} from "lucide-react";

import "./AgriDashboard.css";

const DEFAULT_VILLAGES = [
    {
        id: "hiware_bazar",
        name: "Hiware Bazar",
        district: "Ahilyanagar",
        state: "Maharashtra",
        center: [19.06861, 74.60111],
        bbox: [74.582, 19.052, 74.620, 19.085],
        total_area_ha: 976.8
    },
    {
        id: "ralegan_siddhi",
        name: "Ralegan Siddhi",
        district: "Ahilyanagar",
        state: "Maharashtra",
        center: [18.9182, 74.3941],
        bbox: [74.375, 18.902, 74.412, 18.935],
        total_area_ha: 982.4
    },
    {
        id: "piplantri",
        name: "Piplantri",
        district: "Rajsamand",
        state: "Rajasthan",
        center: [25.0772, 73.8641],
        bbox: [73.845, 25.060, 73.882, 25.095],
        total_area_ha: 1150.0
    },
    {
        id: "pothanikkad",
        name: "Pothanikkad",
        district: "Ernakulam",
        state: "Kerala",
        center: [10.0210, 76.6025],
        bbox: [76.585, 10.005, 76.620, 10.038],
        total_area_ha: 1850.5
    }
];

function AgriDashboard() {
    const [villages, setVillages] = useState(DEFAULT_VILLAGES);
    const [selectedVillageId, setSelectedVillageId] = useState("hiware_bazar");
    const [timeTag, setTimeTag] = useState("t2");
    const [activeTab, setActiveTab] = useState("viewer"); // "viewer" | "temporal" | "insights"
    const [activeLayer, setActiveLayer] = useState("ndvi_heatmap");
    const [opacity, setOpacity] = useState(0.85);

    // Analytical state
    const [geojson, setGeojson] = useState(null);
    const [vegData, setVegData] = useState(null);
    const [lcData, setLcData] = useState(null);
    const [changeData, setChangeData] = useState(null);
    const [summaryData, setSummaryData] = useState(null);
    const [trendsData, setTrendsData] = useState(null);
    const [insightsData, setInsightsData] = useState(null);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [backendConnected, setBackendConnected] = useState(false);

    // Fetch villages from backend
    useEffect(() => {
        satelliteAPI.getVillages()
            .then(res => {
                if (res.data?.villages?.length > 0) {
                    setVillages(res.data.villages);
                }
            })
            .catch(err => {
                console.warn("Using default villages list (backend may still be connecting):", err.message);
            });
    }, []);

    // Main data loading function
    const loadDashboardData = useCallback(() => {
        setLoading(true);
        setError("");

        Promise.allSettled([
            satelliteAPI.getVillageGeoJSON(selectedVillageId),
            vegetationAPI.analyzeNDVI(selectedVillageId, timeTag),
            landcoverAPI.predict(selectedVillageId, timeTag),
            changeDetectionAPI.analyze(selectedVillageId),
            analyticsAPI.getSummary(selectedVillageId),
            analyticsAPI.getVegetationTrends(selectedVillageId),
            analyticsAPI.getAIInsights(selectedVillageId)
        ])
            .then(([geoRes, vegRes, lcRes, chRes, sumRes, trendRes, insRes]) => {
                let anySuccess = false;

                if (geoRes.status === "fulfilled") {
                    setGeojson(geoRes.value.data);
                    anySuccess = true;
                }
                if (vegRes.status === "fulfilled") {
                    setVegData(vegRes.value.data);
                    anySuccess = true;
                }
                if (lcRes.status === "fulfilled") {
                    setLcData(lcRes.value.data);
                    anySuccess = true;
                }
                if (chRes.status === "fulfilled") {
                    setChangeData(chRes.value.data);
                    anySuccess = true;
                }
                if (sumRes.status === "fulfilled") {
                    setSummaryData(sumRes.value.data);
                    anySuccess = true;
                }
                if (trendRes.status === "fulfilled") {
                    setTrendsData(trendRes.value.data);
                    anySuccess = true;
                }
                if (insRes.status === "fulfilled") {
                    setInsightsData(insRes.value.data);
                    anySuccess = true;
                }

                setBackendConnected(anySuccess);

                if (!anySuccess) {
                    setError("Unable to connect to FastAPI backend at http://127.0.0.1:8000. Please start the backend server.");
                } else {
                    setError("");
                }
                setLoading(false);
            })
            .catch(err => {
                console.error("Dashboard data load error:", err);
                setError("Backend connection error. Please verify the FastAPI backend is running on http://127.0.0.1:8000.");
                setLoading(false);
                setBackendConnected(false);
            });
    }, [selectedVillageId, timeTag]);

    useEffect(() => {
        loadDashboardData();
    }, [loadDashboardData]);

    const currentVillage = villages.find(v => v.id === selectedVillageId) || villages[0] || DEFAULT_VILLAGES[0];

    return (
        <div className="agri-dashboard">
            {/* TOP CONTROLS BAR */}
            <div className="agri-topbar">
                <div className="topbar-left">
                    {/* Village Dropdown Selector */}
                    <div className="village-select-wrapper">
                        <Map size={16} color="#10b981" />
                        <select
                            value={selectedVillageId}
                            onChange={(e) => setSelectedVillageId(e.target.value)}
                        >
                            {villages.map(v => (
                                <option key={v.id} value={v.id}>
                                    {v.name} ({v.district}, {v.state})
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Pass Selector */}
                    <div className="pass-selector">
                        <button
                            className={`pass-btn ${timeTag === "t1" ? "active" : ""}`}
                            onClick={() => setTimeTag("t1")}
                        >
                            T1: Oct 2025
                        </button>
                        <button
                            className={`pass-btn ${timeTag === "t2" ? "active" : ""}`}
                            onClick={() => setTimeTag("t2")}
                        >
                            T2: Oct 2026 (Recent)
                        </button>
                    </div>

                    {/* View Mode Navigation Tabs */}
                    <div className="pass-selector">
                        <button
                            className={`pass-btn ${activeTab === "viewer" ? "active" : ""}`}
                            onClick={() => setActiveTab("viewer")}
                        >
                            Interactive Map & Indices
                        </button>
                        <button
                            className={`pass-btn ${activeTab === "temporal" ? "active" : ""}`}
                            onClick={() => setActiveTab("temporal")}
                        >
                            Temporal Comparison (Swipe)
                        </button>
                        <button
                            className={`pass-btn ${activeTab === "insights" ? "active" : ""}`}
                            onClick={() => setActiveTab("insights")}
                        >
                            AI Insights & Reports
                        </button>
                    </div>
                </div>

                <div className="topbar-right">
                    <a
                        href={reportsAPI.getCSVUrl(selectedVillageId)}
                        className="report-btn csv"
                        target="_blank"
                        rel="noreferrer"
                    >
                        <FileSpreadsheet size={14} />
                        CSV Export
                    </a>
                    <a
                        href={reportsAPI.getPDFUrl(selectedVillageId)}
                        className="report-btn pdf"
                        target="_blank"
                        rel="noreferrer"
                    >
                        <FileText size={14} />
                        PDF Report
                    </a>
                </div>
            </div>

            {/* SATELLITE METADATA STRIP */}
            <div className="sat-meta-strip">
                <div className="meta-pill">
                    <Satellite size={15} color="#10b981" />
                    <span>Sensor: <strong>{vegData?.satellite || "Sentinel-2 MSI (Level-2A)"}</strong></span>
                </div>
                <div className="meta-pill">
                    <span>Acquisition: <strong>{vegData?.date || (timeTag === "t1" ? "2025-10-15" : "2026-10-18")}</strong></span>
                </div>
                <div className="meta-pill">
                    <span>Spatial Resolution: <strong>10m / Pixel</strong></span>
                </div>
                <div className="meta-pill">
                    <span>Cloud Cover: <strong>{vegData?.cloud_percentage ?? (timeTag === "t1" ? 0.4 : 0.8)}%</strong></span>
                </div>
                <div className="meta-pill">
                    <span>Center: <strong>{currentVillage?.center?.[0]}° N, {currentVillage?.center?.[1]}° E</strong></span>
                </div>
                <span className="meta-source-tag">COPERNICUS DATA SPACE</span>
            </div>

            {/* ERROR / BACKEND OFFLINE BANNER WITH RETRY */}
            {error && (
                <div style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    background: "rgba(239, 68, 68, 0.15)",
                    border: "1px solid #ef4444",
                    borderRadius: "10px",
                    padding: "12px 18px",
                    color: "#fca5a5",
                    fontSize: "13px",
                    flexWrap: "wrap",
                    gap: "10px"
                }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                        <AlertCircle size={18} color="#ef4444" />
                        <span>{error}</span>
                    </div>
                    <button
                        onClick={loadDashboardData}
                        style={{
                            display: "flex",
                            alignItems: "center",
                            gap: "6px",
                            background: "#ef4444",
                            border: "none",
                            color: "white",
                            padding: "6px 14px",
                            borderRadius: "6px",
                            fontSize: "12px",
                            fontWeight: "600",
                            cursor: "pointer"
                        }}
                    >
                        <RefreshCw size={14} />
                        Retry Connection
                    </button>
                </div>
            )}

            {/* STAT METRIC CARDS */}
            <AnalyticsCards summaryData={summaryData} />

            {/* MAIN TAB CONTENT */}
            {activeTab === "viewer" && (
                <div className="map-analytics-split">
                    <SatelliteMapViewer
                        village={currentVillage}
                        geojson={geojson}
                        activeLayer={activeLayer}
                        setActiveLayer={setActiveLayer}
                        timeTag={timeTag}
                        vegData={vegData}
                        lcData={lcData}
                        changeData={changeData}
                        opacity={opacity}
                        setOpacity={setOpacity}
                    />
                    <VegetationCharts
                        vegData={vegData}
                        lcData={lcData}
                        trendsData={trendsData}
                    />
                </div>
            )}

            {activeTab === "temporal" && (
                <TemporalComparisonPanel changeData={changeData} />
            )}

            {activeTab === "insights" && (
                <AIInsightsPanel
                    insightsData={insightsData}
                    villageId={selectedVillageId}
                />
            )}
        </div>
    );
}

export default AgriDashboard;
