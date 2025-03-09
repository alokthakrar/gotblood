import React, { useState } from "react";
import { Container, Row, Col, Form, FormGroup, FormLabel, FormControl, Button, Alert } from 'react-bootstrap';
import './HospitalSignup.css'; // Import a CSS file for custom styles

const GEOCODING_API_KEY = "041a9e867a23424d9eb6586661af3d59"; // Replace with your API key
const GEOCODING_API_URL = "https://api.opencagedata.com/geocode/v1/json";

const Hsignup = () => {
    const [formData, setFormData] = useState({
        hospitalName: "", // Added hospital name field
        zipCode: "",
        password: "",
    });
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");
    const [redirect, setRedirect] = useState(false);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setMessage("");

        const { zipCode, password, hospitalName } = formData; // Include hospitalName

        if (!zipCode) {
            setError("Zip code is required.");
            return;
        }
        if (!hospitalName) {
            setError("Hospital name is required.");
            return;
        }
        if (!password) {
            setError("Password is required.");
            return;
        }


        try {
            const geocodeResponse = await fetch(`${GEOCODING_API_URL}?q=${zipCode}&key=${GEOCODING_API_KEY}`);
            if (!geocodeResponse.ok) {
                throw new Error(`Geocoding API error! status: ${geocodeResponse.status}`);
            }
            const geocodeData = await geocodeResponse.json();

            if (geocodeData.results.length === 0) {
                setError("Invalid zip code.");
                return;
            }

            const { lat, lng } = geocodeData.results[0].geometry;
            const updatedFormData = {
                name: hospitalName, // Use hospitalName for 'name' field
                city: zipCode,      // Use zipCode for 'city' field as requested
                coordinates: { lat: lat, lon: lng },
                password: password,
                // flagSettings: {} // Optional flagSettings can be added here if needed, e.g., from form inputs
            };

            const signupResponse = await fetch("http://localhost:5001/hospital/create", { // Updated endpoint
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(updatedFormData),
            });

            const signupData = await signupResponse.json();

            if (signupResponse.ok) {
                setMessage(signupData.message);
                setTimeout(() => setRedirect(true), 2000);
            } else {
                setError(signupData.error || "Signup failed. Try again.");
            }

        } catch (apiError) {
            console.error("API Error:", apiError);
            setError(apiError.message || "Signup process failed. Please check your connection and try again.");
        }
    };

    if (redirect) {
        window.location.href = "/login"; // Or wherever you want to redirect after signup
    }

    return (
        <Container fluid className="hsignup-page">
            <Row className="justify-content-center align-items-center h-100">
                <Col md={6} lg={5}>
                    <Container className="hsignup-form-container p-4 rounded shadow-lg">
                        <h2 className="text-center mb-4 text-danger">Hospital Sign Up</h2>
                        {error && <Alert variant="danger" className="mb-3">{error}</Alert>}
                        {message && <Alert variant="success" className="mb-3">{message}</Alert>}
                        <Form onSubmit={handleSubmit}>
                            {/* New Hospital Name Field */}
                            <FormGroup className="mb-3" controlId="formHospitalName">
                                <FormLabel className="text-danger">Hospital Name</FormLabel>
                                <FormControl
                                    type="text"
                                    name="hospitalName"
                                    placeholder="Enter Hospital Name"
                                    value={formData.hospitalName}
                                    onChange={handleChange}
                                    required
                                    className="form-control-red-border"
                                />
                            </FormGroup>

                            <FormGroup className="mb-3" controlId="formZipCode">
                                <FormLabel className="text-danger">Zip Code</FormLabel>
                                <FormControl
                                    type="text"
                                    name="zipCode"
                                    placeholder="Enter Zip Code"
                                    value={formData.zipCode}
                                    onChange={handleChange}
                                    required
                                    className="form-control-red-border"
                                />
                            </FormGroup>

                            <FormGroup className="mb-4" controlId="formPassword">
                                <FormLabel className="text-danger">Password</FormLabel>
                                <FormControl
                                    type="password"
                                    name="password"
                                    placeholder="Password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    required
                                    className="form-control-red-border"
                                />
                            </FormGroup>

                            <div className="d-grid">
                                <Button variant="danger" type="submit" size="lg">
                                    Sign Up
                                </Button>
                            </div>
                        </Form>
                    </Container>
                </Col>
            </Row>
        </Container>
    );
};

export default Hsignup;