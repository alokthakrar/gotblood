import React, { useState } from "react";
import axios from "axios";

const SignIn = () => {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    state: "",
    hospitalName: "",
    bloodAmount: 0,
  });
  const [message, setMessage] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(false); // New state for tracking login status

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const { email, password, state, hospitalName } = formData;

    if (!email || !password || !state || !hospitalName) {
      setMessage("Please enter all required fields.");
      return;
    }

    try {
      // Send the login request to the server
      const response = await axios.post(
        "http://localhost:5001/api/login",
        formData
      );
      setMessage(response.data.message);

      if (response.data.success) {
        // Store the token in localStorage and update login state
        localStorage.setItem("token", response.data.token); // Assume the server returns a token
        setIsLoggedIn(true);
        setTimeout(() => {
          window.location.href = "/dashboard"; // Redirect to the dashboard or home page
        }, 2000);
      }
    } catch (error) {
      setMessage(
        error.response?.data?.error || "Login failed. Please try again."
      );
    }
  };

  const handleBloodChange = async (action) => {
    // Check if the user is logged in before allowing blood change
    if (!isLoggedIn) {
      setMessage("You need to log in to modify blood inventory.");
      return;
    }

    // Proceed with the blood change if logged in
    try {
      const response = await axios.post("http://localhost:5001/api/updateBlood", {
        hospitalName: formData.hospitalName,
        state: formData.state,
        bloodAmount: formData.bloodAmount,
        action,  // either 'add' or 'subtract'
      });
      setMessage(response.data.message);
    } catch (error) {
      setMessage(error.response?.data?.error || "Error updating blood.");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setIsLoggedIn(false);
    setMessage("You have been logged out.");
  };

  return (
    <div className="form-container">
      {!isLoggedIn ? (
        <>
          <h2>Sign In</h2>
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
              type="password"
              name="password"
              placeholder="Password"
              value={formData.password}
              onChange={handleChange}
              required
            />
            <input
              type="text"
              name="state"
              placeholder="State"
              value={formData.state}
              onChange={handleChange}
              required
            />
            <input
              type="text"
              name="hospitalName"
              placeholder="Hospital Name"
              value={formData.hospitalName}
              onChange={handleChange}
              required
            />
            <button type="submit">Sign In</button>
          </form>
        </>
      ) : (
        <div>
          <h3>Welcome to the Dashboard!</h3>
          <button onClick={handleLogout}>Log Out</button>

          {/* Blood Management Section */}
          <div className="blood-management">
            <h3>Blood Management</h3>
            <input
              type="number"
              name="bloodAmount"
              placeholder="Blood Amount"
              value={formData.bloodAmount}
              onChange={handleChange}
            />
            <button onClick={() => handleBloodChange('add')}>Add Blood</button>
            <button onClick={() => handleBloodChange('subtract')}>Subtract Blood</button>
          </div>
        </div>
      )}

      {message && <p>{message}</p>}
    </div>
  );
};

export default SignIn;
