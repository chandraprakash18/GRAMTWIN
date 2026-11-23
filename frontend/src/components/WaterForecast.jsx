
import "./WaterForecast.css";
import {
    CalendarDays,
    TrendingUp,
    TrendingDown,
    Activity
} from "lucide-react";
import { useEffect, useState } from "react";
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Legend
} from "recharts";

import API from "../services/api";
function AnimatedNumber({ value, duration = 1500 }) {
    const [count, setCount] = useState(0);

    useEffect(() => {
        let startTime;
        let animationFrame;

        const animate = (timestamp) => {
            if (!startTime) startTime = timestamp;

            const progress = Math.min(
                (timestamp - startTime) / duration,
                1
            );

            const easeOut = 1 - Math.pow(1 - progress, 4);

            setCount(value * easeOut);

            if (progress < 1) {
                animationFrame = requestAnimationFrame(animate);
            }
        };

        setCount(0);
        animationFrame = requestAnimationFrame(animate);

        return () => cancelAnimationFrame(animationFrame);
    }, [value, duration]);

    return (
        <span>
            {Math.round(count).toLocaleString("en-US")}
        </span>
    );
}

function WaterForecast() {

    const [predictions, setPredictions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [comparisonData, setComparisonData] = useState([]);

  useEffect(() => {

    const fetchData = async () => {
        try {
            const [forecastResponse, comparisonResponse] = await Promise.all([
                API.get("/water/forecast?days=7"),
                API.get("/water/comparison")
            ]);

            setPredictions(forecastResponse.data.predictions);
            setComparisonData(comparisonResponse.data);

        } catch (err) {
            console.error("Dashboard data error:", err);
            setError("Unable to fetch water dashboard data.");

        } finally {
            setLoading(false);
        }
    };

    fetchData();

}, []);
    if (loading) {
    return (
        <div className="water-loading-screen">
            <div className="loading-glow"></div>

            <div className="loading-ring">
                <div className="loading-ring-inner">
                    <Activity size={34} color="#4ade80" />
                </div>
            </div>

            <h2>Analyzing Water Demand</h2>

            <p>
                Processing forecast data and preparing insights...
            </p>

            <div className="loading-progress">
                <div className="loading-progress-bar"></div>
            </div>

            <span className="loading-status">
                GRAMTWIN INTELLIGENCE SYSTEM
            </span>
        </div>
    );
}

    if (error) return <p>{error}</p>;

    if (predictions.length === 0) {
        return <p>No forecast data available.</p>;
    }

    const values = predictions.map(
        (item) => item.predicted_consumption
    );

    const averageDemand =
        values.reduce((sum, value) => sum + value, 0) / values.length;

    const maximumDemand = Math.max(...values);
    const minimumDemand = Math.min(...values);
    const lastHistoricalDate = "2021-01-04";

const forecastStartDate = predictions[0].date;

const forecastEndDate = predictions[predictions.length - 1].date;

    const cardStyle = {
        background: "linear-gradient(145deg, #101d16, #0b120e)",
        padding: "23px",
        borderRadius: "15px",
        border: "1px solid rgba(74, 222, 128, 0.14)",
        boxShadow: "0 8px 30px rgba(0,0,0,0.18)",
        transition: "all 0.3s ease"
    };

    const headingStyle = {
        fontSize: "12px",
        color: "#8fa797",
        marginBottom: "15px",
        fontWeight: 500,
        letterSpacing: "0.4px"
    };

    const valueStyle = {
        fontSize: "27px",
        color: "#e8f5ec",
        margin: 0,
        fontWeight: 700,
        letterSpacing: "-0.7px"
    };

   return (
    <div className="water-forecast" style={{ padding: "20px" }}>

            <h2>7-Day Water Demand Forecast</h2>

            {/* KPI Cards */}
            <div style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                gap: "20px",
                marginBottom: "30px"
            }}>

 {/* Forecast Period */}
                <div className="water-kpi-card" style={cardStyle}>
    <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: "18px"
    }}>
        <h3 style={headingStyle}>Forecast Period</h3>
        <CalendarDays size={22} color="#4ade80" />
    </div>

    <h2 style={valueStyle}>
        {predictions.length} Days
    </h2>
</div>

<div className="water-kpi-card" style={cardStyle}>
    <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: "18px"
    }}>
        <h3 style={headingStyle}>Average Demand</h3>
        <Activity size={22} color="#20d6bd" />
    </div>

    <h2 style={valueStyle}>
       <AnimatedNumber value={averageDemand} />
    </h2>
</div>

            <div className="water-kpi-card" style={cardStyle}>
    <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: "18px"
    }}>
        <h3 style={headingStyle}>Maximum Demand</h3>
        <TrendingUp size={22} color="#fbbf24" />
    </div>

    <h2 style={valueStyle}>
       <AnimatedNumber value={maximumDemand} />
    </h2>
