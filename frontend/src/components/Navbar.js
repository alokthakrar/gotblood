import React from 'react';
import { Link } from 'react-router-dom';
//import '../styles/App.css';
import '../index.css';
//import {Navbar} from 'react-bootstrap';

const Navbar = () => {
  return (
    <nav>
      <Link to="/">Home</Link>
      <Link to="/hospitals">Hospitals</Link>
      <Link to="/about">About</Link>
    </nav>
  );
};

export default Navbar;
