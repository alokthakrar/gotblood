import React from 'react';
import { MapContainer, TileLayer } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import '../styles/Map.css';

const HospitalMap = () => {
  return (
    <div className="map-wrapper">
      {/* MapContainer is where the map is rendered */}
      <MapContainer center={[37.7749, -122.4194]} zoom={5} className="map">
        {/* TileLayer provides the base map tiles */}
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="&copy; OpenStreetMap contributors"
        />
      </MapContainer>
    </div>
  );
};

export default HospitalMap;
