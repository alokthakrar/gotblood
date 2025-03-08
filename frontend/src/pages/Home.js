import React from 'react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import HospitalMap from '../features/HospitalMap';
const Home = () => {
  return (
    <div className="home-container">
      <Navbar />
      <div className="content-wrapper">
        <Sidebar />
        <div className="main-content">
          <h1>got blood?</h1>
          <p>Streamlining blood donations across the country!</p>
          <HospitalMap />
        </div>
      </div>
    </div>
  );
};

export default Home;
