import React from 'react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import HospitalMap from '../features/HospitalMap';
import '../index.css';

const Home = () => {
  return (
    <div className="home-container">
      <Navbar />
      <Sidebar />
      <div className="main-content">
        <div className="header">
          <h1 className="app-title">Got Blood?</h1>
          <p className="subtitle">Streamlining blood donations across the country!</p>
        </div>
        <HospitalMap />
      </div>
    </div>
  );
};

export default Home;

