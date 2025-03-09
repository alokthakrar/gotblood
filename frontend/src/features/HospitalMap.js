import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap, Polyline } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import '../styles/Map.css';
import hospitalIconSrc from '../assets/hospital.png'; // Import your PNG hospital icon

// Blood shortage severity colors (more intensity = higher severity)
const getSeverityColor = (totalBloodCC) => { // Using totalBloodCC for severity now
    if (totalBloodCC < 100) return '#ff0000'; // Red (Critical - adjust threshold as needed)
    if (totalBloodCC < 300) return '#ff6600'; // Orange (Moderate - adjust threshold as needed)
    if (totalBloodCC < 500) return '#ffcc00'; // Yellow (Low - adjust threshold as needed)
    return '#66cc66'; // Green (Adequate stock)
};

// Create custom hospital icon with shortage severity overlay
const createHospitalIcon = (totalBloodCC) => { // Using totalBloodCC for severity
    const iconSize = 40; // Adjust the size for better visibility

    return L.divIcon({
        className: 'custom-hospital-icon',
        html: `
      <div style="position: relative; width: ${iconSize}px; height: ${iconSize}px;">
        <img src="${hospitalIconSrc}" style="width: 100%; height: 100%; display: block;" />
        <div style="
          position: absolute;
          top: -5px;
          right: -5px;
          width: 15px;
          height: 15px;
          background-color: ${getSeverityColor(totalBloodCC)};
          border-radius: 50%;
          border: 2px solid white;
          box-shadow: 0 0 5px rgba(0,0,0,0.3);
        "></div>
      </div>
    `,
        iconSize: [iconSize, iconSize], // Size of the icon
        iconAnchor: [iconSize / 2, iconSize], // Anchor at bottom center
        popupAnchor: [0, -iconSize / 2], // Adjust popup position
    });
};

// Component to fit map view to markers
const FitMapBounds = ({ locations }) => {
    const map = useMap();

    React.useEffect(() => {
        if (locations.length > 0) {
            const bounds = L.latLngBounds(locations);
            map.fitBounds(bounds, { padding: [50, 50] });
        }
    }, [locations, map]);

    return null;
};

