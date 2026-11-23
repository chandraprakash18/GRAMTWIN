
import { useEffect, useState } from "react";

import {
    MapContainer,
    TileLayer,
    Marker,
    Popup,
    ZoomControl
} from "react-leaflet";

import MarkerClusterGroup from "react-leaflet-cluster";

import L from "leaflet";
import API from "../services/api";

import "leaflet/dist/leaflet.css";
import "react-leaflet-cluster/dist/assets/MarkerCluster.css";
import "react-leaflet-cluster/dist/assets/MarkerCluster.Default.css";
import "./WaterResourcesMap.css";

// Hiware Bazar, Maharashtra
const villagePosition = [19.06861, 74.60111];

const resourceIcon = new L.Icon({
    iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
    iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png",
    shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34]
});
// Category-specific water resource markers
const getResourceIcon = (category) => {

    const colors = {
        "Wells": "#38bdf8",
        "Ponds": "#20d6bd",
        "Reservoirs": "#a78bfa",
        "Check Dams": "#fbbf24",
        "Rivers & Canals": "#60a5fa"
    };

    const color = colors[category] || "#94a3b8";

    return L.divIcon({
        className: "custom-water-marker",
        html: `
            <div style="
                width: 16px;
                height: 16px;
                background: ${color};
                border: 2px solid white;
                border-radius: 50%;
                box-shadow: 0 2px 8px rgba(0,0,0,0.45);
            "></div>
        `,
        iconSize: [20, 20],
        iconAnchor: [10, 10],
        popupAnchor: [0, -10]
    });
};
function WaterResourcesMap() {

    const [selectedResource, setSelectedResource] = useState("All");
    const [resources, setResources] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    // Fetch real OpenStreetMap resources
    useEffect(() => {

        const fetchResources = async () => {

            try {
                const response = await API.get("/water/resources/");

                setResources(response.data.resources || []);

            } catch (err) {
                console.error("Water resources error:", err);
                setError("Unable to load mapped water resources.");
            } finally {
                setLoading(false);
            }
        };

        fetchResources();

    }, []);

    // Apply selected map filter
    const filteredResources = resources.filter(resource => {

        if (selectedResource === "All") {
            return true;
        }

        return resource.category === selectedResource;

    });

    const filterOptions = [
        "All",
        "Wells",
        "Ponds",
        "Reservoirs",
        "Check Dams",
        "Rivers & Canals"
    ];

    return (
        <div className="water-resources-page">

            {/* Page Heading */}
            <div className="resources-heading">
                <div>
                    <h2>Village Water Resources</h2>
                    <p>
                        Explore mapped water infrastructure around Hiware Bazar
                    </p>
                </div>

                <span className="map-status">OPENSTREETMAP DATA</span>
            </div>

            {/* Map and Information Layout */}
            <div className="resources-dashboard">

                {/* Main Map */}
                <div className="water-map-section">

                    <div className="map-section-heading">
                        <div>
                            <h3>Interactive Village Map</h3>
                            <p>
                                {loading
                                    ? "Fetching mapped water resources..."
                                    : `${filteredResources.length} mapped resources displayed`}
                            </p>
                        </div>

                        <span>
                            {loading ? "LOADING..." : "MAP DATA CONNECTED"}
                        </span>
                    </div>

                    <div className="water-map-container">

                        <MapContainer
                            center={villagePosition}
                            zoom={15}
                            scrollWheelZoom={true}
                            zoomControl={false}
                            className="water-leaflet-map"
                        >

                            <TileLayer
                                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                            />

                            <ZoomControl position="bottomright" />

                            {/* Village Marker */}
                            <Marker
                                position={villagePosition}
                                icon={resourceIcon}
                            >
                                <Popup>
                                    <strong>Hiware Bazar</strong>
                                    <br />
                                    Prototype village location
                                </Popup>
                            </Marker>

                            {/* Actual OpenStreetMap Resources */}
                           {/* Grouped OpenStreetMap Resources */}
<MarkerClusterGroup chunkedLoading>

    {filteredResources.map(resource => (

        <Marker
            key={resource.id}
            position={[
                resource.latitude,
                resource.longitude
            ]}
            icon={getResourceIcon(resource.category)}
        >
            <Popup>
                <strong>
                    {resource.name || "Unnamed Water Resource"}
                </strong>

                <br />

                Category: {resource.category}

                <br />

                Source: {resource.source}

                <br />

                Coordinates:{" "}
                {Number(resource.latitude).toFixed(5)},
                {" "}
                {Number(resource.longitude).toFixed(5)}
            </Popup>
        </Marker>

    ))}

</MarkerClusterGroup>

                        </MapContainer>

                    </div>

                    <div className="map-coordinate-info">
                        <span>LAT: 19.06861°</span>
                        <span>LON: 74.60111°</span>
                    </div>

                    {loading && (
                        <p style={{ color: "#4ade80", fontSize: "12px" }}>
                            Loading water resources from OpenStreetMap...
                        </p>
                    )}

                    {error && (
                        <p style={{ color: "#f87171", fontSize: "12px" }}>
                            {error}
                        </p>
                    )}

                </div>

                {/* Right Information Panel */}
                <div className="resources-side-panel">

                    <div className="resource-side-card">

                        <h3>Map Layers</h3>

                        <p className="side-card-description">
                            Select a resource category
                        </p>

                        {filterOptions.map(item => (

                            <button
                                key={item}
                                className={`resource-layer-button ${
                                    selectedResource === item ? "active" : ""
                                }`}
                                onClick={() => setSelectedResource(item)}
                            >
                                <span>{item}</span>

                                <span className="layer-indicator">
                                    {selectedResource === item ? "●" : "○"}
                                </span>

                            </button>

                        ))}

                    </div>

                    <div className="resource-side-card">

                        <h3>Map Legend</h3>

                        <div className="legend-item">
                            <span className="legend-dot village-dot"></span>
                            Village Location
                        </div>

                        <div className="legend-item">
                            <span className="legend-dot well-dot"></span>
                            Wells
                        </div>

                        <div className="legend-item">
                            <span className="legend-dot pond-dot"></span>
                            Ponds
                        </div>

                        <div className="legend-item">
                            <span className="legend-dot reservoir-dot"></span>
                            Reservoirs
                        </div>

                        <div className="legend-item">
                            <span className="legend-dot dam-dot"></span>
                            Check Dams
                        </div>

                    </div>

                    <div className="resource-side-card location-details-card">

                        <h3>Village Information</h3>

                        <div className="location-detail">
                            <span>Village</span>
                            <strong>Hiware Bazar</strong>
                        </div>

                        <div className="location-detail">
                            <span>District</span>
                            <strong>Ahilyanagar</strong>
                        </div>

                        <div className="location-detail">
                            <span>State</span>
                            <strong>Maharashtra</strong>
                        </div>

                        <div className="location-detail">
                            <span>Mapped Resources</span>
                            <strong>{resources.length}</strong>
                        </div>

                        <div className="location-detail">
                            <span>Map Status</span>
                            <strong className="prototype-status">
                                {loading ? "Loading" : error ? "Unavailable" : "Connected"}
                            </strong>
                        </div>

                    </div>

                    <div className="resource-side-card source-card">

                        <h3>Data Sources</h3>

                        <p>OpenStreetMap</p>

                        <p>Overpass API</p>

                        <span>
                            Mapped locations only. Actual water availability
                            and storage levels are not provided by this data.
                        </span>

                    </div>

                </div>

            </div>

        </div>
    );
}

export default WaterResourcesMap;
