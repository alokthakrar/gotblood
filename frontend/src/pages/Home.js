import React from 'react';
import Navbar from '../components/Navbar';
import HospitalMap from '../features/HospitalMap';
const Home = () => {
  return (
    <div>
      <Navbar />
      <h1>Welcome to the Blood Donation App</h1>
      <p>Streamlining blood donations across the country!</p>
      <HospitalMap />
    </div>
  );
};

export default Home;
