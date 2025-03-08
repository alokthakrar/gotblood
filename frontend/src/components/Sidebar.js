/*import React from 'react';
import { Menu } from 'antd'; // Import Menu from Ant Design
import '../index.css';

const Sidebar = () => {
  return (
    <div className="sidebar-content">
      <Menu
        mode="inline"
        defaultSelectedKeys={['1']}
        style={{ height: '100%', borderRight: 0 }}
      >
        <Menu.Item key="1">Blood Type A</Menu.Item>
        <Menu.Item key="2">Blood Type B</Menu.Item>
        <Menu.Item key="3">Blood Type AB</Menu.Item>
        <Menu.Item key="4">Blood Type O</Menu.Item>
      </Menu>
    </div>
  );
};

export default Sidebar;*/

import React from 'react';
import '../index.css';  // Make sure to include your CSS file

const Sidebar = () => {
  return (
    <div className="sidebar">
      <h3>Blood Types</h3>
      <ul>
        <li><a href="#blood-type-a">Blood Type A</a></li>
        <li><a href="#blood-type-b">Blood Type B</a></li>
        <li><a href="#blood-type-ab">Blood Type AB</a></li>
        <li><a href="#blood-type-o">Blood Type O</a></li>
      </ul>
    </div>
  );
};

export default Sidebar;


