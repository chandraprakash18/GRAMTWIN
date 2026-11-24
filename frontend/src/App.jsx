import { useState } from "react";
import Sidebar from "./components/Sidebar";
import AgriDashboard from "./components/AgriDashboard";
import WaterForecast from "./components/WaterForecast";
import WaterRisk from "./components/WaterRisk";
import WaterResourcesMap from "./components/WaterResourcesMap";

import {
    Activity,
    CalendarDays,
    ChevronRight,
    Droplets,
    Leaf,
    Map,
    Satellite,
    Sprout
} from "lucide-react";

import "./App.css";

function App() {
    const [activePage, setActivePage] = useState("Satellite & Vegetation");

    const currentDate = new Date().toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "long",
        year: "numeric"
    });

    const isAgriPage = activePage === "Satellite & Vegetation" || activePage === "Overview";
    const isResourcesPage = activePage === "Water Resources";
    const isWaterPage = activePage === "Water Intelligence";

    const getPageTitle = () => {
        if (isAgriPage) return "Satellite & Vegetation Intelligence";
        if (isResourcesPage) return "Water Resources Infrastructure";
        return "Water Intelligence & Demand Forecasting";
    };

    const getPageDescription = () => {
        if (isAgriPage) {
            return "AI-powered Sentinel-2 satellite imagery monitoring, NDVI vegetation health, U-Net land cover, and temporal change detection.";
        }
        if (isResourcesPage) {
            return "Explore the geographical distribution of village water resources from OpenStreetMap.";
        }
        return "AI-powered water consumption forecasting and historical performance analysis.";
    };

    const getSectionIcon = () => {
        if (isAgriPage) return <Satellite size={14} />;
        if (isResourcesPage) return <Map size={14} />;
        return <Droplets size={14} />;
    };

    return (
        <div className="dashboard-layout">
            <Sidebar
                activePage={activePage}
                onNavigate={setActivePage}
            />

            <main className="dashboard-main">
                {/* TOP HEADER */}
                <header className="dashboard-header">
                    <div className="header-left">
                        <div className="header-breadcrumb">
                            <span>GRAMTWIN AI</span>
                            <ChevronRight size={14} />
                            <span className="breadcrumb-active">{getPageTitle()}</span>
                        </div>

                        <h1>{getPageTitle()}</h1>
                        <p>{getPageDescription()}</p>
                    </div>

                    <div className="header-right">
                        <div className="header-date">
                            <CalendarDays size={16} />
                            <span>{currentDate}</span>
                        </div>

                        <div className="header-status">
                            <span className="header-status-dot"></span>
                            <span>System Operational</span>
                        </div>

                        <div className="header-profile">
                            <Leaf size={19} />
                        </div>
                    </div>
                </header>

                {/* PAGE CONTENT */}
                <div className="dashboard-content">
                    <div className="page-intro">
                        <div>
                            <div className="section-label">
                                {getSectionIcon()}
                                {isAgriPage ? "SATELLITE & VEGETATION INTELLIGENCE" : isResourcesPage ? "WATER RESOURCE MAPPING" : "WATER RESOURCE MODULE"}
                            </div>

                            <h2>
                                {isAgriPage ? "Village Satellite Analytics" : isResourcesPage ? "Village Water Infrastructure" : "Water Demand Analytics"}
                            </h2>

                            <p>{getPageDescription()}</p>
                        </div>

                        <div className="module-indicator">
                            <Activity size={16} />
                            <span>
                                {isAgriPage ? "Deep Learning U-Net Active" : isResourcesPage ? "OpenStreetMap Connected" : "Forecasting Engine"}
                            </span>
                        </div>
                    </div>

                    {isAgriPage && <AgriDashboard />}

                    {isResourcesPage && <WaterResourcesMap />}

                    {isWaterPage && (
                        <>
                            <WaterForecast />
                            <WaterRisk />
                        </>
                    )}
                </div>
            </main>
        </div>
    );
}

export default App;