const HospitalMap = () => {
    const [data, setData] = useState([]);
    const [mapHospitals, setMapHospitals] = useState([]); // State for map-ready hospital data
    const [hospitalMatches, setHospitalMatches] = useState({}); // State to store API matches

    useEffect(() => {
        const fetchDataAsync = async () => { // Wrap fetchData in an async function
            try {
                const response = await fetch('http://localhost:5001/hospital/dataLoc');
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const jsonData = await response.json();
                setData(jsonData);
                console.log("Fetched JSON Data for Map:", jsonData); // Log fetched data

                // **Data Transformation and Matching API Calls:** Prepare data for the map
                const transformedHospitals = [];
                const matches = {}; // Object to store matches temporarily

                for (const hospitalEntry of jsonData) {
                    const hospitalName = hospitalEntry.hospital;
                    const cityState = `${hospitalEntry.city}`;
                    const coordinates = hospitalEntry.coordinates;
                    const bloodDataArray = hospitalEntry.bloodData;

                    // Calculate representative shortage severity based on total blood count
                    let totalBloodCC = 0;
                    bloodDataArray.forEach(btData => {
                        totalBloodCC += btData.totalBloodCC;
                    });

                    transformedHospitals.push({
                        name: hospitalName,
                        coords: [coordinates.lat, coordinates.lon],
                        shortageSeverity: totalBloodCC,
                        cityState: cityState,
                        bloodTypes: bloodDataArray
                    });

                    // **Call Matching API for each hospital**
                    try {
                        const matchResponse = await fetch(
                            `http://localhost:5001/hospital/matching/shortage?surplus_hospital=${encodeURIComponent(hospitalName)}&surplus_city=${encodeURIComponent(cityState)}&blood_type=O+` // Using 'O+' as default blood type for matching
                        );
                        if (matchResponse.ok) {
                            const matchData = await matchResponse.json();
                            matches[hospitalName] = matchData; // Store matches with hospital name as key
                            console.log(`Matches for ${hospitalName}:`, matchData);
                        } else {
                            console.warn(`Matching API failed for ${hospitalName}: Status ${matchResponse.status}`);
                            matches[hospitalName] = []; // Store empty array if API call fails
                        }
                    } catch (matchError) {
                        console.error(`Error calling matching API for ${hospitalName}:`, matchError);
                        matches[hospitalName] = []; // Store empty array on error
                    }
                }
                setMapHospitals(transformedHospitals);
                setHospitalMatches(matches); // Set the matches state after processing all hospitals

            } catch (error) {
                console.error("Error fetching hospital data:", error);
                setData([]);
                setMapHospitals([]);
                setHospitalMatches({}); // Clear matches on error
            }
        };

        fetchDataAsync();
    }, []);


    return (
        <div className="map-wrapper">
            <MapContainer
                center={[37.0902, -95.7129]}
                zoom={4}
                className="map"
                maxBounds={[
                    [24.396308, -125.0], // Southwest corner (bottom-left)
                    [49.384358, -66.93457], // Northeast corner (top-right)
                ]}
                scrollWheelZoom={true} // Allow zooming with scroll
            >
                <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution="© OpenStreetMap contributors"
                />

                {/* Add hospital markers using mapHospitals data */}
                {mapHospitals.map((hospital, index) => {
                    if (hospital.coords && hospital.coords[0] !== 0 && hospital.coords[1] !== 0) {
                        return (
                            <Marker
                                key={index}
                                position={hospital.coords}
                                icon={createHospitalIcon(hospital.shortageSeverity)}
                            >
                                <Popup>
                                    <div style={{ textAlign: 'center' }}>
                                        <strong>{hospital.name}</strong> <br />
                                        <p>{hospital.cityState}</p> <br />
                                        <p><strong>Total Blood Stock:</strong> {hospital.shortageSeverity} cc</p>
                                        <hr />
                                        <strong>Detailed Blood Stock Levels:</strong>
                                        <ul>
                                            {hospital.bloodTypes.map((btData, btIndex) => (
                                                <li key={btIndex}>
                                                    {btData.bloodType}: {btData.totalBloodCC} cc
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                </Popup>
                            </Marker>
                        );
                    } else {
                        console.warn(`Hospital "${hospital.name}" in ${hospital.cityState} skipped due to missing coordinates.`);
                        return null;
                    }
                })}

                {/* **Render Arrows for Matches** */}
                {mapHospitals.map((hospital, index) => {
                    const matchesForHospital = hospitalMatches[hospital.name] || []; // Get matches for this hospital
                    return matchesForHospital.map((match, matchIndex) => {
                        const matchedHospitalCoords = match.coordinates; // Assuming match object has coordinates
                        if (matchedHospitalCoords && hospital.coords && hospital.coords[0] !== 0 && hospital.coords[1] !== 0 && matchedHospitalCoords.lat !== 0 && matchedHospitalCoords.lon !== 0) {
                            const arrowPoints = [hospital.coords, [matchedHospitalCoords.lat, matchedHospitalCoords.lon]];
                            return (
                                <Polyline
                                    key={`${index}-match-${matchIndex}`}
                                    positions={arrowPoints}
                                    color="blue" // Customize arrow color
                                    weight={2}     // Customize arrow weight
                                    opacity={0.7}    // Customize arrow opacity
                                    dashArray="4"   // Optional: dashed line style
                                >
                                    <Popup>
                                        {`Match from ${hospital.name} to ${match.hospital} for blood type O+`} {/* Customize popup content */}
                                    </Popup>
                                </Polyline>
                            );
                        }
                        return null; // Don't render arrow if coordinates are missing or invalid
                    });
                })}


                {/* Fit map to markers using mapHospitals coords */}
                <FitMapBounds locations={mapHospitals.filter(h => h.coords && h.coords[0] !== 0 && h.coords[1] !== 0).map(h => h.coords)} />
            </MapContainer>
        </div>
    );
};

export default HospitalMap;