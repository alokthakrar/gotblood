import React from 'react';
import { Link } from 'react-router-dom';
import logo from "../assets/cow.jpg"
import '../index.css';

const Navbar = () => {
  return (
    <nav className="navbar">
      <div className="nav-left">
      <img src={logo} alt="Logo" className="logo" />
        <Link to="/">got blood ?</Link>
      </div>
    </nav>
  );
};

export default Navbar;

