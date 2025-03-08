import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Hospitals from './pages/Hospitals';
import SignUp from './pages/SignUp'
//import About from './pages/About';

const App = () => {
  return (
    <Router>
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/hospitals" element={<Hospitals />} />
      <Route path="/signup" element={<SignUp/>}/>
    </Routes>
  </Router>

 
  );
};

export default App;

//<Route path="/about" component={About} />