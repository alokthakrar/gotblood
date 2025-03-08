from pymongo import MongoClient
from datetime import datetime
import requests

#######################################
# Auth0 Configuration
#######################################

auth0_domain = dev-nzbenqyyuji62b1n.us.auth0.com  # Replace with your Auth0 domain
auth0_client_id = zVcYBqZQsx6d9mEwEaW1zQxT9gEiKHnA # Replace with your Auth0 client ID
auth0_client_secret = zxMUC-ND13MaB-2ED-_I0IZmlJHxbIJqiNehJCEhCrpi2diKEwQ9e-tqZIWos9gn  # Replace with your Auth0 client secret
auth0_audience = https://PassWordManager.com  # Replace with your Auth0 API identifier
auth0_token_url = f"https://{auth0_domain}/oauth/token"

#######################################
# Helper functions for Auth0
#######################################

def get_auth0_token():
    payload = {
        "client_id": auth0_client_id,
        "client_secret": auth0_client_secret,
        "audience": auth0_audience,
        "grant_type": "client_credentials"
    }
    response = requests.post(auth0_token_url, json=payload)
    response.raise_for_status()
    return response.json().get("access_token")

def verify_auth0_user(email, password):
    url = f"https://{auth0_domain}/oauth/token"
    payload = {
        "grant_type": "password",
        "username": email,
        "password": password,
        "audience": auth0_audience,
        "client_id": auth0_client_id,
        "client_secret": auth0_client_secret,
        "scope": "openid profile email"
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def register_auth0_user(email, password):
    url = f"https://{auth0_domain}/dbconnections/signup"
    payload = {
        "client_id": auth0_client_id,
        "email": email,
        "password": password,
        "connection": "Username-Password-Authentication"
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("User registered successfully.")
    else:
        print("Failed to register user:", response.json())

#######################################
# Hospital Management Functions
#######################################

def add_hospital(db, hospital_data, email, password):
    # Register the hospital in Auth0
    register_auth0_user(email, password)

    if "lid" not in hospital_data:
        count = db.locations.count_documents({})
        hospital_data["lid"] = "L{:04d}".format(count + 1)
    if "locationCode" not in hospital_data:
        hospital_data["locationCode"] = "HOSP"

    hospital_data["email"] = email  # Store the email for Auth0 login reference
    result = db.locations.insert_one(hospital_data)
    print(f"Hospital '{hospital_data['name']}' added with lid {hospital_data['lid']}.")
    return hospital_data

def update_hospital_inventory(db, hospital, city, bloodType, delta_count, email, password):
    # Verify Auth0 credentials
    auth_result = verify_auth0_user(email, password)
    if not auth_result:
        print("Authentication failed: Incorrect email or password.")
        return

    hosp_doc = db.locations.find_one({"name": hospital, "city": city})
    if not hosp_doc:
        print("Hospital not found!")
        return

    lid = hosp_doc["lid"]
    if delta_count > 0:
        for i in range(delta_count):
            new_bbid = "NEW" + str(db.bloodBags.count_documents({}) + 1)
            new_blood_bag = {
                "bbid": new_bbid,
                "donationType": "Whole Blood",
                "quantityCC": 450,
                "bloodType": bloodType,
                "available": True
            }
            db.bloodBags.insert_one(new_blood_bag)
            new_inventory = {
                "bbid": new_bbid,
                "lid": lid,
                "available": True
            }
            db.globalInventory.insert_one(new_inventory)
        print(f"Added {delta_count} blood bag(s) of type {bloodType} to {hospital} in {city}.")
    elif delta_count < 0:
        count_to_remove = -delta_count
        pipeline = [
            {"$lookup": {"from": "bloodBags", "localField": "bbid", "foreignField": "bbid", "as": "bag"}},
            {"$unwind": "$bag"},
            {"$match": {"lid": lid, "available": True, "bag.bloodType": bloodType}}
        ]
        available_bags = list(db.globalInventory.aggregate(pipeline))
        if len(available_bags) < count_to_remove:
            print(f"Not enough blood bags to remove. Available: {len(available_bags)}")
        else:
            for bag_record in available_bags[:count_to_remove]:
                db.globalInventory.delete_one({"_id": bag_record["_id"]})
                db.bloodBags.update_one({"bbid": bag_record["bag"]["bbid"]}, {"$set": {"available": False}})
            print(f"Removed {count_to_remove} blood bag(s) of type {bloodType} from {hospital} in {city}.")
    else:
        print("No change requested (delta_count is 0).")

def main():
    client = MongoClient("mongodb://localhost:27017")
    db = client["americanRedCrossDB"]

    # Example: Add a new hospital with email/password authentication.
    hospital_data = {
        "name": "Central Medical Center",
        "city": "Boston, MA",
        "coordinates": {"lat": 42.3601, "lon": -71.0589}
    }
    email = "hospital_admin@example.com"
    password = "securepassword123"

    new_hosp = add_hospital(db, hospital_data, email, password)
    hosp_name = new_hosp["name"]
    hosp_city = new_hosp["city"]

    # For each blood type, add 5 blood bags using Auth0 authentication.
    blood_types = ["O+", "A+", "B+", "AB+", "O-", "A-", "B-", "AB-"]
    for bt in blood_types:
        update_hospital_inventory(db, hosp_name, hosp_city, bt, 5, email, password)

if __name__ == "__main__":
    main()
