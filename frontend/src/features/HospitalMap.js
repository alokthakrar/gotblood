import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import '../styles/Map.css';

// Dummy hospital data (replace with real data later)
const hospitals = [
  { id: 1, name: "General Hospital", coords: [37.7749, -122.4194], bloodType: 'A', shortageSeverity: 0.8 },
  { id: 2, name: "City Medical Center", coords: [40.7128, -74.0060], bloodType: 'B', shortageSeverity: 0.2 },
  { id: 3, name: "Metro Health", coords: [34.0522, -118.2437], bloodType: 'O', shortageSeverity: 1.0 },
];

// Utility function to convert hex color to RGB
const hexToRgb = (hex) => {
  // Remove '#' if present
  hex = hex.replace('#', '');

  // Convert 3-digit hex to 6-digit
  if (hex.length === 3) {
    hex = hex.split('').map(c => c + c).join('');
  }

  const r = parseInt(hex.substr(0, 2), 16);
  const g = parseInt(hex.substr(2, 2), 16);
  const b = parseInt(hex.substr(4, 2), 16);

  return [r, g, b];
};

// Function to determine marker color based on blood type and shortage severity
const getMarkerColor = (bloodType, shortageSeverity) => {
  let color = '';

  // Blood type colors
  switch (bloodType) {
    case 'A':
      color = '#ff7f00'; // Orange for A blood type
      break;
    case 'B':
      color = '#ff0000'; // Red for B blood type
      break;
    case 'O':
      color = '#ffcc00'; // Yellow for O blood type
      break;
    case 'AB':
      color = '#00ff00'; // Green for AB blood type
      break;
    default:
      color = '#cccccc'; // Default color if blood type is unknown
      break;
  }

  const intensity = Math.max(0.2, shortageSeverity); // Set a minimum intensity for visibility
  const [r, g, b] = hexToRgb(color); // Convert hex to RGB
  const adjustedColor = [Math.floor(r * intensity), Math.floor(g * intensity), Math.floor(b * intensity)];
  return `rgb(${adjustedColor.join(', ')})`; // Return a color string in rgb format
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
        {hospitals.map((hospital) => {
          const { bloodType, shortageSeverity } = hospital;
          const markerColor = getMarkerColor(bloodType, shortageSeverity);

          return (
            <Marker
              key={hospital.id}
              position={hospital.coords}
              icon={new L.DivIcon({
                className: 'custom-marker',
                html: `<div style="background-color:${markerColor}; width: 30px; height: 40px; border-radius: 50%;"></div>`,
              })}
            >
              <Popup>
                <strong>{hospital.name}</strong> <br />
                <p><strong>Blood Type Needed: {bloodType}</strong></p>
                <p><strong>Severity:</strong> {Math.round(shortageSeverity * 100)}%</p>
              </Popup>
            </Marker>
          );
        })}

        {/* Fit map to markers */}
        <FitMapBounds locations={hospitals.map(h => h.coords)} />
      </MapContainer>
    </div>
  );
};

export default HospitalMap;

