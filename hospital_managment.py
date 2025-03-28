# hospital_managment.py
from pymongo import MongoClient
from datetime import datetime
import math
import random
import bcrypt

#######################################
# Helper functions for password handling
#######################################

def hash_password(plain_password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

#######################################
# Aggregation & Update Functions (Internal)
#######################################

def aggregate_donor_data_by_location(db):
    pipeline = [
        {"$match": {"role": "donor"}},
        {"$group": {
            "_id": {
                "hospital": "$hospital",
                "city": "$city",
                "bloodType": "$donorDetails.bloodType"
            },
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
        {"$lookup": {
            "from": "bloodBags",
            "localField": "bbid",
            "foreignField": "bbid",
            "as": "bag"
        }},
        {"$unwind": "$bag"},
        {"$lookup": {
            "from": "locations",
            "localField": "lid",
            "foreignField": "lid",
            "as": "loc"
        }},
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
        {"$project": {
            "_id": 0,
            "hospital": "$_id.hospital",
            "city": "$_id.city",
            "inventoryStats": 1
        }}
    ]
    return list(db.globalInventory.aggregate(pipeline))

def merge_secondary_data(donor_stats, inventory_stats):
    inv_lookup = {(doc["hospital"], doc["city"]): doc["inventoryStats"] for doc in inventory_stats}
    merged = []
    for stat in donor_stats:
        key = (stat["hospital"], stat["city"])
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
    
    # Complete missing blood types
    complete_blood_types = ["O+", "A+", "B+", "AB+", "O-", "A-", "B-", "AB-"]
    hospitals = list(db.locations.find())
    merged_dict = {(rec["hospital"], rec["city"]): rec for rec in merged_data}
    
    # Preserve existing manual flag updates.
    existing_flags = {}
    for rec in db.donorStats.find():
        key = (rec["hospital"], rec["city"])
        flags = {}
        for bt in rec.get("bloodTypeStats", []):
            flags[bt["bloodType"]] = (bt.get("surplus", False), bt.get("shortage", False))
        existing_flags[key] = flags
    
    for hosp in hospitals:
        key = (hosp["name"], hosp["city"])
        if key not in merged_dict:
            merged_dict[key] = {"hospital": hosp["name"], "city": hosp["city"],
                                "bloodTypeStats": [], "inventoryStats": []}
        record = merged_dict[key]
        # Complete donor stats.
        new_bt_stats = []
        for bt in complete_blood_types:
            computed = next((item for item in record.get("bloodTypeStats", []) if item["bloodType"] == bt), None)
            donorCount = computed["donorCount"] if computed else 0
            flags = existing_flags.get(key, {}).get(bt, (False, False))
            new_bt_stats.append({
                "bloodType": bt,
                "donorCount": donorCount,
                "surplus": flags[0],
                "shortage": flags[1]
            })
        record["bloodTypeStats"] = new_bt_stats
        
        # Complete inventory stats.
        new_inv_stats = []
        for bt in complete_blood_types:
            computed_inv = next((item for item in record.get("inventoryStats", []) if item["bloodType"] == bt), None)
            totalBloodCC = computed_inv["totalBloodCC"] if computed_inv else 0
            new_inv_stats.append({
                "bloodType": bt,
                "totalBloodCC": totalBloodCC
            })
        record["inventoryStats"] = new_inv_stats

    completed_merged_data = list(merged_dict.values())
    create_secondary_collection(db, completed_merged_data)
    print("Secondary collection 'donorStats' updated with complete data.")

#######################################
# Donor and Inventory Management Functions (with authentication)
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
    # Verify password first.
    hosp_doc = db.locations.find_one({"name": hospital, "city": city})
    if not hosp_doc:
        print("Hospital not found!")
        return
    if "passwordHash" not in hosp_doc or not verify_password(password, hosp_doc["passwordHash"]):
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
    # For updating flags, also require a password.
    hosp_doc = db.locations.find_one({"name": hospital, "city": city})
    if not hosp_doc:
        print("Hospital not found!")
        return
    if password is None or "passwordHash" not in hosp_doc or not verify_password(password, hosp_doc["passwordHash"]):
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
    if "password" in hospital_data:
        hospital_data["passwordHash"] = hash_password(hospital_data.pop("password"))
    result = db.locations.insert_one(hospital_data)
    print(f"Hospital '{hospital_data['name']}' added with lid {hospital_data['lid']}.")
    return hospital_data

def search_secondary(db, hospital, city):
    result = db.donorStats.find_one({"hospital": hospital, "city": city})
    return result

#######################################
# Main Function for Hospital Management
#######################################

def main():
    client = MongoClient("mongodb://localhost:27017")
    db = client["americanRedCrossDB"]

    # Update secondary collection based on existing primary data.
    update_secondary_data(db)
    
    # Print all hospitals for reference.
    print("Hospitals in the database:")
    for hosp in db.locations.find():
        print(f"{hosp['name']} - {hosp['city']}")
    
    # Example: Add a new hospital with a password.
    hospital_data = {
        "name": "Central Medical Center",
        "city": "Boston, MA",
        "coordinates": {"lat": 42.3601, "lon": -71.0589},
        "password": "pass123"
    }
    new_hosp = add_hospital(db, hospital_data)
    hosp_name = new_hosp["name"]
    hosp_city = new_hosp["city"]
    
    # For each blood type, add 5 blood bags and set surplus flag to True.
    blood_types = ["O+", "A+", "B+", "AB+", "O-", "A-", "B-", "AB-"]
    for bt in blood_types:
        # Use the hospital's password ("pass123" in this example) for authentication.
        update_hospital_inventory(db, hosp_name, hosp_city, bt, 5, password="pass123")
        update_inventory_flag(db, hosp_name, hosp_city, bt, surplus=True, shortage=False, password="pass123")
    
    update_secondary_data(db)
    
    # Example: Add a donor.
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
    
    # Example: Remove a donor.
    #remove_donor_and_update(db, "P1111111")
    
    # Example: Update hospital inventory (requires password).
    update_hospital_inventory(db, hosp_name, hosp_city, "O+", 2, password="pass123")
    
    # Example: Search for the hospital in the secondary collection.
    result = search_secondary(db, hosp_name, hosp_city)
    print(f"\nSearch result for {hosp_name} in {hosp_city}:")
    print(result)
    
if __name__ == "__main__":
    main()
