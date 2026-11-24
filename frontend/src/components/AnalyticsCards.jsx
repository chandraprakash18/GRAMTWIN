import React from "react";
import {
    Trees,
    Activity,
    AlertCircle,
    Droplets,
    Building2,
    TrendingUp,
    TrendingDown,
    Globe
} from "lucide-react";

function AnalyticsCards({ summaryData }) {
    if (!summaryData) return null;

    const cards = [
        {
            label: "Total Village Area",
            value: `${summaryData.total_area_ha} ha`,
            subtext: "Geospatial boundary extent",
            icon: Globe,
            color: "#38bdf8"
        },
        {
            label: "Vegetation Coverage",
            value: `${summaryData.vegetation_coverage_pct}%`,
            subtext: "Total active vegetative surface",
            icon: Trees,
            color: "#22c55e"
        },
        {
            label: "Healthy Canopy",
            value: `${summaryData.healthy_vegetation_pct}%`,
            subtext: "NDVI range: 0.66 - 1.00",
            icon: Activity,
            color: "#10b981"
        },
        {
            label: "Moisture / Stress",
            value: `${summaryData.stressed_vegetation_pct}%`,
            subtext: "NDVI range: 0.00 - 0.40",
            icon: AlertCircle,
            color: "#f59e0b"
        },
        {
            label: "Water Coverage",
            value: `${summaryData.water_area_ha} ha`,
            subtext: `${summaryData.water_coverage_pct}% of total area`,
            icon: Droplets,
            color: "#3b82f6"
        },
        {
            label: "Built-up Settlements",
            value: `${summaryData.builtup_area_ha} ha`,
            subtext: `${summaryData.builtup_pct}% (expansion: +${summaryData.builtup_increase_ha} ha)`,
            icon: Building2,
            color: "#ef4444"
        },
        {
            label: "Vegetation Gain",
            value: `+${summaryData.vegetation_gain_pct}%`,
            subtext: "Parcels with NDVI change >= +0.10",
            icon: TrendingUp,
            color: "#16a34a"
        },
        {
            label: "Vegetation Loss",
            value: `-${summaryData.vegetation_loss_pct}%`,
            subtext: "Harvested or stressed parcels",
            icon: TrendingDown,
            color: "#ea580c"
        }
    ];

    return (
        <div className="stat-cards-grid">
            {cards.map((c, idx) => {
                const Icon = c.icon;
                return (
                    <div className="agri-stat-card" key={idx}>
                        <div className="stat-header">
                            <span className="stat-label">{c.label}</span>
                            <div className="stat-icon" style={{ color: c.color }}>
                                <Icon size={18} />
                            </div>
                        </div>
                        <div className="stat-value">{c.value}</div>
                        <div className="stat-subtext">{c.subtext}</div>
                    </div>
                );
            })}
        </div>
    );
}

export default AnalyticsCards;