</div>
              <div className="water-kpi-card" style={cardStyle}>
    <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: "18px"
    }}>
        <h3 style={headingStyle}>Minimum Demand</h3>
        <TrendingDown size={22} color="#60a5fa" />
    </div>

    <h2 style={valueStyle}>
       <AnimatedNumber value={minimumDemand} />
    </h2>
</div>
 </div>  {/* This closes the KPI Cards grid */}           

{/* Forecast Date Range */}
<div className="water-date-panel" style={{
    background: "linear-gradient(135deg, #0d1b13, #10251a)",
    padding: "20px 24px",
    borderRadius: "14px",
    marginBottom: "25px",
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
    gap: "15px",
    border: "1px solid rgba(74, 222, 128, 0.16)",
    boxShadow: "0 8px 25px rgba(0, 0, 0, 0.15)",
    color: "#e8f5ec"
}}>

    <div>
        <p style={{ color: "#8fa797", fontSize: "13px" }}>
            Last Historical Data
        </p>
        <h3>04 January 2021</h3>
    </div>

    <div>
        <p style={{ color: "#8fa797", fontSize: "13px" }}>
            Forecast Starts
        </p>
        <h3>{forecastStartDate}</h3>
    </div>

    <div>
        <p style={{ color: "#8fa797", fontSize: "13px" }}>
            Forecast Ends
        </p>
        <h3>{forecastEndDate}</h3>
    </div>

</div>

{/* Forecast Information */}
<div style={{
    background: "linear-gradient(145deg, #0d1b13, #101d16)",
    padding: "22px",
    borderRadius: "14px",
    border: "1px solid rgba(74, 222, 128, 0.14)",
    boxShadow: "0 8px 25px rgba(0, 0, 0, 0.15)",
    marginBottom: "25px",
    color: "#e8f5ec"
}}>

    <h3 style={{
    color: "#e8f5ec",
    marginBottom: "18px",
    fontSize: "17px"
}}>
    Forecast Information
</h3>

    <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
        gap: "20px"
    }}>

        <div>
<p style={{ color: "#8fa797", fontSize: "13px" }}>                Forecasting Model
            </p>
            <h3>XGBoost</h3>
        </div>

        <div>
<p style={{ color: "#8fa797", fontSize: "13px" }}>                Forecast Period
            </p>
            <h3>7 Days</h3>
        </div>

        <div>
<p style={{ color: "#8fa797", fontSize: "13px" }}>                Data Source
            </p>
            <h3>Historical Dataset</h3>
        </div>

        <div>
<p style={{ color: "#8fa797", fontSize: "13px" }}>
                    Data Status
            </p>
           <h3 style={{ color: "#fbbf24" }}>
    Prototype Data
</h3>
        </div>

    </div>
</div>

           
{/* Forecast Chart */}
<div className="water-chart-card" style={{
    background: "linear-gradient(145deg, #0d1b13, #101d16)",
    padding: "24px",
    borderRadius: "16px",
    border: "1px solid rgba(74, 222, 128, 0.14)",
    boxShadow: "0 8px 25px rgba(0, 0, 0, 0.15)",
    height: "400px",
    marginBottom: "25px",
    color: "#e8f5ec"
}}>
    <h3 style={{
    color: "#e8f5ec",
    fontSize: "17px",
    marginBottom: "15px"
}}>
    7-Day Water Demand Trend
</h3>

                <ResponsiveContainer width="100%" height="100%">
                   <LineChart data={predictions}>
    <CartesianGrid
        strokeDasharray="3 3"
        stroke="rgba(148, 163, 184, 0.12)"
    />
    <XAxis
    dataKey="date"
    tickFormatter={(date) => {
        const formattedDate = new Date(date);
        return formattedDate.toLocaleDateString("en-GB", {
            day: "2-digit",
            month: "short"
        });
    }}
    tick={{ fill: "#8fa797", fontSize: 11 }}
    axisLine={{ stroke: "#304438" }}
    tickLine={false}
/>
   <YAxis
    tickFormatter={(value) => value.toLocaleString("en-US")}
    tick={{ fill: "#8fa797", fontSize: 11 }}
    axisLine={false}
    tickLine={false}
/>
    <Tooltip
    formatter={(value) => [
        Number(value).toLocaleString("en-US", {
            maximumFractionDigits: 2
        }),
        "Predicted Demand"
    ]}
    contentStyle={{
        background: "#10251a",
        border: "1px solid rgba(74, 222, 128, 0.2)",
        borderRadius: "10px",
        color: "#e8f5ec"
    }}
    labelStyle={{ color: "#4ade80" }}
/>

    <Line
        type="monotone"
        dataKey="predicted_consumption"
        stroke="#4ade80"
        strokeWidth={3}
        dot={{ r: 4, fill: "#4ade80" }}
        activeDot={{ r: 7 }}
        name="Predicted Consumption"
    />
