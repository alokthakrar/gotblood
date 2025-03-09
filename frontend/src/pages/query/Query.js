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
        if (Array.isArray(item) && item.length > 0 && typeof item[0] === 'string') { // Check if item is array, has at least one element, and the first element is a string
            return item[0].toLowerCase().includes(searchQuery.toLowerCase()); // Filter based on the FIRST element (hospital name)
        } else {
            console.warn("Skipping item in filter: Item is not a valid array or hospital name missing:", item);
            return false; // Skip invalid array items during filtering
        }
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
                                <td>{item[0]}</td> 
                                <td>{item[1]}</td>      
                                <td>{item[2]}</td>
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