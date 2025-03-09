import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import '../styles/Map.css';
import hospitalIconSrc from '../assets/hospital.png'; // Import your PNG hospital icon

// Dummy hospital data (replace with real data later)
const hospitals = [
  { id: 1, name: "General Hospital", coords: [37.7749, -122.4194], bloodType: 'A', shortageSeverity: 0.8 },
  { id: 2, name: "City Medical Center", coords: [40.7128, -74.0060], bloodType: 'B', shortageSeverity: 0.2 },
  { id: 3, name: "Metro Health", coords: [34.0522, -118.2437], bloodType: 'O', shortageSeverity: 1.0 },
];

// Blood shortage severity colors (more intensity = higher severity)
const getSeverityColor = (shortageSeverity) => {
  if (shortageSeverity > 0.8) return '#ff0000'; // Red (Critical)
  if (shortageSeverity > 0.5) return '#ff6600'; // Orange (Moderate)
  if (shortageSeverity > 0.2) return '#ffcc00'; // Yellow (Low)
  return '#66cc66'; // Green (No shortage)
};

// Create custom hospital icon with shortage severity overlay
const createHospitalIcon = (shortageSeverity) => {
  const iconSize = 40; // Adjust the size for better visibility

  return L.divIcon({
    className: 'custom-hospital-icon',
    html: `
      <div style="position: relative; width: ${iconSize}px; height: ${iconSize}px;">
        <img src="${hospitalIconSrc}" style="width: 100%; height: 100%; display: block;" />
        <div style="
          position: absolute;
          top: -5px;
          right: -5px;
          width: 15px;
          height: 15px;
          background-color: ${getSeverityColor(shortageSeverity)};
          border-radius: 50%;
          border: 2px solid white;
          box-shadow: 0 0 5px rgba(0,0,0,0.3);
        "></div>
      </div>
    `,
    iconSize: [iconSize, iconSize], // Size of the icon
    iconAnchor: [iconSize / 2, iconSize], // Anchor at bottom center
    popupAnchor: [0, -iconSize / 2], // Adjust popup position
  });
};

// Component to fit map view to markers
const FitMapBounds = ({ locations }) => {
  const map = useMap();

  React.useEffect(() => {
    if (locations.length > 0) {
      const bounds = L.latLngBounds(locations);
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [locations, map]);

  return null;
};

const HospitalMap = () => {
  return (
    <div className="map-wrapper">
      <MapContainer
        center={[37.0902, -95.7129]}
        zoom={4}
        className="map"
        maxBounds={[
          [24.396308, -125.0], // Southwest corner (bottom-left)
          [49.384358, -66.93457], // Northeast corner (top-right)
        ]}
        scrollWheelZoom={true} // Allow zooming with scroll
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="&copy; OpenStreetMap contributors"
        />

        {/* Add hospital markers */}
        {hospitals.map((hospital) => (
          <Marker
            key={hospital.id}
            position={hospital.coords}
            icon={createHospitalIcon(hospital.shortageSeverity)}
          >
            <Popup>
              <div style={{ textAlign: 'center' }}>
                <strong>{hospital.name}</strong> <br />
                <p><strong>Blood Type Needed:</strong> {hospital.bloodType}</p>
                <p><strong>Severity:</strong> {Math.round(hospital.shortageSeverity * 100)}%</p>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* Fit map to markers */}
        <FitMapBounds locations={hospitals.map(h => h.coords)} />
      </MapContainer>
    </div>
  );
};

export default HospitalMap;