</LineChart>
                </ResponsiveContainer>

            </div>
           
          
{/* Actual vs Predicted Chart */}
<div className="water-chart-card" style={{
    background: "linear-gradient(145deg, #0d1b13, #101d16)",
    padding: "24px",
    borderRadius: "16px",
    border: "1px solid rgba(74, 222, 128, 0.14)",
    boxShadow: "0 8px 25px rgba(0, 0, 0, 0.15)",
    height: "450px",
    marginTop: "25px",
    color: "#e8f5ec"
}}>

                <h3 style={{
    color: "#e8f5ec",
    fontSize: "17px",
    marginBottom: "15px"
}}>
    Actual vs Predicted Water Demand
</h3>

                <ResponsiveContainer width="100%" height="90%">
                    <LineChart data={comparisonData}>
    <CartesianGrid
        strokeDasharray="3 3"
        stroke="rgba(148, 163, 184, 0.12)"
    />

    <XAxis
    dataKey="date"
    tickFormatter={(date) => {
        const formattedDate = new Date(date);
        return formattedDate.toLocaleDateString("en-GB", {
            day: "2-digit",
            month: "short"
        });
    }}
    tick={{ fill: "#8fa797", fontSize: 11 }}
    axisLine={{ stroke: "#304438" }}
    tickLine={false}
/>

    <YAxis
    tickFormatter={(value) => value.toLocaleString("en-US")}
    tick={{ fill: "#8fa797", fontSize: 11 }}
    axisLine={false}
    tickLine={false}
/>

    <Tooltip
    formatter={(value, name) => [
        Number(value).toLocaleString("en-US", {
            maximumFractionDigits: 2
        }),
        name
    ]}
    contentStyle={{
        background: "#10251a",
        border: "1px solid rgba(74, 222, 128, 0.2)",
        borderRadius: "10px",
        color: "#e8f5ec"
    }}
    labelStyle={{ color: "#4ade80" }}
/>

    <Legend
        wrapperStyle={{
            color: "#e8f5ec",
            fontSize: "12px"
        }}
    />

    <Line
        type="monotone"
        dataKey="actual"
        stroke="#20d6bd"
        strokeWidth={2}
        dot={false}
        name="Actual Demand"
    />

    <Line
        type="monotone"
        dataKey="xgboost_predicted"
        stroke="#4ade80"
        strokeWidth={2}
        dot={false}
        name="XGBoost Predicted"
    />
</LineChart>
                               </ResponsiveContainer>

            </div>

            {/* Forecast Insights */}
          

{/* Forecast Insights */}

<div className="water-insights-card" style={{
    background: "linear-gradient(145deg, #0d1b13, #101d16)",
    padding: "26px",
    borderRadius: "18px",
    border: "1px solid rgba(74, 222, 128, 0.18)",
    boxShadow: "0 12px 35px rgba(0, 0, 0, 0.22)",
    marginTop: "25px",
    color: "#e8f5ec"
}}>

    <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: "25px",
        flexWrap: "wrap",
        gap: "12px"
    }}>
        <div>
            <h3 style={{ fontSize: "19px", margin: 0 }}>
                Forecast Insights
            </h3>
            <p style={{
                color: "#8fa797",
                fontSize: "12px",
                marginTop: "6px"
            }}>
                AI-powered demand intelligence
            </p>
        </div>

        <span style={{
            fontSize: "10px",
            color: "#4ade80",
            background: "rgba(74, 222, 128, 0.09)",
            border: "1px solid rgba(74, 222, 128, 0.2)",
            padding: "7px 12px",
            borderRadius: "20px",
            letterSpacing: "1px"
        }}>
            XGBOOST MODEL
        </span>
    </div>

    <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
        gap: "18px"
    }}>

        {/* Average Demand */}
        <div className="insight-metric-card">
            <span className="insight-label">AVERAGE PREDICTED DEMAND</span>

            <h2 className="insight-value">
                <AnimatedNumber value={averageDemand} />
            </h2>

            <p className="insight-description">
                Expected daily demand across 7 days
            </p>

            <div className="insight-accent average-accent"></div>
        </div>

        {/* Highest Demand */}
        <div className="insight-metric-card">
            <span className="insight-label">HIGHEST DEMAND</span>

            <h2 className="insight-value">
                <AnimatedNumber value={maximumDemand} />
            </h2>

            <p className="insight-description">
                Peak predicted demand in the forecast
            </p>

            <div className="insight-accent maximum-accent"></div>
        </div>

        {/* Lowest Demand */}
        <div className="insight-metric-card">
            <span className="insight-label">LOWEST DEMAND</span>

            <h2 className="insight-value">
                <AnimatedNumber value={minimumDemand} />
            </h2>

            <p className="insight-description">
                Minimum predicted demand in the forecast
            </p>

            <div className="insight-accent minimum-accent"></div>
        </div>

    </div>

    <div className="insight-footer">
        <Activity size={17} color="#4ade80" />

        <p>
            These insights summarize the seven-day XGBoost water
            demand forecast using historical dataset patterns.
        </p>
    </div>

</div>
</div>

    );
}

export default WaterForecast;
