import React from "react";
import {
    Sparkles,
    CheckCircle2,
    AlertTriangle,
    FileText,
    Download,
    Cpu,
    ExternalLink
} from "lucide-react";
import { reportsAPI } from "../services/api";

function AIInsightsPanel({ insightsData, villageId }) {
    if (!insightsData) return null;

    const findings = insightsData.findings || [];
    const recommendations = insightsData.recommendations || [];

    const handleDownloadCSV = () => {
        window.open(reportsAPI.getCSVUrl(villageId), "_blank");
    };

    const handleDownloadPDF = () => {
        window.open(reportsAPI.getPDFUrl(villageId), "_blank");
    };

    return (
        <div className="ai-insights-box">
            {/* HEADER & EXPORT ACTIONS */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "18px", flexWrap: "wrap", gap: "12px" }}>
                <div>
                    <h3>
                        <Sparkles size={18} color="#10b981" />
                        AI Geospatial Intelligence & Agronomic Recommendations
                    </h3>
                    <p style={{ margin: "0", fontSize: "12px", color: "#829588" }}>
                        Synthesized from calibrated Sentinel-2 reflectance, PyTorch U-Net segmentation, and multi-temporal change detection.
                    </p>
                </div>

                <div style={{ display: "flex", gap: "10px" }}>
                    <button className="report-btn csv" onClick={handleDownloadCSV}>
                        <Download size={14} />
                        Download CSV Report
                    </button>
                    <button className="report-btn pdf" onClick={handleDownloadPDF}>
                        <FileText size={14} />
                        Download PDF Report
                    </button>
                </div>
            </div>

            {/* FINDINGS GRID */}
            <div className="findings-grid">
                {findings.map((f, idx) => (
                    <div className="finding-card" key={idx}>
                        <div className="finding-type">{f.type}</div>
                        <div className="finding-title">{f.category}</div>
                        <p className="finding-desc" style={{ marginBottom: "8px" }}>
                            <strong style={{ color: "#ecfdf5" }}>Observation: </strong>
                            {f.observation}
                        </p>
                        <p className="finding-desc" style={{ color: "#34d399", fontSize: "11.5px" }}>
                            <strong>Analysis: </strong>
                            {f.interpretation}
                        </p>
                    </div>
                ))}
            </div>

            {/* ACTIONABLE RECOMMENDATIONS */}
            <div style={{ marginTop: "24px" }}>
                <h4 style={{ color: "#ecfdf5", fontSize: "13px", marginBottom: "12px", textTransform: "uppercase", letterSpacing: "0.5px" }}>
                    Actionable Agronomic & Watershed Interventions
                </h4>
                <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                    {recommendations.map((r, i) => (
                        <div
                            key={i}
                            style={{
                                display: "flex",
                                alignItems: "flex-start",
                                gap: "12px",
                                background: "rgba(11, 20, 29, 0.75)",
                                border: "1px solid rgba(255, 255, 255, 0.05)",
                                borderRadius: "8px",
                                padding: "12px"
                            }}
                        >
                            <span
                                style={{
                                    padding: "3px 8px",
                                    borderRadius: "4px",
                                    fontSize: "10px",
                                    fontWeight: "700",
                                    background: r.priority === "High" ? "rgba(239, 68, 68, 0.2)" : r.priority === "Medium" ? "rgba(245, 158, 11, 0.2)" : "rgba(16, 185, 129, 0.2)",
                                    color: r.priority === "High" ? "#ef4444" : r.priority === "Medium" ? "#f59e0b" : "#10b981",
                                    alignSelf: "flex-start"
                                }}
                            >
                                {r.priority} Priority
                            </span>
                            <div>
                                <strong style={{ color: "#ecfdf5", fontSize: "12.5px" }}>{r.action}</strong>
                                <p style={{ margin: "4px 0 0 0", fontSize: "12px", color: "#94a3b8" }}>{r.details}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* METHODOLOGY NOTE */}
            <div style={{ marginTop: "16px", padding: "10px 14px", background: "rgba(15, 23, 42, 0.6)", borderRadius: "8px", fontSize: "11px", color: "#64748b" }}>
                <strong>Methodological Transparency: </strong>
                {insightsData.methodology_note}
            </div>
        </div>
    );
}

export default AIInsightsPanel;
