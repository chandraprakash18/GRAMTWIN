
import { useState } from "react";
import WaterRisk from "./components/WaterRisk";
import Sidebar from "./components/Sidebar";
import WaterForecast from "./components/WaterForecast";
import WaterResourcesMap from "./components/WaterResourcesMap";

import {
    Activity,
    CalendarDays,
    ChevronRight,
    Droplets,
    Leaf,
    Map
} from "lucide-react";

import "./App.css";

function App() {

    const [activePage, setActivePage] = useState("Water Intelligence");

    const currentDate = new Date().toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "long",
        year: "numeric"
    });

    const isResourcesPage = activePage === "Water Resources";

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
                            <span>GRAMTWIN</span>
                            <ChevronRight size={14} />
                            <span className="breadcrumb-active">
                                {isResourcesPage
                                    ? "Water Resources"
                                    : "Water Intelligence"}
                            </span>
                        </div>

                        <h1>
                            {isResourcesPage
                                ? "Water Resources"
                                : "Water Intelligence"}
                        </h1>

                        <p>
                            Monitor, analyse and forecast village water resources.
                        </p>

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
                                {isResourcesPage
                                    ? <Map size={14} />
                                    : <Droplets size={14} />
                                }

                                {isResourcesPage
                                    ? "WATER RESOURCE MAPPING"
                                    : "WATER RESOURCE MODULE"}
                            </div>

                            <h2>
                                {isResourcesPage
                                    ? "Village Water Infrastructure"
                                    : "Water Demand Analytics"}
                            </h2>

                            <p>
                                {isResourcesPage
                                    ? "Explore the geographical distribution of village water resources."
                                    : "AI-powered water consumption forecasting and historical performance analysis."}
                            </p>
                        </div>

                        <div className="module-indicator">
                            <Activity size={16} />
                            <span>
                                {isResourcesPage
                                    ? "Resource Mapping"
                                    : "Forecasting Engine"}
                            </span>
                        </div>

                    </div>

                   {isResourcesPage ? (
    <WaterResourcesMap />
) : (
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
