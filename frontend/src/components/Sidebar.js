
import React from 'react';
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

export default Sidebar;


