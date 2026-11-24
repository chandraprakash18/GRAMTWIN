import axios from "axios";

// In dev mode with Vite proxy, use relative path so requests avoid CORS and host issues.
// Fallback to direct backend URL if called outside Vite proxy.
const getBaseURL = () => {
    if (typeof window !== "undefined") {
        if (window.location.port === "5173") {
            return ""; // Uses Vite proxy
        }
        return `http://${window.location.hostname}:8000`;
    }
    return "http://127.0.0.1:8000";
};

const API = axios.create({
    baseURL: getBaseURL(),
    headers: {
        "Content-Type": "application/json",
    },
});

export const satelliteAPI = {
    getVillages: () => API.get("/api/satellite/villages"),
    getVillageGeoJSON: (villageId) => API.get(`/api/satellite/village/${villageId}/geojson`),
    getAvailableImages: (villageId) => API.get(`/api/satellite/images?village_id=${villageId}`),
    uploadImage: (formData) => API.post("/api/satellite/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" }
    })
};

export const vegetationAPI = {
    analyzeNDVI: (villageId, timeTag = "t2", aoiBbox = null) =>
        API.post("/api/vegetation/ndvi", { village_id: villageId, time_tag: timeTag, aoi_bbox: aoiBbox }),
    getSpectralIndices: (villageId, timeTag = "t2") =>
        API.post("/api/vegetation/indices", { village_id: villageId, time_tag: timeTag })
};

export const landcoverAPI = {
    predict: (villageId, timeTag = "t2") =>
        API.post("/api/landcover/predict", { village_id: villageId, time_tag: timeTag }),
    getModelStatus: () => API.get("/api/landcover/status")
};

export const changeDetectionAPI = {
    analyze: (villageId, t1Date = "2025-10-15", t2Date = "2026-10-18") =>
        API.post("/api/change-detection/analyze", { village_id: villageId, t1_date: t1Date, t2_date: t2Date })
};

export const analyticsAPI = {
    getSummary: (villageId) => API.get(`/api/analytics/summary?village_id=${villageId}`),
    getLandcover: (villageId) => API.get(`/api/analytics/landcover?village_id=${villageId}`),
    getVegetationTrends: (villageId) => API.get(`/api/analytics/vegetation-trends?village_id=${villageId}`),
    getAIInsights: (villageId) => API.get(`/api/analytics/ai-insights?village_id=${villageId}`)
};

export const reportsAPI = {
    getCSVUrl: (villageId) => `${getBaseURL()}/api/reports/download/csv?village_id=${villageId}`,
    getPDFUrl: (villageId) => `${getBaseURL()}/api/reports/download/pdf?village_id=${villageId}`
};

export default API;
