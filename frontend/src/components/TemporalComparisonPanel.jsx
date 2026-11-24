import React, { useState, useRef } from "react";
import {
    SplitSquareVertical,
    TrendingUp,
    TrendingDown,
    Building2,
    Calendar,
    ArrowRight
} from "lucide-react";

function TemporalComparisonPanel({ changeData }) {
    const [sliderPos, setSliderPos] = useState(50);
    const [isDragging, setIsDragging] = useState(false);
    const containerRef = useRef(null);

    if (!changeData) return null;

    const stats = changeData.stats;
    const t1 = changeData.t1;
    const t2 = changeData.t2;
    const overlays = changeData.overlays;

    const handleMouseMove = (e) => {
        if (!isDragging || !containerRef.current) return;
        const rect = containerRef.current.getBoundingClientRect();
        const offsetX = e.clientX - rect.left;
        const newPos = Math.max(0, Math.min(100, (offsetX / rect.width) * 100));
        setSliderPos(newPos);
    };

    const handleTouchMove = (e) => {
        if (!containerRef.current) return;
        const rect = containerRef.current.getBoundingClientRect();
        const touch = e.touches[0];
        const offsetX = touch.clientX - rect.left;
        const newPos = Math.max(0, Math.min(100, (offsetX / rect.width) * 100));
        setSliderPos(newPos);
    };

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            {/* COMPARISON HEADER BAR */}
            <div style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                background: "rgba(11, 20, 29, 0.85)",
                border: "1px solid rgba(16, 185, 129, 0.2)",
                borderRadius: "12px",
                padding: "14px 20px",
                flexWrap: "wrap",
                gap: "12px"
            }}>
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                    <Calendar size={18} color="#10b981" />
                    <span style={{ color: "#ecfdf5", fontWeight: "600", fontSize: "14px" }}>
                        Time T1: <span style={{ color: "#38bdf8" }}>{t1?.date}</span>
                    </span>
                    <ArrowRight size={16} color="#64748b" />
                    <span style={{ color: "#ecfdf5", fontWeight: "600", fontSize: "14px" }}>
                        Time T2: <span style={{ color: "#34d399" }}>{t2?.date}</span>
                    </span>
                </div>

                <div style={{ display: "flex", gap: "16px", fontSize: "12px" }}>
                    <span style={{ color: "#94a3b8" }}>
                        Net Veg Change: <strong style={{ color: stats.net_vegetation_change_ha >= 0 ? "#10b981" : "#ef4444" }}>
                            {stats.net_vegetation_change_ha > 0 ? `+${stats.net_vegetation_change_ha}` : stats.net_vegetation_change_ha} ha ({stats.net_vegetation_change_pct}%)
                        </strong>
                    </span>
                    <span style={{ color: "#94a3b8" }}>
                        Built-Up Expansion: <strong style={{ color: "#e11d48" }}>+{stats.builtup_increase_ha} ha</strong>
                    </span>
                </div>
            </div>

            {/* SWIPE COMPARISON SLIDER */}
            <div
                className="swipe-container"
                ref={containerRef}
                onMouseMove={handleMouseMove}
                onMouseDown={() => setIsDragging(true)}
                onMouseUp={() => setIsDragging(false)}
                onMouseLeave={() => setIsDragging(false)}
                onTouchMove={handleTouchMove}
            >
                {/* Background Image: Time T2 (Recent) */}
                <img
                    src={overlays.t2_rgb}
                    alt="Time T2 Recent Satellite"
                    className="swipe-image"
                />

                {/* Foreground Clipped Image: Time T1 (Previous) */}
                <div
                    style={{
                        position: "absolute",
                        top: 0,
                        left: 0,
                        height: "100%",
                        width: `${sliderPos}%`,
                        overflow: "hidden",
                        zIndex: 2
                    }}
                >
                    <img
                        src={overlays.t1_rgb}
                        alt="Time T1 Previous Satellite"
                        style={{
                            width: containerRef.current ? `${containerRef.current.clientWidth}px` : "100%",
                            height: "100%",
                            objectFit: "contain",
                            maxWidth: "none"
                        }}
                    />
                </div>

                {/* Vertical Divider Slider Bar */}
                <div
                    className="swipe-slider-bar"
                    style={{ left: `${sliderPos}%` }}
                >
                    <div className="swipe-handle">
                        <SplitSquareVertical size={16} />
                    </div>
                </div>

                {/* Labels */}
                <div style={{
                    position: "absolute",
                    top: "16px",
                    left: "16px",
                    zIndex: 5,
                    background: "rgba(0,0,0,0.75)",
                    border: "1px solid #38bdf8",
                    color: "#38bdf8",
                    padding: "4px 10px",
                    borderRadius: "6px",
                    fontSize: "11px",
                    fontWeight: "600"
                }}>
                    T1: Previous Season ({t1?.date})
                </div>

                <div style={{
                    position: "absolute",
                    top: "16px",
                    right: "16px",
                    zIndex: 5,
                    background: "rgba(0,0,0,0.75)",
                    border: "1px solid #10b981",
                    color: "#34d399",
                    padding: "4px 10px",
                    borderRadius: "6px",
                    fontSize: "11px",
                    fontWeight: "600"
                }}>
                    T2: Recent Comparative ({t2?.date})
                </div>
            </div>

            {/* CHANGE CATEGORIES BREAKDOWN */}
            <div style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
                gap: "12px"
            }}>
                {changeData.categories.map((c, i) => (
                    <div
                        key={i}
                        style={{
                            background: "rgba(11, 20, 29, 0.75)",
                            border: `1px solid ${c.color}33`,
                            borderRadius: "10px",
                            padding: "12px",
                            borderLeft: `4px solid ${c.color}`
                        }}
                    >
                        <div style={{ fontSize: "11px", color: "#94a3b8", marginBottom: "4px" }}>{c.name}</div>
                        <div style={{ fontSize: "18px", fontWeight: "700", color: "#ecfdf5" }}>{c.percentage}%</div>
                        <div style={{ fontSize: "11px", color: "#64748b" }}>{c.area_ha} ha ({c.range})</div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default TemporalComparisonPanel;
