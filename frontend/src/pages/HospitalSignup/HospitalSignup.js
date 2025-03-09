import React, { useState } from "react";
import axios from "axios";

//Opencage api
const GEOCODING_API_KEY = "041a9e867a23424d9eb6586661af3d59"; // Replace with your API key
const GEOCODING_API_URL = "https://api.opencagedata.com/geocode/v1/json";

const Hsignup = () => {
  const [formData, setFormData] = useState({
    email: "",
    zipCode: "", 
    password: "",
  });
  const [message, setMessage] = useState("");
  const [redirect, setRedirect] = useState(false); // State to control the redirect

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Geocode the zip code to get latitude and longitude
    const { zipCode } = formData;
    if (!zipCode) {
      setMessage("Zip code is required.");
      return;
    }

    try {
      const geocodeResponse = await axios.get(GEOCODING_API_URL, {
        params: {
          q: zipCode,
          key: GEOCODING_API_KEY,
        },
      });

      if (geocodeResponse.data.results.length === 0) {
        setMessage("Invalid zip code.");
        return;
      }

      const { lat, lng } = geocodeResponse.data.results[0].geometry; // Extract latitude and longitude

      // Add latitude and longitude to the form data
      const updatedFormData = {
        ...formData,
        latitude: lat,
        longitude: lng,
      };

      // Send the updated form data to the server
      const response = await axios.post("http://localhost:5001/api/signup", updatedFormData);
      setMessage(response.data.message);
      setTimeout(() => setRedirect(true), 2000); // Set redirect flag after 2 seconds
    } catch (error) {
      setMessage(error.response?.data?.error || "Signup failed. Try again.");
    }
  };

  // Redirect to login page manually after signup success
  if (redirect) {
    window.location.href = "/login"; // Redirect to the login page
  }

  return (
    <div className="form-container">
      <h2>Signup</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          name="email"
          placeholder="Email"
          value={formData.email}
          onChange={handleChange}
          required
        />
        <input
          type="text"
          name="zipCode"
          placeholder="Zip Code" // Zip Code for location
          value={formData.zipCode}
          onChange={handleChange}
          required
        />
        <input
          type="password"
          name="password"
          placeholder="Password"
          value={formData.password}
          onChange={handleChange}
          required
        />
        <button type="submit">Signup</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
};

export default Hsignup;

