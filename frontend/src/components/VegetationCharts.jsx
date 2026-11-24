import React from "react";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    LineChart,
    Line,
    CartesianGrid,
    Legend
} from "recharts";
import { BarChart3, PieChart as PieIcon, Activity, TrendingUp } from "lucide-react";

function VegetationCharts({ vegData, lcData, trendsData }) {
    const distribution = vegData?.distribution || [];
    const categories = vegData?.categories || [];
    const classes = lcData?.classes || [];
    const trends = trendsData?.trends || [];

    return (
        <div className="side-analytics-container">
            {/* 1. NDVI DISTRIBUTION HISTOGRAM */}
            <div className="analytics-card">
                <h3>
                    <BarChart3 size={16} color="#10b981" />
                    NDVI Distribution Histogram
                </h3>
                <div style={{ height: 180, width: "100%" }}>
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={distribution} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                            <XAxis dataKey="bin" tick={{ fill: "#64748b", fontSize: 9 }} interval={2} />
                            <YAxis tick={{ fill: "#64748b", fontSize: 10 }} />
                            <Tooltip
                                contentStyle={{ background: "#0b141d", borderColor: "#10b981", borderRadius: 8, fontSize: 11, color: "#ecfdf5" }}
                                formatter={(val) => [`${val}%`, "Coverage"]}
                            />
                            <Bar dataKey="percentage" fill="#10b981" radius={[3, 3, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* 2. LAND COVER CLASSIFICATION BREAKDOWN */}
            <div className="analytics-card">
                <h3>
                    <PieIcon size={16} color="#38bdf8" />
                    Land Cover Distribution (U-Net AI)
                </h3>
                <div style={{ height: 180, width: "100%" }}>
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={classes}
                                dataKey="percentage"
                                nameKey="name"
                                cx="50%"
                                cy="50%"
                                innerRadius={42}
                                outerRadius={68}
                                paddingAngle={3}
                            >
                                {classes.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                            </Pie>
                            <Tooltip
                                contentStyle={{ background: "#0b141d", borderColor: "#38bdf8", borderRadius: 8, fontSize: 11, color: "#ecfdf5" }}
                                formatter={(val, name, item) => [`${val}% (${item.payload.area_ha} ha)`, name]}
                            />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginTop: "6px" }}>
                    {classes.map((c) => (
                        <div key={c.class_id} style={{ display: "flex", alignItems: "center", gap: "5px", fontSize: "10.5px", color: "#94a3b8" }}>
                            <div style={{ width: 8, height: 8, borderRadius: 2, background: c.color }}></div>
                            <span>{c.name}: <strong>{c.percentage}%</strong></span>
                        </div>
                    ))}
                </div>
            </div>

            {/* 3. VEGETATION HEALTH PROGRESS BARS */}
            <div className="analytics-card">
                <h3>
                    <Activity size={16} color="#f59e0b" />
                    Vegetation Health Zones
                </h3>
                <div className="health-bars-list">
                    {categories.map((cat, idx) => (
                        <div className="health-bar-item" key={idx}>
                            <div className="health-bar-header">
                                <span>{cat.name}</span>
                                <strong>{cat.percentage}% ({cat.area_ha} ha)</strong>
                            </div>
                            <div className="health-bar-track">
                                <div
                                    className="health-bar-fill"
                                    style={{ width: `${cat.percentage}%`, background: cat.color }}
                                ></div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* 4. HISTORICAL VEGETATION TREND DYNAMICS */}
            {trends.length > 0 && (
                <div className="analytics-card">
                    <h3>
                        <TrendingUp size={16} color="#34d399" />
                        Multi-Temporal Seasonal Trends
                    </h3>
                    <div style={{ height: 180, width: "100%" }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={trends} margin={{ top: 10, right: 15, left: -25, bottom: 0 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                                <XAxis dataKey="season" tick={{ fill: "#64748b", fontSize: 9 }} interval={1} />
                                <YAxis tick={{ fill: "#64748b", fontSize: 10 }} />
                                <Tooltip
                                    contentStyle={{ background: "#0b141d", borderColor: "#10b981", borderRadius: 8, fontSize: 11, color: "#ecfdf5" }}
                                />
                                <Line type="monotone" dataKey="veg_coverage_pct" name="Veg Coverage %" stroke="#10b981" strokeWidth={2} dot={{ r: 3 }} />
                                <Line type="monotone" dataKey="mean_ndvi" name="Mean NDVI" stroke="#38bdf8" strokeWidth={2} dot={{ r: 3 }} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            )}
        </div>
    );
}

export default VegetationCharts;
