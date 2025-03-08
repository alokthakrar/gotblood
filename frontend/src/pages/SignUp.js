import React, { useState } from 'react';
import axios from 'axios';
import { Form, Button, Container, Alert, Spinner } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';

const SignUp = () => {
  const [email, setEmail] = useState('');
  const [bloodType, setBloodType] = useState('');
  const [location, setLocation] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post('https://your-backend-api.com/signup', {
        email,
        bloodType,
        location,
      });
      console.log('User signed up successfully', response.data);
      alert('You are successfully signed up for blood donation notifications!');
    } catch (err) {
      console.error('Error signing up user:', err);
      setError('There was an issue with your signup. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container className="mt-5 p-4" style={{ maxWidth: '500px', backgroundColor: '#fff', borderRadius: '10px', boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)', border: '2px solid #d9534f' }}>
      <h2 className="mb-4 text-center" style={{ color: '#d9534f' }}>Sign Up for Blood Donation Notifications</h2>
      {error && <Alert variant="danger">{error}</Alert>}
      <Form onSubmit={handleSubmit}>
        <Form.Group className="mb-3" controlId="email">
          <Form.Label style={{ color: '#d9534f' }}>Email:</Form.Label>
          <Form.Control
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </Form.Group>

        <Form.Group className="mb-3" controlId="bloodType">
          <Form.Label style={{ color: '#d9534f' }}>Blood Type:</Form.Label>
          <Form.Select
            value={bloodType}
            onChange={(e) => setBloodType(e.target.value)}
            required
          >
            <option value="">Select your blood type</option>
            <option value="A+">A+</option>
            <option value="A-">A-</option>
            <option value="B+">B+</option>
            <option value="B-">B-</option>
            <option value="O+">O+</option>
            <option value="O-">O-</option>
            <option value="AB+">AB+</option>
            <option value="AB-">AB-</option>
          </Form.Select>
        </Form.Group>

        <Form.Group className="mb-3" controlId="location">
          <Form.Label style={{ color: '#d9534f' }}>Location:</Form.Label>
          <Form.Control
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            required
          />
        </Form.Group>

        <Button 
          variant="danger" 
          type="submit" 
          disabled={loading} 
          style={{ width: '100%', backgroundColor: '#d9534f', borderColor: '#d9534f', fontSize: '18px' }}
        >
          {loading ? <Spinner as="span" animation="border" size="sm" /> : 'Sign Up'}
        </Button>
      </Form>
    </Container>
  );
};

export default SignUp;
