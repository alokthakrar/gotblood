#!/usr/bin/env python3
import requests
import random

# Base URL for your Flask app endpoints (adjust if needed)
BASE_URL = "http://localhost:5001"
TEST_PASSWORD = "testPassword"
BLOOD_TYPES = ["O+", "A+", "B+", "AB+", "O-", "A-", "B-", "AB-"]

# List of real cities with coordinates
CITIES = [
    {"city": "New York, NY", "lat": 40.7128, "lon": -74.0060},
    {"city": "Los Angeles, CA", "lat": 34.0522, "lon": -118.2437},
    {"city": "Chicago, IL", "lat": 41.8781, "lon": -87.6298},
    {"city": "Houston, TX", "lat": 29.7604, "lon": -95.3698},
    {"city": "Phoenix, AZ", "lat": 33.4484, "lon": -112.0740},
    {"city": "Philadelphia, PA", "lat": 39.9526, "lon": -75.1652},
    {"city": "San Antonio, TX", "lat": 29.4241, "lon": -98.4936},
    {"city": "San Diego, CA", "lat": 32.7157, "lon": -117.1611},
    {"city": "Dallas, TX", "lat": 32.7767, "lon": -96.7970},
    {"city": "San Jose, CA", "lat": 37.3382, "lon": -121.8863},
    {"city": "Austin, TX", "lat": 30.2672, "lon": -97.7431},
    {"city": "Jacksonville, FL", "lat": 30.3322, "lon": -81.6557},
    {"city": "Fort Worth, TX", "lat": 32.7555, "lon": -97.3308},
    {"city": "Columbus, OH", "lat": 39.9612, "lon": -82.9988},
    {"city": "Charlotte, NC", "lat": 35.2271, "lon": -80.8431},
    {"city": "San Francisco, CA", "lat": 37.7749, "lon": -122.4194},
    {"city": "Indianapolis, IN", "lat": 39.7684, "lon": -86.1581},
    {"city": "Seattle, WA", "lat": 47.6062, "lon": -122.3321},
    {"city": "Denver, CO", "lat": 39.7392, "lon": -104.9903},
    {"city": "Washington, DC", "lat": 38.9072, "lon": -77.0369}
]

def generate_flag_settings():
    """
    Returns a dictionary with randomized flag settings for each blood type.
    Each blood type gets random boolean values for "surplus" and "shortage".
    """
    return {bt: {"surplus": random.choice([True, False]),
                 "shortage": random.choice([True, False])}
            for bt in BLOOD_TYPES}

def create_hospital(hospital_data):
    """
    Sends a POST request to /hospital/create endpoint with hospital_data.
    Returns the created hospital data if successful, or None.
    """
    url = f"{BASE_URL}/hospital/create"
    response = requests.post(url, json=hospital_data)
    if response.status_code == 201:
        print(f"Created hospital: {hospital_data['name']} in {hospital_data['city']}")
        return response.json().get("hospital")
    else:
        print(f"Failed to create hospital {hospital_data['name']}: {response.text}")
        return None

def update_inventory(hospital, city, blood_type, delta_count):
    """
    Sends a POST request to /hospital/inventory/update to update blood inventory.
    """
    url = f"{BASE_URL}/hospital/inventory/update"
    payload = {
        "hospital": hospital,
        "city": city,
        "bloodType": blood_type,
        "delta_count": delta_count,
        "password": TEST_PASSWORD
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print(f"Updated inventory for {hospital} ({city}) - {blood_type}: delta {delta_count}")
    else:
        print(f"Failed to update inventory for {hospital} ({city}) - {blood_type}: {response.text}")

def generate_hospitals(total_hospitals=250):
    """
    Generates 'total_hospitals' hospitals in various cities.
    For each hospital:
      - A random city is chosen from CITIES.
      - The hospital name is constructed using the city name and an index.
      - Randomized flag settings are generated.
      - The /hospital/create endpoint is called.
      - For each blood type, a random number (0 to 20) is added to the inventory.
    """
    created_hospitals = []
    for i in range(1, total_hospitals + 1):
        city_info = random.choice(CITIES)
        hospital_name = f"{city_info['city']} Hospital {i}"
        flag_settings = generate_flag_settings()
        hospital_data = {
            "name": hospital_name,
            "city": city_info["city"],
            "coordinates": {"lat": city_info["lat"], "lon": city_info["lon"]},
            "password": TEST_PASSWORD,
            "flagSettings": flag_settings
        }
        created = create_hospital(hospital_data)
        if created:
            created_hospitals.append(created)
            # Update inventory for each blood type with a random delta (0 to 20)
            for bt in BLOOD_TYPES:
                delta = random.randint(0, 20)
                update_inventory(hospital_name, city_info["city"], bt, delta)
    return created_hospitals

def main():
    hospitals = generate_hospitals(250)
    print(f"Generated {len(hospitals)} hospitals.")

if __name__ == "__main__":
    main()
