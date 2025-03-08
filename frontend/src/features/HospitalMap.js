import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import '../styles/Map.css';

// Dummy hospital data (replace with real data later)
const hospitals = [
  { id: 1, name: "General Hospital", coords: [37.7749, -122.4194], bloodShortage: true },
  { id: 2, name: "City Medical Center", coords: [40.7128, -74.0060], bloodShortage: false },
  { id: 3, name: "Metro Health", coords: [34.0522, -118.2437], bloodShortage: true },
];

// Custom icons for blood availability
const bloodShortageIcon = new L.Icon({
  iconUrl: '/red-marker.png', // Add a red marker image in public folder
  iconSize: [30, 40],
});

const bloodAvailableIcon = new L.Icon({
  iconUrl: '/green-marker.png', // Add a green marker image in public folder
  iconSize: [30, 40],
});

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
            icon={hospital.bloodShortage ? bloodShortageIcon : bloodAvailableIcon}
          >
            <Popup>
              <strong>{hospital.name}</strong> <br />
              {hospital.bloodShortage ? "🚨 Blood Shortage!" : "✅ Blood Available"}
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
