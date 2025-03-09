import streamlit as st
from pymongo import MongoClient
import folium
from streamlit_folium import folium_static

# Function to connect to MongoDB and fetch data
def get_hospital_data(blood_filter=None):
    client = MongoClient("mongodb://localhost:27017")
    db = client["americanRedCrossDB"]
    
    # Build query based on the blood type filter (assuming backend already classifies)
    query = {}
    if blood_filter and blood_filter != "All":
        query = {"inventoryStats.bloodType": blood_filter}
    
    # Get hospital data
    hospitals = list(db.donorStats.find(query))
    
    return hospitals

# Function to display hospital data in a table
def display_hospitals(hospitals):
    if hospitals:
        st.write(f"Found {len(hospitals)} hospitals:")
        for hospital in hospitals:
            st.write(f"**{hospital['hospital']}** in {hospital['city']}")
            st.write("Blood Availability:")
            for bt in hospital["inventoryStats"]:
                st.write(f"  - Blood Type: {bt['bloodType']}, Total Blood: {bt['totalBloodCC']} CC")
            st.write("---")
    else:
        st.write("No hospitals found.")

# Function to display the map (with folium)
def display_map(hospitals):
    # Create a base map centered on a location (e.g., USA)
    map = folium.Map(location=[37.0902, -95.7129], zoom_start=4)

    # Add a marker for each hospital
    for hospital in hospitals:
        lat, lon = get_lat_lon(hospital['city'])  # Assuming you have a function to fetch lat/lon for city
        folium.Marker(
            [lat, lon],
            popup=f"{hospital['hospital']} - {hospital['city']}",
        ).add_to(map)

    # Display map in Streamlit
    folium_static(map)

# Streamlit UI components
st.title("Hospital Blood Availability Tracker")

st.sidebar.header("Filter Hospitals")
blood_filter = st.sidebar.selectbox(
    "Choose blood type:",
    ["All", "A", "B", "O", "AB"]
)

# Fetch and display filtered data
hospitals = get_hospital_data(blood_filter)
display_hospitals(hospitals)

# Display the map if data is available
if hospitals:
    display_map(hospitals)

