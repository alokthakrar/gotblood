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
    const [largestShortageHospitalMatch, setLargestShortageHospitalMatch] = useState(null); // State for largest shortage match
    const [loadingMatches, setLoadingMatches] = useState(false);
    const [matchError, setMatchError] = useState(null);

    // **Define Node of Interest (Surplus Hospital in API context) **
    const nodeOfInterestName = "Central Medical Center"; // Node of interest is now Central Medical Center
    const nodeOfInterestCityState = "Boston, MA";
    const bloodTypeForMatching = "A+";
    const maxMatchingResults = 5;

    useEffect(() => {
        const fetchDataAsync = async () => { // Wrap fetchData in an async function
            try {
                const response = await fetch('http://localhost:5001/hospital/data/loc');
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const jsonData = await response.json();
                setData(jsonData);
                console.log("Fetched JSON Data for Map:", jsonData); // Log fetched data

                // **Data Transformation:** Prepare data for the map (same as before)
                const transformedHospitals = [];
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
                }
                setMapHospitals(transformedHospitals);


            } catch (error) {
                console.error("Error fetching hospital data:", error);
                setData([]);
                setMapHospitals([]);
            }
        };

        const fetchLargestShortageMatch = async () => {
            setLoadingMatches(true);
            setMatchError(null);
            setLargestShortageHospitalMatch(null); // Clear previous match

            try {
                // Build URL for shortage matching (using 'shortage' endpoint as before)
                const surplusHospitalEncoded = encodeURIComponent(nodeOfInterestName); // Node of interest as surplus hospital
                const surplusCityEncoded = encodeURIComponent(nodeOfInterestCityState);
                const bloodTypeEncoded = encodeURIComponent(bloodTypeForMatching);
                const maxResults = maxMatchingResults;

                const url = `http://localhost:5001/hospital/matching/shortage?surplus_hospital=${surplusHospitalEncoded}&surplus_city=${surplusCityEncoded}&blood_type=${bloodTypeEncoded}&max_results=${maxResults}`;
                const matchResponse = await fetch(url);
                if (!matchResponse.ok) {
                    throw new Error(`Matching API Error: ${matchResponse.status}`);
                }
                const matchData = await matchResponse.json();

                if (matchData && matchData.length > 0) {
                    // Find hospital with the largest shortage (smallest totalBloodCC)
                    const largestShortageMatch = matchData.reduce((minShortageHospital, currentHospital) => {
                        return (currentHospital.totalBloodCC < minShortageHospital.totalBloodCC) ? currentHospital : minShortageHospital;
                    }, matchData[0]); // Assume first hospital is initial min

                    setLargestShortageHospitalMatch(largestShortageMatch);
                    console.log("Largest Shortage Hospital Match:", largestShortageMatch);
                } else {
                    setLargestShortageHospitalMatch(null); // No matches found
                    console.log("No shortage matches found for node of interest.");
                }


            } catch (err) {
                setMatchError(err.message);
                console.error("Error fetching shortage matches:", err);
                setLargestShortageHospitalMatch(null); // Clear match on error
            } finally {
                setLoadingMatches(false);
            }
        };


        fetchDataAsync();
        fetchLargestShortageMatch(); // Fetch largest shortage match when component mounts

    }, []);


    // Find coordinates of the node of interest (Central Medical Center)
    const nodeOfInterestInfo = mapHospitals.find(h => h.name === nodeOfInterestName && h.cityState === nodeOfInterestCityState);
    const nodeOfInterestCoords = nodeOfInterestInfo ? nodeOfInterestInfo.coords : null;

    console.log("Node of Interest:", nodeOfInterestName, nodeOfInterestCityState); // DEBUG LOG
    console.log("Node of Interest Coords:", nodeOfInterestCoords); // DEBUG LOG
    console.log("Largest Shortage Match:", largestShortageHospitalMatch); // DEBUG LOG


    return (
        <div className="map-wrapper">
            <h2>Hospital Blood Supply Map</h2>
            {matchError && <p style={{ color: 'red' }}>Error fetching matches: {matchError}</p>}
            {loadingMatches && <p>Loading shortage matches...</p>}

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

                {/* **Render Arrow to Hospital with Largest Shortage** */}
                {(() => { // Immediately invoked function expression for logging just before Polyline
                    console.log("Rendering Polyline Condition:");
                    console.log("largestShortageHospitalMatch:", largestShortageHospitalMatch);
                    console.log("nodeOfInterestCoords:", nodeOfInterestCoords);
                    console.log("largestShortageHospitalMatch Coordinates:", largestShortageHospitalMatch?.coordinates);
                    const shouldRenderPolyline = largestShortageHospitalMatch && nodeOfInterestCoords && largestShortageHospitalMatch.coordinates && nodeOfInterestCoords[0] !== 0 && nodeOfInterestCoords[1] !== 0 && largestShortageHospitalMatch.coordinates.lat !== 0 && largestShortageHospitalMatch.coordinates.lon !== 0;
                    console.log("Should Render Polyline:", shouldRenderPolyline);
                    return shouldRenderPolyline ? (
                        <Polyline
                            positions={[nodeOfInterestCoords, [largestShortageHospitalMatch.coordinates.lat, largestShortageHospitalMatch.coordinates.lon]]}
                            color="red" // Arrow to largest shortage in red
                            weight={4}
                            opacity={0.9}
                        >
                            <Popup>
                                {`Largest Shortage Hospital: ${largestShortageHospitalMatch.hospital} (Blood Type ${bloodTypeForMatching}) - Shortage Level: ${largestShortageHospitalMatch.totalBloodCC} cc`}
                            </Popup>
                        </Polyline>
                    ) : null;
                })()}


                {/* Fit map to markers using mapHospitals coords */}
                <FitMapBounds locations={mapHospitals.filter(h => h.coords && h.coords[0] !== 0 && h.coords[1] !== 0).map(h => h.coords)} />
            </MapContainer>
        </div>
    );
};

export default HospitalMap;