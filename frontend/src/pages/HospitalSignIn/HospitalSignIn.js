import React, { useState } from "react";

const AddDonor = () => {
  const [formData, setFormData] = useState({
    donor_id: "",
    first_name: "",
    last_name: "",
    age: "",
    blood_type: "",
    city: "",
    state: "",
    lat: "",
    lon: "",
    email: "",
    phone: "",
  });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setMessage("");

    // Basic validation - you can add more robust validation
    if (!formData.donor_id || !formData.first_name || !formData.last_name || !formData.age || !formData.blood_type || !formData.city || !formData.state || !formData.lat || !formData.lon || !formData.email || !formData.phone) {
      setError("Please fill in all fields.");
      return;
    }

    try {
      const response = await fetch("http://localhost:5001/donor/add", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          donor_id: formData.donor_id,
          first_name: formData.first_name,
          last_name: formData.last_name,
          age: parseInt(formData.age), // Ensure age is an integer
          blood_type: formData.blood_type,
          location: {
            city: formData.city,
            state: formData.state,
            coordinates: { lat: parseFloat(formData.lat), lon: parseFloat(formData.lon) }, // Ensure lat and lon are floats
          },
          contact_info: { email: formData.email, phone: formData.phone },
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(data.message || "Donor added successfully!");
        // Optionally reset form after successful submission
        setFormData({
            donor_id: "",
            first_name: "",
            last_name: "",
            age: "",
            blood_type: "",
            city: "",
            state: "",
            lat: "",
            lon: "",
            email: "",
            phone: "",
        });
      } else {
        setError(data.error || "Failed to add donor. Please try again.");
      }
    } catch (apiError) {
      console.error("API Error:", apiError);
      setError("Failed to add donor. Please check your connection and try again.");
    }
  };

  return (
    <div className="form-container">
      <h2>Add Donor</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          name="donor_id"
          placeholder="Donor ID (e.g., D0000001)"
          value={formData.donor_id}
          onChange={handleChange}
          required
        />
        <input
          type="text"
          name="first_name"
          placeholder="First Name"
          value={formData.first_name}
          onChange={handleChange}
          required
        />
        <input
          type="text"
          name="last_name"
          placeholder="Last Name"
          value={formData.last_name}
          onChange={handleChange}
          required
        />
        <input
          type="number"
          name="age"
          placeholder="Age"
          value={formData.age}
          onChange={handleChange}
          required
        />
        <input
          type="text"
          name="blood_type"
          placeholder="Blood Type (e.g., O+)"
          value={formData.blood_type}
          onChange={handleChange}
          required
        />
        <input
          type="text"
          name="city"
          placeholder="City"
          value={formData.city}
          onChange={handleChange}
          required
        />
        <input
          type="text"
          name="state"
          placeholder="State (e.g., NY)"
          value={formData.state}
          onChange={handleChange}
          required
        />
        <input
          type="number"
          name="lat"
          placeholder="Latitude"
          value={formData.lat}
          onChange={handleChange}
          required
        />
        <input
          type="number"
          name="lon"
          placeholder="Longitude"
          value={formData.lon}
          onChange={handleChange}
          required
        />
        <input
          type="email"
          name="email"
          placeholder="Email"
          value={formData.email}
          onChange={handleChange}
          required
        />
        <input
          type="tel"
          name="phone"
          placeholder="Phone (e.g., 123-456-7890)"
          value={formData.phone}
          onChange={handleChange}
          required
        />

        <button type="submit">Add Donor</button>
      </form>
      {message && <p style={{ color: 'green' }}>{message}</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};

export default AddDonor;