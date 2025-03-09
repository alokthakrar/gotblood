import React from 'react';
import '../index.css';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-container">
        <p>&copy; {new Date().getFullYear()} got blood?</p>
        <a
          href="https://docs.google.com/presentation/d/1-NoRxK_QzmNcdKb5xkyn4vsOyh1L71y9LMDrlCir08E/edit#slide=id.g6d136aaa59_1_51"
          target="_blank"
          rel="noopener noreferrer"
        >
          About Us
        </a>
      </div>
    </footer>
  );
};

export default Footer;

