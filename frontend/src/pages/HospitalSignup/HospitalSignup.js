import React, { useState } from "react";
import { Container, Row, Col, Form, FormGroup, FormLabel, FormControl, Button, Alert } from 'react-bootstrap';
import './HospitalSignup.css'; // Import a CSS file for custom styles

const GEOCODING_API_KEY = "041a9e867a23424d9eb6586661af3d59"; // Replace with your API key
const GEOCODING_API_URL = "https://api.opencagedata.com/geocode/v1/json";

const Hsignup = () => {
    const [formData, setFormData] = useState({
        email: "",
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

        const { zipCode } = formData;
        if (!zipCode) {
            setError("Zip code is required.");
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
                ...formData,
                latitude: lat,
                longitude: lng,
            };

            const signupResponse = await fetch("http://localhost:5001/api/signup", {
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
        window.location.href = "/login";
    }

    return (
        <Container fluid className="hsignup-page">
            <Row className="justify-content-center align-items-center h-100">
                <Col md={6} lg={5}> {/* Reduced column size here: md={3} lg={2} */}
                    <Container className="hsignup-form-container p-4 rounded shadow-lg">
                        <h2 className="text-center mb-4 text-danger">Hospital Sign Up</h2>
                        {error && <Alert variant="danger" className="mb-3">{error}</Alert>}
                        {message && <Alert variant="success" className="mb-3">{message}</Alert>}
                        <Form onSubmit={handleSubmit}>
                            <FormGroup className="mb-3" controlId="formEmail">
                                <FormLabel className="text-danger">Email address</FormLabel>
                                <FormControl
                                    type="email"
                                    name="email"
                                    placeholder="Enter email"
                                    value={formData.email}
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