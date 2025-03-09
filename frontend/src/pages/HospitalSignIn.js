import React, { useState } from "react";
import axios from "axios";

const SignIn = () => {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [message, setMessage] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const { email, password } = formData;

    if (!email || !password) {
      setMessage("Please enter both email and password.");
      return;
    }

    try {
      // Send the login request to the server
      const response = await axios.post(
        "http://localhost:5001/api/login",
        formData
      );
      setMessage(response.data.message);

      // Redirect to the dashboard or another page after successful login
      if (response.data.success) {
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

  return (
    <div className="form-container">
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
        <button type="submit">Sign In</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
};

export default SignIn;
