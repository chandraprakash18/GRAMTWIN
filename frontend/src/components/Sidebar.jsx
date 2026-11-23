
import {
    LayoutDashboard,
    Droplets,
    Map,
    Sprout,
    Zap,
    Users,
    Settings,
    ChevronRight,
    Leaf,
    Activity
} from "lucide-react";

import "./Sidebar.css";

function Sidebar({ activePage, onNavigate }) {

    const menuItems = [
        {
            name: "Overview",
            icon: LayoutDashboard,
            section: "GENERAL"
        },
        {
            name: "Water Intelligence",
            icon: Droplets,
            section: "RESOURCES"
        },
        {
            name: "Water Resources",
            icon: Map,
            section: "RESOURCES"
        },
        {
            name: "Agriculture",
            icon: Sprout,
            section: "RESOURCES"
        },
        {
            name: "Energy",
            icon: Zap,
            section: "RESOURCES"
        },
        {
            name: "Population",
            icon: Users,
            section: "RESOURCES"
        }
    ];

    return (
        <aside className="sidebar">

            {/* Brand */}
            <div className="sidebar-brand">

                <div className="brand-icon">
                    <Leaf size={23} />
                </div>

                <div className="brand-details">
                    <h2>
                        GRAM<span>TWIN</span>
                    </h2>
                    <p>DIGITAL TWIN PLATFORM</p>
                </div>

            </div>

            <div className="sidebar-divider"></div>

            {/* Navigation */}
            <nav className="sidebar-navigation">

                <p className="menu-heading">GENERAL</p>

                {menuItems
                    .filter(item => item.section === "GENERAL")
                    .map(item => {
                        const Icon = item.icon;

                        return (
                            <div
                                className={`menu-item ${
                                    activePage === item.name ? "active" : ""
                                }`}
                                key={item.name}
                                onClick={() => onNavigate(item.name)}
                            >
                                <Icon size={19} />
                                <span>{item.name}</span>
                            </div>
                        );
                    })}

                <p className="menu-heading resources-heading">
                    RESOURCE INTELLIGENCE
                </p>

                {menuItems
                    .filter(item => item.section === "RESOURCES")
                    .map(item => {
                        const Icon = item.icon;

                        return (
                            <div
                                key={item.name}
                                className={`menu-item ${
                                    activePage === item.name ? "active" : ""
                                }`}
                                onClick={() => {
                                    if (
                                        item.name === "Water Intelligence" ||
                                        item.name === "Water Resources"
                                    ) {
                                        onNavigate(item.name);
                                    }
                                }}
                            >
                                <Icon size={19} />
                                <span>{item.name}</span>

                                {activePage === item.name && (
                                    <ChevronRight
                                        size={16}
                                        className="menu-arrow"
                                    />
                                )}
                            </div>
                        );
                    })}

            </nav>

            {/* Bottom section */}
            <div className="sidebar-bottom">

                <div className="system-status">
                    <div className="status-icon">
                        <Activity size={17} />
                    </div>

                    <div>
                        <h4>System Status</h4>
                        <p>
                            <span className="status-dot"></span>
                            Prototype Active
                        </p>
                    </div>
                </div>

                <div className="sidebar-divider"></div>

                <div className="sidebar-settings">
                    <Settings size={18} />
                    <span>Settings</span>
                </div>

                <div className="sidebar-footer">
                    <p>POWERED BY GRAMTWIN</p>
                    <span>Version 2.0.0</span>
                </div>

            </div>

        </aside>
    );
}

export default Sidebar;
