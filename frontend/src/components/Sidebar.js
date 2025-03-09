
/*import React from 'react';
import '../index.css';  // Make sure to include your CSS file

const Sidebar = () => {
  //const [sidebarWidth, setSidebarWidth] = useState(250);
  return (
    <div className="sidebar">
      <h3>Map Guide</h3>
      <ul>
        <li><strong>Orange Markers</strong>: Indicate hopsitals with a high need for blood.</li>
        <li><strong>Green Markers</strong>: Indicate blood donation centers.</li>
        <li><strong>Hovering over Marker</strong>: Displays more detailed information about the hospital or blood donation center.</li>
        <li><strong>Zooming in/out</strong>: Allows you to explore locations at different levels of detail.</li>
      </ul>
    </div>
  );
};

export default Sidebar;*/

import React from 'react';
import '../index.css';
import hospitalIconSrc from '../assets/hospital.png';

const Sidebar = () => {
  return (
    <div className="sidebar">
      <h3>🗺 Map Guide</h3>

      {/* Marker Legend */}
      <div className="legend">
        <h4>📍 Marker Legend</h4>
        <ul>
          <li>
            <div className="legend-item">
              <img src={hospitalIconSrc} alt="Hospital" className="hospital-icon" />
              <span className="severity-dot high"></span>
              <span>High Blood Shortage</span>
            </div>
          </li>
          <li>
            <div className="legend-item">
              <img src={hospitalIconSrc} alt="Hospital" className="hospital-icon" />
              <span className="severity-dot medium"></span>
              <span>Moderate Blood Shortage</span>
            </div>
          </li>
          <li>
            <div className="legend-item">
              <img src={hospitalIconSrc} alt="Hospital" className="hospital-icon" />
              <span className="severity-dot low"></span>
              <span>Low Blood Shortage</span>
            </div>
          </li>
          <li>
            <div className="legend-item">
              <img src={hospitalIconSrc} alt="Hospital" className="hospital-icon" />
              <span className="severity-dot none"></span>
              <span>Stable Blood Supply</span>
            </div>
          </li>
        </ul>
      </div>

      {/* Map Interaction Guide */}
      <div className="map-tips">
        <h4>🛠 Map Controls</h4>
        <ul>
          <li><strong>🔍 Zoom In/Out:</strong> Explore different locations.</li>
          <li><strong>🩸 Click a Marker:</strong> Get detailed blood supply info.</li>
        </ul>
      </div>
    </div>
  );
};

export default Sidebar;
