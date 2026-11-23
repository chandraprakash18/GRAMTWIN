
import { useState } from "react";

import {
    ShieldCheck,
    AlertTriangle,
    Activity,
    Droplets,
    CloudRain,
    Thermometer,
    Sun,
    BrainCircuit,
    ArrowUpRight,
    RefreshCw,
    Gauge,
    Waves
} from "lucide-react";

import API from "../services/api";
import "./WaterRisk.css";

function WaterRisk() {

    const [formData, setFormData] = useState({
        daily_consumption: 41759,
        avg_temperature: 3.1583,
        daily_rain: 1,
        daily_sun_total: 7,
        avg_sun: 0.291667,
        hourly_records: 24,
        month: 1,
        day_of_week: 4
    });

    const [riskData, setRiskData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [alertHistory, setAlertHistory] = useState([]);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: Number(e.target.value)
        });
    };

    const handlePrediction = async (e) => {
        e.preventDefault();

        setLoading(true);
        setError("");

        try {
            const response = await API.post(
                "/water/risk/predict",
                formData
            );

           setRiskData(response.data);

setAlertHistory((previous) => [
    {
        risk_level: response.data.risk_level,
        confidence: response.data.confidence,
        date: new Date().toLocaleString("en-IN", {
            day: "2-digit",
            month: "short",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit"
        })
    },
    ...previous
].slice(0, 5));

        } catch (err) {
            console.error("Water risk error:", err);
            setError("Unable to generate risk assessment. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    const riskColors = {
        Low: "#4ade80",
        Medium: "#fbbf24",
        High: "#fb7185"
    };

    const riskColor = riskData
        ? riskColors[riskData.risk_level]
        : "#94a3b8";

    const recommendations = {
        Low: "Demand pressure is relatively low. Continue monitoring daily consumption.",
        Medium: "Demand pressure is elevated. Monitor consumption and review water conservation practices.",
        High: "Demand pressure is high. Prioritise demand monitoring and consider water conservation measures."
    };

const alertDetails = {
    Low: {
        title: "Normal Monitoring",
        severity: "LOW PRIORITY",
        message: "Water demand pressure is currently within the lower historical range.",
        actions: [
            "Continue routine water consumption monitoring.",
            "Maintain regular water conservation practices.",
            "Review daily demand trends."
        ],
        color: "#4ade80"
    },

    Medium: {
        title: "Water Conservation Advisory",
        severity: "MEDIUM PRIORITY",
        message: "Elevated demand pressure has been detected by the prediction model.",
        actions: [
            "Monitor daily water consumption closely.",
            "Identify opportunities to reduce unnecessary water usage.",
            "Review rainfall and temperature trends."
        ],
        color: "#fbbf24"
    },

    High: {
        title: "Priority Demand Alert",
        severity: "HIGH PRIORITY",
        message: "The model has classified the current inputs as high demand pressure.",
        actions: [
            "Prioritise monitoring of water demand.",
            "Review available water conservation measures.",
            "Inspect reported consumption for unusual increases."
        ],
        color: "#fb7185"
    }
};

const currentAlert = riskData
    ? alertDetails[riskData.risk_level]
    : null;
  
    const historicalRiskDistribution = [
    {
        level: "Low",
        count: 915,
        percentage: 50,
        color: "#4ade80"
    },
    {
        level: "Medium",
        count: 640,
        percentage: 34.97,
        color: "#fbbf24"
    },
    {
        level: "High",
        count: 275,
        percentage: 15.03,
        color: "#fb7185"
    }
];

    return (
        <section className="water-risk-page">

            {/* SECTION HEADER */}
            <div className="risk-heading">

                <div>
                    <span className="risk-eyebrow">
                        INTELLIGENT RESOURCE MONITORING
                    </span>

                    <h2>Water Risk & Alerts</h2>

                    <p>
                        Machine learning powered water demand pressure assessment.
                    </p>
                </div>

                <div className="risk-engine-badge">
                    <BrainCircuit size={17} />
                    <span>Random Forest Engine</span>
                </div>

            </div>

            {/* CURRENT RISK BANNER */}
            <div
                className="risk-status-banner"
                style={{
                    "--risk-color": riskColor
                }}
            >

                <div className="risk-status-icon">
                    {riskData?.risk_level === "High"
                        ? <AlertTriangle size={24} />
                        : <ShieldCheck size={24} />
                    }
                </div>

                <div className="risk-status-content">
                    <span>WATER DEMAND PRESSURE STATUS</span>

                    <h3>
                        {riskData
                            ? `${riskData.risk_level.toUpperCase()} RISK`
                            : "ASSESSMENT PENDING"}
                    </h3>

                    <p>
                        {riskData
                            ? recommendations[riskData.risk_level]
                            : "Enter the available data and run an assessment to view the predicted risk."}
                    </p>
                </div>

                <div className="risk-status-indicator">
                    <span></span>
                    {riskData ? "Assessment Complete" : "Awaiting Input"}
                </div>

            </div>

            {/* MAIN DASHBOARD GRID */}
            <div className="risk-dashboard-grid">

                {/* LEFT: INPUT PANEL */}
                <div className="risk-input-panel">

                    <div className="risk-panel-heading">
                        <div className="risk-panel-icon">
                            <Activity size={18} />
                        </div>

                        <div>
                            <h3>Assessment Inputs</h3>
                            <p>Enter daily water and weather data</p>
                        </div>
                    </div>

                    <form onSubmit={handlePrediction}>

                        <div className="risk-input-grid">

                            <label>
                                <span>
                                    <Droplets size={14} />
                                    Daily Consumption
                                </span>

                                <input
                                    type="number"
                                    name="daily_consumption"
                                    value={formData.daily_consumption}
                                    onChange={handleChange}
                                    min="0"
                                    required
                                />
                            </label>

                            <label>
                                <span>
                                    <Thermometer size={14} />
                                    Temperature
                                </span>

                                <input
                                    type="number"
                                    name="avg_temperature"
                                    value={formData.avg_temperature}
                                    onChange={handleChange}
                                    step="0.01"
                                    required
                                />
                            </label>

                            <label>
                                <span>
                                    <CloudRain size={14} />
                                    Daily Rainfall
                                </span>

                                <input
                                    type="number"
                                    name="daily_rain"
                                    value={formData.daily_rain}
                                    onChange={handleChange}
                                    min="0"
                                    step="0.1"
                                    required
                                />
                            </label>

                            <label>
                                <span>
                                    <Sun size={14} />
                                    Total Sunlight
                                </span>

                                <input
                                    type="number"
                                    name="daily_sun_total"
                                    value={formData.daily_sun_total}
                                    onChange={handleChange}
                                    min="0"
                                    step="0.1"
                                    required
                                />
                            </label>

                            <label>
                                <span>
                                    <Sun size={14} />
                                    Average Sunlight
                                </span>

                                <input
                                    type="number"
                                    name="avg_sun"
                                    value={formData.avg_sun}
                                    onChange={handleChange}
                                    min="0"
                                    step="0.01"
                                    required
                                />
                            </label>

                            <label>
                                <span>
                                    <Waves size={14} />
                                    Hourly Records
                                </span>

                                <input
                                    type="number"
                                    name="hourly_records"
                                    value={formData.hourly_records}
                                    onChange={handleChange}
                                    min="1"
                                    required
                                />
                            </label>

                            <label>
                                <span>
                                    <Activity size={14} />
                                    Month
                                </span>

                                <input
                                    type="number"
                                    name="month"
                                    value={formData.month}
                                    onChange={handleChange}
                                    min="1"
                                    max="12"
                                    required
                                />
                            </label>

                            <label>
                                <span>
                                    <Gauge size={14} />
                                    Day of Week
                                </span>

                                <input
                                    type="number"
                                    name="day_of_week"
                                    value={formData.day_of_week}
                                    onChange={handleChange}
                                    min="0"
                                    max="6"
                                    required
                                />
                            </label>

                        </div>

                        <button
                            type="submit"
                            className="risk-predict-button"
                            disabled={loading}
                        >
                            {loading
                                ? <RefreshCw size={17} className="risk-spin" />
                                : <BrainCircuit size={17} />
                            }

                            {loading
                                ? "Analysing Data..."
                                : "Generate Risk Assessment"
                            }

                            {!loading && <ArrowUpRight size={17} />}
                        </button>

                    </form>

                    {error && (
                        <p className="risk-error">{error}</p>
                    )}

                    <div className="risk-input-note">
                        <Activity size={14} />
                        Prototype dataset inputs. Replace these sample values
                        with valid observations before interpreting predictions.
                    </div>

                </div>

                {/* RIGHT: RESULT PANEL */}
                <div className="risk-result-panel">

                    <div className="risk-panel-heading">
                        <div className="risk-panel-icon">
                            <ShieldCheck size={18} />
                        </div>

                        <div>
                            <h3>Risk Assessment</h3>
                            <p>Random Forest classification result</p>
                        </div>
                    </div>

                    <div className="risk-result-display">

                        <div
                            className="risk-gauge"
                            style={{
                                "--risk-color": riskColor,
                                "--risk-progress": riskData
                                    ? `${riskData.confidence}%`
                                    : "0%"
                            }}
                        >
                            <div className="risk-gauge-inner">
                                <span>
                                    {riskData
                                        ? `${riskData.confidence}%`
                                        : "--"}
                                </span>
                                <small>Confidence</small>
                            </div>
                        </div>

                        <div
                            className="risk-result-level"
                            style={{ color: riskColor }}
                        >
                            {riskData
                                ? `${riskData.risk_level} Risk`
                                : "No Prediction Yet"}
                        </div>

                        <p className="risk-result-description">
                            {riskData
                                ? "Model confidence for the predicted demand-pressure category."
                                : "Your model result will appear here after assessment."}
                        </p>

                    </div>

                    <div className="risk-model-info">

                        <div>
                            <span>ML Algorithm</span>
                            <strong>Random Forest</strong>
                        </div>

                        <div>
                            <span>Model Test Accuracy</span>
                            <strong>63.39%</strong>
                        </div>

                        <div>
                            <span>Prediction Type</span>
                            <strong>Demand Pressure</strong>
                        </div>

                    </div>

                </div>

            </div>

            {/* RISK LEVEL LEGEND */}
            <div className="risk-legend-panel">

                <div className="risk-legend-heading">
                    <div>
                        <h3>Risk Classification</h3>
                        <p>Historical consumption-based thresholds</p>
                    </div>
                </div>

                <div className="risk-legend-grid">

                    <div className="risk-legend-item low">
                        <span className="risk-legend-dot"></span>
                        <div>
                            <strong>Low Risk</strong>
                            <small>Up to 54,139</small>
                        </div>
                    </div>

                    <div className="risk-legend-item medium">
                        <span className="risk-legend-dot"></span>
                        <div>
                            <strong>Medium Risk</strong>
                            <small>54,140 – 61,398</small>
                        </div>
                    </div>

                    <div className="risk-legend-item high">
                        <span className="risk-legend-dot"></span>
                        <div>
                            <strong>High Risk</strong>
                            <small>Above 61,398</small>
                        </div>
                    </div>

                </div>

            </div>


{/* WATER RISK ALERT CENTRE */}
<div className="risk-alert-centre">

    <div className="risk-alert-heading">
        <div className="risk-panel-icon">
            <AlertTriangle size={18} />
        </div>

        <div>
            <h3>Water Risk Alert Centre</h3>
            <p>Recommended actions based on the latest ML prediction</p>
        </div>

        <span className="risk-alert-live">
            {riskData ? "ASSESSMENT ACTIVE" : "AWAITING RESULT"}
        </span>
    </div>

    {currentAlert ? (

        <div
            className="risk-alert-content"
            style={{ "--alert-color": currentAlert.color }}
        >

            <div className="risk-alert-summary">
                <div>
                    <span className="risk-alert-severity">
                        {currentAlert.severity}
                    </span>

                    <h4>{currentAlert.title}</h4>

                    <p>{currentAlert.message}</p>
                </div>

                <div className="risk-alert-symbol">
                    <AlertTriangle size={25} />
                </div>
            </div>

            <div className="risk-alert-actions-heading">
                Recommended Actions
            </div>

            <div className="risk-alert-actions">

                {currentAlert.actions.map((action, index) => (
                    <div className="risk-alert-action" key={index}>
                        <span>{String(index + 1).padStart(2, "0")}</span>
                        <p>{action}</p>
                    </div>
                ))}

            </div>

        </div>

    ) : (

        <div className="risk-alert-empty">
            <Activity size={20} />
            <span>
                Generate a risk assessment to view alerts and recommended actions.
            </span>
        </div>

    )}

</div>

{/* HISTORICAL RISK DISTRIBUTION */}
<div className="risk-distribution-panel">
    <div className="risk-distribution-heading">
        <div className="risk-panel-icon">
            <Activity size={18} />
        </div>
        <div>
            <h3>Historical Risk Distribution</h3>
            <p>Risk categories across the model training dataset</p>
        </div>
    </div>

    <div className="risk-distribution-list">
        {historicalRiskDistribution.map((item) => (
            <div className="risk-distribution-item" key={item.level}>
                <div className="risk-distribution-info">
                    <span>{item.level} Risk</span>
                    <strong>{item.count.toLocaleString()} records</strong>
                </div>

                <div className="risk-distribution-track">
                    <div
                        className="risk-distribution-fill"
                        style={{
                            width: `${item.percentage}%`,
                            background: item.color
                        }}
                    />
                </div>

                <span className="risk-distribution-percentage">
                    {item.percentage}%
                </span>
            </div>
        ))}
    </div>

    <p className="risk-distribution-note">
        This distribution represents historical training data, not live village measurements.
    </p>
</div>
{/* RECENT RISK ASSESSMENTS */}
<div className="risk-history-panel">

    <div className="risk-history-heading">
        <div>
            <h3>Recent Risk Assessments</h3>
            <p>Latest machine learning assessment activity</p>
        </div>

        <span className="risk-history-count">
            {alertHistory.length} Records
        </span>
    </div>

    {alertHistory.length > 0 ? (

        <div className="risk-history-list">

            {alertHistory.map((item, index) => {

                const color = {
                    Low: "#4ade80",
                    Medium: "#fbbf24",
                    High: "#fb7185"
                }[item.risk_level];

                return (
                    <div className="risk-history-item" key={index}>

                        <div
                            className="risk-history-dot"
                            style={{ background: color }}
                        />

                        <div className="risk-history-details">
                            <strong>
                                {item.risk_level} Risk
                            </strong>

                            <span>{item.date}</span>
                        </div>

                        <div className="risk-history-confidence">
                            {item.confidence}%
                        </div>

                    </div>
                );
            })}

        </div>

    ) : (

        <div className="risk-history-empty">
            <Activity size={20} />
            <span>
                No previous assessments. Your predictions will appear here.
            </span>
        </div>

    )}

</div>

            {/* FOOTER NOTE */}
            <div className="risk-disclaimer">
                <AlertTriangle size={15} />
                <span>
                    Prototype assessment based on historical water consumption
                    and weather patterns. It does not measure actual water
                    availability or confirm water shortages.
                </span>
            </div>

        </section>
    );
}

export default WaterRisk;
