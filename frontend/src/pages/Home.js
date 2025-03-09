import React from 'react';
import Navbar from '../components/Bav';
import Sidebar from '../components/Sidebar';
import Footer from '../components/Footer';
import HospitalMap from '../features/HospitalMap';
import '../index.css';

const Home = () => {
  return (
    <div className="home-container">

      <Sidebar />
      <div className="main-content">
        <div className="header">
          <h4 className="app-title">Got Blood? We Do. Let’s Make Sure Everyone Does.</h4>
          <p className="subtitle"><i>Track donations and shortages nationwide with our interactive map.</i></p>
        </div>
        <HospitalMap />
        
      </div>
      <Footer/>
    </div>
  );
};

export default Home;

