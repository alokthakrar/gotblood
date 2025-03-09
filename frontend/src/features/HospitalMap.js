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
    const [surplusMatches, setSurplusMatches] = useState([]); // State for surplus matches
    const [loadingMatches, setLoadingMatches] = useState(false);
    const [matchError, setMatchError] = useState(null);

    // **Define Shortage Hospital Details Here** - Make Dynamic Later if Needed
    const shortageHospitalName = "General Hospital 1"; // Example shortage hospital
    const shortageCityState = "Los Angeles, CA"; // Example shortage city/state
    const bloodTypeForMatching = "O+"; // Example blood type for matching
    const maxMatchingResults = 5; // Example max ¿
    
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

        const fetchSurplusData = async () => {
            setLoadingMatches(true);
            setMatchError(null);
            try {
                // Build URL for surplus matching
                /*
                const shortageHospitalEncoded = encodeURIComponent(shortageHospitalName);
                const shortageCityEncoded = encodeURIComponent(shortageCityState);
                const bloodTypeEncoded = encodeURIComponent(bloodTypeForMatching);
                const url = `http://localhost:5001/hospital/matching/surplus?shortage_hospital=${shortageHospitalEncoded}&shortage_city=${shortageCityEncoded}&blood_type=${bloodTypeEncoded}&max_results=${maxMatchingResults}`;
                */
                const surplusHospitalEncoded = encodeURIComponent("Central Medical Center"); // Match curl value
                const surplusCityEncoded = encodeURIComponent("Boston, MA"); // Match curl value
                const bloodTypeEncoded = encodeURIComponent("A+");
                const maxResults = 5;
                
                // Use /hospital/matching/shortage endpoint (match curl)
                const url = `http://localhost:5001/hospital/matching/shortage?surplus_hospital=${surplusHospitalEncoded}&surplus_city=${surplusCityEncoded}&blood_type=${bloodTypeEncoded}&max_results=${maxResults}`;
                const matchResponse = await fetch(url);
                if (!matchResponse.ok) {
                    throw new Error(`Matching API Error: ${matchResponse.status}`);
                }
                const matchData = await matchResponse.json();
                setSurplusMatches(matchData);
                console.log("Surplus Matches Fetched:", matchData);
            } catch (err) {
                setMatchError(err.message);
                console.error("Error fetching surplus matches:", err);
                setSurplusMatches([]); // Clear matches on error
            } finally {
                setLoadingMatches(false);
            }
        };


        fetchDataAsync();
        fetchSurplusData(); // Fetch surplus matches when component mounts

    }, []);


    // Find coordinates of the shortage hospital
    const shortageHospitalInfo = mapHospitals.find(h => h.name === shortageHospitalName && h.cityState === shortageCityState);
    const shortageHospitalCoords = shortageHospitalInfo ? shortageHospitalInfo.coords : null;


    return (
        <div className="map-wrapper">
            <h2>Hospital Blood Supply Map</h2>
            {matchError && <p style={{ color: 'red' }}>Error fetching matches: {matchError}</p>}
            {loadingMatches && <p>Loading surplus hospital matches...</p>}

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

                {/* **Render Arrows for Surplus Matches** */}
                {surplusMatches.map((match, matchIndex) => {
                    const matchedHospitalCoords = match.coordinates; // Coordinates of surplus hospital
                    if (shortageHospitalCoords && matchedHospitalCoords && shortageHospitalCoords[0] !== 0 && shortageHospitalCoords[1] !== 0 && matchedHospitalCoords.lat !== 0 && matchedHospitalCoords.lon !== 0) {
                        const arrowPoints = [shortageHospitalCoords, [matchedHospitalCoords.lat, matchedHospitalCoords.lon]]; // From shortage to surplus
                        return (
                            <Polyline
                                key={`surplus-match-${matchIndex}`}
                                positions={arrowPoints}
                                color="green" // Surplus arrows in green
                                weight={3}
                                opacity={0.8}
                            >
                                <Popup>
                                    {`Potential Blood Supply from ${match.hospital} to ${shortageHospitalName} (Blood Type ${bloodTypeForMatching}) - Distance: ${match.distance_km} km`}
                                </Popup>
                            </Polyline>
                        );
                    }
                    return null; // Don't render arrow if coordinates are missing
                })}


                {/* Fit map to markers using mapHospitals coords */}
                <FitMapBounds locations={mapHospitals.filter(h => h.coords && h.coords[0] !== 0 && h.coords[1] !== 0).map(h => h.coords)} />
            </MapContainer>
        </div>
    );
};

export default HospitalMap;