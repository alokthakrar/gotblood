# hospital_managment.py
from pymongo import MongoClient
from datetime import datetime
import math
import random
import requests

#######################################
# Auth0 Configuration and Helper Functions (Integrated)
#######################################

auth0_domain = "dev-ad14rnf5k6iwyi22.us.auth0.com"  # Your Auth0 domain
auth0_client_id = "DKtSjVvqZ08VmXoOOAlNiCbHNRXiqIWu"  # Your Auth0 client ID
auth0_client_secret = "IhlJLDVqyrQkI_fTXp6Gwa-yLPShxH3I6Z98c9SCUwreuMMMjR-YwxMpOGzfh8EV"  # Your Auth0 client secret
auth0_audience = "https://password.com/"  # Your Auth0 API identifier
auth0_token_url = f"https://{auth0_domain}/oauth/token"

# Set TEST_MODE to True to bypass real Auth0 calls for local testing.
TEST_MODE = True

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

def verify_auth0_user(username, password):
    """
    Verifies the user credentials via Auth0.
    In TEST_MODE, we use a simple mapping where the hospital name is the username.
    Debug prints show the username, provided password, and expected value.
    """
    if TEST_MODE:
        test_passwords = {
            "Central Medical Center": "pass123",
            "General Hospital 1": "securePass",
            "City Hospital 1": "hospitalNY",
            "Regional Medical Center": "chicagoPass",
            "Health Clinic": "houstonClinic"
        }
        expected = test_passwords.get(username)
        print(f"[DEBUG] verify_auth0_user: Checking username='{username}' with provided password='{password}', expected='{expected}'")
        if expected and expected == password:
            return {"access_token": "TEST_TOKEN"}
        else:
            return None
    else:
        url = f"https://{auth0_domain}/oauth/token"
        payload = {
            "grant_type": "password",
            "username": username,
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

def register_auth0_user(username, password):
    """
    Registers a new user with Auth0.
    In TEST_MODE, simply prints a message.
    """
    if TEST_MODE:
        print(f"[TEST_MODE] Registered Auth0 user: {username}")
    else:
        url = f"https://{auth0_domain}/dbconnections/signup"
        payload = {
            "client_id": auth0_client_id,
            "email": username,  # using hospital name as username/email
            "password": password,
            "connection": "Username-Password-Authentication"
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("User registered successfully.")
        else:
            print("Failed to register user:", response.json())

#######################################
# Aggregation & Update Functions (Internal)
#######################################

def aggregate_donor_data_by_location(db):
    pipeline = [
        {"$match": {"role": "donor"}},
        {"$group": {
            "_id": {"hospital": "$hospital", "city": "$city", "bloodType": "$donorDetails.bloodType"},
            "donorCount": {"$sum": 1}
        }},
        {"$group": {
            "_id": {"hospital": "$_id.hospital", "city": "$_id.city"},
            "bloodTypeStats": {"$push": {
                "bloodType": "$_id.bloodType",
                "donorCount": "$donorCount",
                "surplus": False,
                "shortage": False
            }}
        }},
        {"$project": {
            "_id": 0,
            "hospital": "$_id.hospital",
            "city": "$_id.city",
            "bloodTypeStats": 1
        }}
    ]
    return list(db.persons.aggregate(pipeline))

def aggregate_inventory_by_location(db):
    pipeline = [
        {"$lookup": {"from": "bloodBags", "localField": "bbid", "foreignField": "bbid", "as": "bag"}},
        {"$unwind": "$bag"},
        {"$lookup": {"from": "locations", "localField": "lid", "foreignField": "lid", "as": "loc"}},
        {"$unwind": "$loc"},
        {"$match": {"available": True}},
        {"$group": {
            "_id": {"hospital": "$loc.name", "city": "$loc.city", "bloodType": "$bag.bloodType"},
            "totalBloodCC": {"$sum": "$bag.quantityCC"}
        }},
        {"$group": {
            "_id": {"hospital": "$_id.hospital", "city": "$_id.city"},
            "inventoryStats": {"$push": {
                "bloodType": "$_id.bloodType",
                "totalBloodCC": "$totalBloodCC"
            }}
        }},
        {"$project": {"_id": 0, "hospital": "$_id.hospital", "city": "$_id.city", "inventoryStats": 1}}
    ]
    return list(db.globalInventory.aggregate(pipeline))

def merge_secondary_data(donor_stats, inventory_stats):
    """
    Merges the donor_stats and inventory_stats based on hospital and city.
    This version safely checks for the keys "hospital" and "city" in each document.
    """
    inv_lookup = {}
    for doc in inventory_stats:
        hospital = doc.get("hospital")
        city = doc.get("city")
        if hospital is not None and city is not None:
            inv_lookup[(hospital, city)] = doc.get("inventoryStats", [])
    
    merged = []
    for stat in donor_stats:
        hospital = stat.get("hospital")
        city = stat.get("city")
        key = (hospital, city)
        # If keys don't exist, default to an empty list.
        stat["inventoryStats"] = inv_lookup.get(key, [])
        merged.append(stat)
    return merged

def create_secondary_collection(db, merged_data):
    db.donorStats.drop()
    db.donorStats.insert_many(merged_data)

def update_secondary_data(db):
    donor_stats = aggregate_donor_data_by_location(db)
    inventory_stats = aggregate_inventory_by_location(db)
    merged_data = merge_secondary_data(donor_stats, inventory_stats)
    
    complete_blood_types = ["O+", "A+", "B+", "AB+", "O-", "A-", "B-", "AB-"]
    hospitals = list(db.locations.find())
    
    # Build lookup only for records that have both 'hospital' and 'city'
    merged_dict = {
        (rec.get("hospital"), rec.get("city")): rec
        for rec in merged_data
        if rec.get("hospital") is not None and rec.get("city") is not None
    }
    
    # Preserve existing flags if any
    existing_flags = {}
    for rec in db.donorStats.find():
        key = (rec.get("hospital"), rec.get("city"))
        if not key[0] or not key[1]:
            continue
        flags = {}
        for bt in rec.get("bloodTypeStats", []):
            flags[bt.get("bloodType")] = (bt.get("surplus", False), bt.get("shortage", False))
        existing_flags[key] = flags
    
    for hosp in hospitals:
        key = (hosp.get("name"), hosp.get("city"))
        if key not in merged_dict:
            merged_dict[key] = {"hospital": hosp.get("name"), "city": hosp.get("city"),
                                "bloodTypeStats": [], "inventoryStats": []}
        record = merged_dict[key]
        new_bt_stats = []
        # Use flagSettings from hospital document if available
        flag_settings = hosp.get("flagSettings", {})  # e.g. {"A+": {"surplus": True, "shortage": False}, ...}
        for bt in complete_blood_types:
            computed = next((item for item in record.get("bloodTypeStats", []) if item.get("bloodType") == bt), None)
            donorCount = computed.get("donorCount") if computed else 0
            if bt in flag_settings:
                flags = (flag_settings[bt].get("surplus", False), flag_settings[bt].get("shortage", False))
            else:
                flags = existing_flags.get(key, {}).get(bt, (False, False))
            new_bt_stats.append({
                "bloodType": bt,
                "donorCount": donorCount,
                "surplus": flags[0],
                "shortage": flags[1]
            })
        record["bloodTypeStats"] = new_bt_stats
        
        new_inv_stats = []
        for bt in complete_blood_types:
            computed_inv = next((item for item in record.get("inventoryStats", []) if item.get("bloodType") == bt), None)
            totalBloodCC = computed_inv.get("totalBloodCC") if computed_inv else 0
            new_inv_stats.append({
                "bloodType": bt,
                "totalBloodCC": totalBloodCC
            })
        record["inventoryStats"] = new_inv_stats

    completed_merged_data = list(merged_dict.values())
    create_secondary_collection(db, completed_merged_data)
    print("Secondary collection 'donorStats' updated with complete data.")


#######################################
# Donor and Inventory Management Functions (with Auth0 integration)
#######################################

def add_donor(db, donor_data):
    donor_data["role"] = "donor"
    result = db.persons.insert_one(donor_data)
    print(f"Donor with pid {donor_data['pid']} added. Inserted ID: {result.inserted_id}")

def remove_donor(db, pid):
    result = db.persons.delete_one({"pid": pid, "role": "donor"})
    if result.deleted_count > 0:
        print(f"Donor with pid {pid} removed.")
    else:
        print(f"No donor with pid {pid} found.")

def add_donor_and_update(db, donor_data):
    add_donor(db, donor_data)
    update_secondary_data(db)

def remove_donor_and_update(db, pid):
    remove_donor(db, pid)
    update_secondary_data(db)

def update_hospital_inventory(db, hospital, city, bloodType, delta_count, password):
    hosp_doc = db.locations.find_one({"name": hospital, "city": city})
    if not hosp_doc:
        print("Hospital not found!")
        return
    auth_response = verify_auth0_user(hospital, password)
    if not auth_response:
        print("Authentication failed: Incorrect password.")
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
    
    update_secondary_data(db)
    
    pipeline_inventory = [
        {"$lookup": {"from": "bloodBags", "localField": "bbid", "foreignField": "bbid", "as": "bag"}},
        {"$unwind": "$bag"},
        {"$lookup": {"from": "locations", "localField": "lid", "foreignField": "lid", "as": "loc"}},
        {"$unwind": "$loc"},
        {"$match": {"loc.name": hospital, "loc.city": city, "available": True}},
        {"$group": {"_id": "$bag.bloodType", "totalBloodCC": {"$sum": "$bag.quantityCC"}}},
        {"$project": {"_id": 0, "bloodType": "$_id", "totalBloodCC": 1}}
    ]
    current_inventory = list(db.globalInventory.aggregate(pipeline_inventory))
    print("Current Inventory by Blood Type:")
    for inv in current_inventory:
        print(inv)

def update_inventory_flag(db, hospital, city, blood_type, surplus=None, shortage=None, password=None):
    hosp_doc = db.locations.find_one({"name": hospital, "city": city})
    if not hosp_doc:
        print("Hospital not found!")
        return
    if password is None or not verify_auth0_user(hospital, password):
        print("Authentication failed: Incorrect password.")
        return

    update_doc = {}
    if surplus is not None:
        update_doc["bloodTypeStats.$[elem].surplus"] = surplus
    if shortage is not None:
        update_doc["bloodTypeStats.$[elem].shortage"] = shortage
    if update_doc:
        result = db.donorStats.update_one(
            {"hospital": hospital, "city": city},
            {"$set": update_doc},
            array_filters=[{"elem.bloodType": blood_type}]
        )
        if result.modified_count > 0:
            print(f"Updated flags for {hospital}, {city}, blood type {blood_type}.")
        else:
            print(f"No matching record found to update flags for {hospital}, {city}, blood type {blood_type}.")

def add_hospital(db, hospital_data):
    if "lid" not in hospital_data:
        count = db.locations.count_documents({})
        hospital_data["lid"] = "L{:04d}".format(count + 1)
    if "locationCode" not in hospital_data:
        hospital_data["locationCode"] = "HOSP"
    if "password" not in hospital_data:
        print("No password provided; hospital not added.")
        return None
    # Register with Auth0 using hospital name as username.
    register_auth0_user(hospital_data["name"], hospital_data["password"])
    # For testing, we insert the hospital document.
    db.locations.insert_one(hospital_data)
    print(f"Hospital '{hospital_data['name']}' added with lid {hospital_data['lid']}.")
    return hospital_data

def search_secondary(db, hospital, city):
    result = db.donorStats.find_one({"hospital": hospital, "city": city})
    return result

def main():
    client = MongoClient("mongodb://localhost:27017")
    db = client["americanRedCrossDB"]

    update_secondary_data(db)
    
    print("Hospitals in the database:")
    for hosp in db.locations.find():
        print(f"{hosp['name']} - {hosp['city']}")
    
    # Example: Add a new hospital with Auth0 registration.
    hospital_data = {
        "name": "Central Medical Center",
        "city": "Boston, MA",
        "coordinates": {"lat": 42.3601, "lon": -71.0589},
        "password": "pass123"
    }
    new_hosp = add_hospital(db, hospital_data)
    if new_hosp:
        hosp_name = new_hosp["name"]
        hosp_city = new_hosp["city"]
    
        blood_types = ["O+", "A+", "B+", "AB+", "O-", "A-", "B-", "AB-"]
        for bt in blood_types:
            update_hospital_inventory(db, hosp_name, hosp_city, bt, 5, password="pass123")
            update_inventory_flag(db, hosp_name, hosp_city, bt, surplus=True, shortage=False, password="pass123")
    
        update_secondary_data(db)
    
        donor = {
            "pid": "P3333333",
            "firstName": "Derek",
            "lastName": "Miller",
            "age": 32,
            "hospital": "Central Medical Center",
            "city": "Boston, MA",
            "donorDetails": {
                "bloodType": "B+",
                "weightLBS": 175,
                "heightIN": 72,
                "gender": "M",
                "nextSafeDonation": datetime(2025, 8, 15)
            }
        }
        add_donor_and_update(db, donor)
    
        remove_donor_and_update(db, "P1111111")
    
        update_hospital_inventory(db, hosp_name, hosp_city, "O+", 2, password="pass123")
    
        result = search_secondary(db, hosp_name, hosp_city)
        print(f"\nSearch result for {hosp_name} in {hosp_city}:")
        print(result)
    
if __name__ == "__main__":
    main()
