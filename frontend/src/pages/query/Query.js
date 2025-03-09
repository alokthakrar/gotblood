import React, { useState, useEffect } from 'react';
import { Container, Form, FormControl, Table, Alert, Spinner } from 'react-bootstrap';

function FilterableHospitalTable() {
    const [searchQuery, setSearchQuery] = useState('');
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setError(null);
            try {
                const response = await fetch('http://localhost:5001/hospital/data'); // USE YOUR ACTUAL API ENDPOINT URL
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
            }
                const jsonData = await response.json();
                setData(jsonData)
                console.log(typeof jsonData)
                console.log(data)
            } catch (error) {
                console.error("Error fetching hospital data:", error);
                setError(error.message || "Failed to load hospital data.");
                setData([]);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);
    const filteredData = data.filter(item => {
            return item.hospital.toLowerCase().includes(searchQuery.toLowerCase()); // Filter based on the FIRST element (hospital name)
    }); 
    return (
        <Container className="mt-4">
            <h2>Hospital Data</h2>

            <Form inline className="mb-3">
                <FormControl
                    type="text"
                    placeholder="Search by Hospital Name..."
                    className="mr-sm-2"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                />
            </Form>

            {error && <Alert variant="danger">Error: {error}</Alert>}

            {loading && <div className="text-center"><Spinner animation="border" role="status"> <span className="visually-hidden">Loading...</span></Spinner> <p>Loading Hospital Data...</p></div>}

            {!loading && !error && (
                <Table striped bordered hover>
                    <thead>
                    <tr>
                        <th>Hospital Name</th> 
                        <th>City</th>
                        <th>Blood Type</th>
                        <th>Delta Count</th>
                    </tr>
                    </thead>
                    <tbody>
                        {filteredData.map((item, index) => (
                            <tr key={index}>
                                <td>{item.hospital}</td> 
                                <td>{item.city}</td>      
                                <td>{item.hospital}</td>
                                <td>{item.delta_count}</td>
                            </tr>
                        ))}
                        {filteredData.length === 0 && (
                            <tr>
                                <td colSpan="4" className="text-center">No hospitals found matching "{searchQuery}"</td>
                            </tr>
                        )}
                    </tbody>
                </Table>
            )}
        </Container>
    );
}

export default FilterableHospitalTable;