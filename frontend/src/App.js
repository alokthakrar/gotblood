import React from 'react';
import "bootstrap/dist/css/bootstrap.min.css";
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
//import 'antd/dist/antd.css';
//import Hospitals from './pages/Hospitals';
import SignUp from './pages/SignUp'
import FilterableHospitalTable from './pages/query/Query';
import NavTop from './components/Bav';
//import About from './pages/About';

const App = () => {
  return (
    <>
    <NavTop/>
    <Router>
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/signup" element={<SignUp/>}/>
      <Route path="/filter" element={<FilterableHospitalTable/>}/>
    </Routes>
  </Router>
  </>

 
  );
};

export default App;

//<Route path="/about" component={About} />