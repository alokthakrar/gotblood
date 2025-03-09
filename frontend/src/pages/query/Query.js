import React, { useState, useEffect } from 'react';
import { Container, Form, FormControl, Table } from 'react-bootstrap';

function FilterableHospitalTable() {
    const [searchQuery, setSearchQuery] = useState('');
    const [data, setData] = useState([]); // State to hold the data
    const [loading, setLoading] = useState(false); // Add loading state
    const [error, setError] = useState(null);     // Add error state

    // Sample data - replace with actual data fetching if needed
    useEffect(() => {
        const fetchData = async () => {
            setLoading(true); // Set loading to true at start
            setError(null);     // Clear any previous errors

            try {
                const response = await fetch('http://localhost:5001/hospital/data'); // **USE YOUR ACTUAL API ENDPOINT URL**
                console.log("API Response Received:", response); // **Log the entire response object**

                if (!response.ok) {
                    const errorMessage = `HTTP error! status: ${response.status}`;
                    console.error("API Error - HTTP Status NOT OK:", errorMessage); // Log HTTP error
                    throw new Error(errorMessage);
                }

                const jsonData = await response.json();
                console.log("Parsed JSON Data from API:", jsonData); // **Log the parsed JSON data**

                if (Array.isArray(jsonData)) {
                    setData(jsonData);
                    console.log("setData called with API data (array). Data state updated."); // **Log when setData is called correctly**
                } else {
                    console.warn("API Response is NOT an array! Response Data:", jsonData);
                    setData([]); // Still set data to an empty array (to avoid .filter error) but log warning
                    setError("API response was not in the expected array format."); // Set error message for user
                }


            } catch (error) {
                console.error("Error during API Fetch:", error); // Log full error details
                setError(error.message || "Failed to load hospital data."); // Set error state for user
                setData([]); // Ensure data is still an array (empty) on error to avoid filter issues
            } finally {
                setLoading(false); // Set loading to false at the end
            }
        };

        fetchData();

    }, []); // Empty dependency array
    const filteredData = data.filter(item =>
        item[0].toLowerCase().includes(searchQuery.toLowerCase()));

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

            <Table striped bordered hover>
                <thead>
                    <tr>
                        <th>Hospital</th>
                        <th>City</th>
                        <th>Blood Type</th>
                        <th>Delta Count</th>
                        {/* You can choose to hide/show 'password' column as needed */}
                        {/* <th>Password</th> */}
                    </tr>
                </thead>
                <tbody>
                    {filteredData.map((item, index) => (
                        <tr key={index}>
                            <td>{item.hospital}</td>
                            <td>{item.city}</td>
                            <td>{item.bloodType}</td>
                            <td>{item.delta_count}</td>
                            {/* Conditionally render 'password' if needed for display or debugging */}
                            {/* <td>{item.password}</td> */}
                        </tr>
                    ))}
                    {filteredData.length === 0 && (
                        <tr>
                            <td colSpan="4" className="text-center">No hospitals found matching "{searchQuery}"</td>
                        </tr>
                    )}
                </tbody>
            </Table>
        </Container>
    );
}

export default FilterableHospitalTable;