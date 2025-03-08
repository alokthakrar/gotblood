# backend/flask_server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from elasticsearch import Elasticsearch
# backend/flask_server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from elasticsearch import Elasticsearch

# Import Mailchimp library
from mailchimp_marketing import Client
from mailchimp_marketing.api_client import ApiClientError

app = Flask(__name__)
CORS(app)  # Enable CORS for development

# Elasticsearch setup (as before)
es_client = Elasticsearch("http://localhost:9200")


# Mailchimp Configuration
mailchimp = Client()
mailchimp.set_config({
    "api_key": "58d63b0d8745d5bad45f51d9eaecd283-us14",  # Replace with your actual API key
    "server": "us14"  # Replace with your server prefix (e.g., 'us1', 'us20')
})
MAILCHIMP_LIST_ID = "got blood?" # Replace with your Mailchimp list ID
@app.route('/api/signup', methods=['POST'])
def signup():
    signup_data = request.get_json()

    if not signup_data or 'email' not in signup_data:
        return jsonify({"error": "Email is required for signup."}), 400

    email = signup_data.get('email')
    blood_type = signup_data.get('bloodType')
    latitude = signup_data.get('latitude')
    longitude = signup_data.get('longitude')

    try:
        member_info = {
            "email_address": email,
            "status": "subscribed",  # or 'pending' if you want double opt-in
            "merge_fields": {
                "BLOODTYPE": blood_type,  # Merge tag names must be in ALL CAPS and match your Mailchimp audience fields
                "LATITUDE": latitude,     # Adjust merge tag names as needed in Mailchimp
                "LONGITUDE": longitude
            }
        }

        response = mailchimp.lists.add_list_member(MAILCHIMP_LIST_ID, member_info)
        print(f"Mailchimp API Response: {response}") # Optional: Log the response for debugging
        return jsonify({"message": "Signup successful! Added to Mailchimp list."}), 200

    except ApiClientError as error:
        print(f"Mailchimp API Error: {error.text}")
        return jsonify({"error": "Mailchimp signup failed.", "mailchimp_error": error.text}), 500
    except Exception as e:
        print(f"Signup error: {e}")
        return jsonify({"error": "Signup failed due to an unexpected error."}), 500

# ... (rest of your flask_server.py file, including /api/search, /api/generate_data, and data generation functions)

@app.route('/api/search')
def search():
    search_query = request.args.get('q')  # Get search query from request query parameters

    if not search_query:
        return jsonify({"error": "Search query 'q' is required."}), 400

    try:
        response = es_client.search(
            index='blood_bank_index',  # Your Elasticsearch index name
            query={
                "multi_match": {  # Simple example: search across multiple text fields
                    "query": search_query,
                    "fields": ['hospitalName', 'hospitalLocation', 'bloodType']  # Fields to search in
                }
            }
        )

        results = [hit['_source'] for hit in response['hits']['hits']]  # Extract source documents
        return jsonify(results)
    except Exception as e:
        print(f"Elasticsearch query error: {e}")
        return jsonify({"error": "Error querying Elasticsearch"}), 500

# Optional: Endpoint to trigger data generation (for development/setup)
from pymongo import MongoClient
from datetime import datetime, timedelta
import random

def wipe_database(db_name="americanRedCrossDB"):
    client = MongoClient("mongodb://localhost:27017")
    client.drop_database(db_name)
    print(f"Database '{db_name}' has been dropped.")

def generate_sample_hospitals(db, count=20):
    """... (rest of your generate_sample_hospitals function) ..."""
    cities = [
        {"city": "New York, NY", "lat": 40.7128, "lon": -74.0060},
        {"city": "Los Angeles, CA", "lat": 34.0522, "lon": -118.2437},
        {"city": "Chicago, IL", "lat": 41.8781, "lon": -87.6298},
        {"city": "Houston, TX", "lat": 29.7604, "lon": -95.3698},
        {"city": "Phoenix, AZ", "lat": 33.4484, "lon": -112.0740},
        {"city": "Philadelphia, PA", "lat": 39.9526, "lon": -75.1652},
        {"city": "San Antonio, TX", "lat": 29.4241, "lon": -98.4936},
        {"city": "San Diego, CA", "lat": 32.7157, "lon": -117.1611},
        {"city": "Dallas, TX", "lat": 32.7767, "lon": -96.7970},
        {"city": "San Jose, CA", "lat": 37.3382, "lon": -121.8863}
    ]

    base_names = ["General Hospital", "Community Health Center", "City Hospital", "Regional Medical Center", "Health Clinic"]
    hospitals = []

    for i in range(count):
        city_info = random.choice(cities)
        name = random.choice(base_names) + " " + str(i+1)
        hospital = {
            "lid": "L{:04d}".format(i+1),
            "name": name,
            "city": city_info["city"],
            "locationCode": "HOSP",
            "coordinates": {"lat": city_info["lat"], "lon": city_info["lon"]}
        }
        hospitals.append(hospital)
    db.locations.drop()
    db.locations.insert_many(hospitals)
    print(f"Inserted {count} sample hospitals.")

