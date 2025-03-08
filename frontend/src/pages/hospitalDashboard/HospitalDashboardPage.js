import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, ListGroup, Alert, Spinner, Button } from 'react-bootstrap';

function HospitalDashboardPage() {
    // Example Hospital ID -  In a real app, this would come from routing parameters or selection.
    const initialHospitalLid = "L0001"; // Or get this dynamically

    const [hospitalData, setHospitalData] = useState(null);
    const [nearbyExcessHospitals, setNearbyExcessHospitals] = useState(null);
    const [nearbyDonorPools, setNearbyDonorPools] = useState(null);
    const [nearestNeededHospitals, setNearestNeededHospitals] = useState(null);
    const [recommendations, setRecommendations] = useState(null);
    const [loading, setLoading] = useState(true); // Initially loading
    const [error, setError] = useState(null);

    const currentHospitalLid = useState(initialHospitalLid)[0]; //  Just for readability here - in real app manage dynamically

    useEffect(() => {
        const fetchHospitalData = async () => {
            setLoading(true);
            setError(null);

            try {
                const inventoryResponse = await fetch(`/api/hospital_inventory/${currentHospitalLid}`); // Backend proxy setup likely needed in React
                if (!inventoryResponse.ok) throw new Error(`Inventory fetch failed: ${inventoryResponse.status}`);
                const inventoryData = await inventoryResponse.json();
                setHospitalData(inventoryData);

                // Example - Check if any blood type is low (customize your "low" threshold)
                let lowBloodType = null;
                const lowStockThreshold = 2; // Example low stock threshold. Adjust as needed
                for (const bt in inventoryData.inventory) {
                    if (inventoryData.inventory[bt] <= lowStockThreshold) {
                        lowBloodType = bt; // Assume only one type can be "most low" for simplicity here
                        break; // Stop at the first low type
                    }
                }


                if (lowBloodType) { // Fetch nearby excess hospitals and donor pools if low on a blood type
                    const excessHospitalsResponse = await fetch(`/api/nearby_excess_hospitals/${currentHospitalLid}?bloodType=${lowBloodType}`);
                    if (!excessHospitalsResponse.ok) throw new Error(`Nearby Excess Hospitals fetch failed: ${excessHospitalsResponse.status}`);
                    setNearbyExcessHospitals(await excessHospitalsResponse.json());

                    const donorPoolsResponse = await fetch(`/api/nearby_donor_pools/${currentHospitalLid}?bloodType=${lowBloodType}`);
                    if (!donorPoolsResponse.ok) throw new Error(`Nearby Donor Pools fetch failed: ${donorPoolsResponse.status}`);
                    setNearbyDonorPools(await donorPoolsResponse.json());
                     setNearestNeededHospitals(null); // Clear if showing shortage related components
                } else { // If not low - check for surplus.  Example surplus logic - if *any* blood type > a threshold.
                    let surplusBloodType = null;
                    const surplusThreshold = 10; // Example surplus threshold
                    for (const bt in inventoryData.inventory) {
                        if (inventoryData.inventory[bt] >= surplusThreshold) {
                            surplusBloodType = bt; // Take the first surplus type found. Adjust logic if multiple types can be in surplus and handled.
                            break;
                        }
                    }

                    if (surplusBloodType) {
                        const neededHospitalsResponse = await fetch(`/api/nearest_needed_hospitals/${currentHospitalLid}?bloodType=${surplusBloodType}`);
                        if (!neededHospitalsResponse.ok) throw new Error(`Nearest Needed Hospitals fetch failed: ${neededHospitalsResponse.status}`);
                        setNearestNeededHospitals(await neededHospitalsResponse.json());
                        setNearbyExcessHospitals(null); // Clear if showing surplus related components
                        setNearbyDonorPools(null);

                    } else { // If neither low nor surplus on any type for example - clear these components.
                        setNearbyExcessHospitals(null);
                        setNearbyDonorPools(null);
                        setNearestNeededHospitals(null);
                    }
                }

                const recommendationsResponse = await fetch(`/api/blood_recommendations/${currentHospitalLid}`);
                if (!recommendationsResponse.ok) throw new Error(`Recommendations fetch failed: ${recommendationsResponse.status}`);
                setRecommendations(await recommendationsResponse.json());


            } catch (e) {
                console.error("Error fetching hospital dashboard data:", e);
                setError(e.message || "Failed to load hospital data.");
            } finally {
                setLoading(false);
            }
        };

        fetchHospitalData();
    }, [currentHospitalLid]); // Re-fetch data if hospital ID changes (add hospital selection logic in real app)


    if (loading) return <div className="text-center"><Spinner animation="border" role="status"> <span className="visually-hidden">Loading...</span></Spinner> <p>Loading Hospital Dashboard...</p></div>;
    if (error) return <Alert variant="danger">Error: {error}</Alert>;
    if (!hospitalData) return <Alert variant="warning">No hospital data available.</Alert>;


    return (
        <Container className="mt-4">
            <h1>Hospital Blood Dashboard: {hospitalData.hospitalName}</h1>
            <p>Location: {hospitalData.hospitalLocation}</p>

            <Card className="mb-3">
                <Card.Header>Current Blood Inventory</Card.Header>
                <ListGroup variant="flush">
                    {Object.entries(hospitalData.inventory).map(([bloodType, count]) => (
                        <ListGroup.Item key={bloodType}>
                            {bloodType}: {count} bags
                        </ListGroup.Item>
                    ))}
                    {hospitalData.donorStats && hospitalData.donorStats.length > 0 && (
                        <ListGroup.Item>
                             <details>
                                <summary>Donor Statistics Summary</summary>
                                <p>Details of donor statistics available from the backend:</p>
                                <ul>
                                    {hospitalData.donorStats.map((stat, index) => (
                                        <li key={index}>
                                             {stat.city}: {stat.totalDonors} total donors
                                             {stat.bloodTypeStats && stat.bloodTypeStats.map(bts => (
                                                 <div key={bts.bloodType}> - {bts.bloodType}: {bts.donorCount} donors</div>
                                             ))}
                                        </li>
                                    ))}
                                </ul>
                            </details>
                        </ListGroup.Item>
                    )}

                </ListGroup>
            </Card>


            {nearbyExcessHospitals && nearbyExcessHospitals.length > 0 && (
                <Card className="mb-3">
                    <Card.Header>Nearby Hospitals with Excess Blood (of Needed Type)</Card.Header>
                    <ListGroup variant="flush">
                        {nearbyExcessHospitals.map((hosp, index) => (
                            <ListGroup.Item key={index}>
                                {hosp.hospitalName}, {hosp.hospitalLocation} - Excess bags: {hosp.excessBloodCount}
                            </ListGroup.Item>
                        ))}
                    </ListGroup>
                </Card>
            )}

             {nearbyDonorPools && nearbyDonorPools.length > 0 && (
                <Card className="mb-3">
                    <Card.Header>Nearby Areas with Potential Donors (of Needed Type)</Card.Header>
                    <ListGroup variant="flush">
                        {nearbyDonorPools.map((area, index) => (
                            <ListGroup.Item key={index}>
                                {area.areaName} - Potential Donors: {area.donorCount}
                            </ListGroup.Item>
                        ))}
                    </ListGroup>
                </Card>
            )}

            {nearestNeededHospitals && nearestNeededHospitals.length > 0 && (
                 <Card className="mb-3">
                    <Card.Header>Nearest Hospitals in Need (of Surplus Blood Type)</Card.Header>
                    <ListGroup variant="flush">
                        {nearestNeededHospitals.map((hosp, index) => (
                            <ListGroup.Item key={index}>
                                {hosp.hospitalName}, {hosp.hospitalLocation} - Shortage Bags: {hosp.shortageBloodCount}
                            </ListGroup.Item>
                        ))}
                    </ListGroup>
                </Card>
            )}


            {recommendations && recommendations.recommendations && recommendations.recommendations.length > 0 && (
                <Card>
                    <Card.Header>Donation Recommendations</Card.Header>
                    <ListGroup variant="flush">
                        {recommendations.recommendations.map((rec, index) => (
                            <ListGroup.Item key={index}>
                                {rec}
                            </ListGroup.Item>
                        ))}
                    </ListGroup>
                </Card>
            )}
             {recommendations && recommendations.recommendations && recommendations.recommendations.length === 0 && (
                <Alert variant="info">No specific blood donation recommendations at this time based on available data.</Alert>
             )}


        </Container>
    );
}

export default HospitalDashboardPage;