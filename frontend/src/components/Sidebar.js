import React from 'react';
import { Menu } from 'antd'; // Import Menu from Ant Design

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

export default Sidebar;