def generate_sample_donors(db, count=100):
    """... (rest of your generate_sample_donors function) ..."""
    donors = []
    blood_types = ["O+", "A+", "B+", "AB+", "O-", "A-", "B-", "AB-"]
    first_names = ["John", "Jane", "Alice", "Bob", "Carol", "Derek", "Eva", "Frank", "Grace", "Henry"]
    last_names = ["Doe", "Smith", "Brown", "Taylor", "Johnson", "Miller", "Davis", "Wilson", "Moore", "Anderson"]

    hospitals = list(db.locations.find())
    for i in range(count):
        hosp = random.choice(hospitals)
        donor = {
            "pid": "P{:07d}".format(i+1),
            "firstName": random.choice(first_names),
            "lastName": random.choice(last_names),
            "age": random.randint(18, 65),
            "role": "donor",
            "hospital": hosp["name"],
            "city": hosp["city"],
            "donorDetails": {
                "bloodType": random.choice(blood_types),
                "weightLBS": random.randint(110, 250),
                "heightIN": random.randint(60, 80),
                "gender": random.choice(["M", "F"]),
                "nextSafeDonation": datetime.now() + timedelta(days=random.randint(30, 100))
            }
        }
        donors.append(donor)
    db.persons.drop()
    db.persons.insert_many(donors)
    print(f"Inserted {count} sample donors.")

def generate_sample_inventory(db):
    """... (rest of your generate_sample_inventory function) ..."""
    blood_types = ["O+", "A+", "B+", "AB+", "O-", "A-", "B-", "AB-"]
    db.bloodBags.drop()
    db.globalInventory.drop()
    hospitals = list(db.locations.find())
    blood_bags = []
    inventory = []
    bbid_counter = 1
    for hosp in hospitals:
        for bt in blood_types:
            num_bags = random.randint(0, 10)
            if num_bags == 0:
                num_bags = 1  # Force at least one record per blood type.
                qty = 0
            else:
                qty = None  # Not used.
            for _ in range(num_bags):
                bbid = "BB{:04d}".format(bbid_counter)
                bbid_counter += 1
                current_qty = 0 if qty == 0 else random.choice([450, 500, 550])
                bag = {
                    "bbid": bbid,
                    "donationType": "Whole Blood",
                    "quantityCC": current_qty,
                    "bloodType": bt,
                    "available": True
                }
                blood_bags.append(bag)
                inv = {
                    "bbid": bbid,
                    "lid": hosp["lid"],
                    "available": True
                }
                inventory.append(inv)
    if blood_bags:
        db.bloodBags.insert_many(blood_bags)
    if inventory:
        db.globalInventory.insert_many(inventory)
    print("Inserted sample blood bags and global inventory for every blood type at each hospital.")

from databaseFunctions import update_secondary_data, update_inventory_flag # Assuming databaseFunctions.py is in the same directory

def randomize_flags(db):
    """... (rest of your randomize_flags function) ..."""
    donor_stats = list(db.donorStats.find())
    for stat in donor_stats:
        hospital = stat["hospital"]
        city = stat["city"]
        for bt_stat in stat.get("bloodTypeStats", []):
            blood_type = bt_stat["bloodType"]
            new_surplus = random.choice([True, False])
            new_shortage = random.choice([True, False])
            update_inventory_flag(db, hospital, city, blood_type, surplus=new_surplus, shortage=new_shortage)
    print("Randomized flag settings updated.")

def generate_all_sample_data():
    client = MongoClient("mongodb://localhost:27017")
    db = client["americanRedCrossDB"]
    wipe_database("americanRedCrossDB")
    generate_sample_hospitals(db, count=20)
    generate_sample_donors(db, count=100)
    generate_sample_inventory(db)
    print("All sample data generated.")
    update_secondary_data(db)
    randomize_flags(db)

@app.route('/api/generate_data') # New route to trigger data generation
def generate_data():
    generate_all_sample_data()
    return jsonify({"message": "Sample data generated successfully!"})


if __name__ == '__main__':
    app.run(debug=True, port=5000) # Run Flask app