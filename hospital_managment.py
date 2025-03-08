# hospital_management.py
from pymongo import MongoClient
from datetime import datetime
import math
import random

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
            "_id": {
                "hospital": "$_id.hospital",
                "city": "$_id.city"
            },
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
            "_id": {
                "hospital": "$loc.name",
                "city": "$loc.city",
                "bloodType": "$bag.bloodType"
            },
            "totalBloodCC": {"$sum": "$bag.quantityCC"}
        }},
        {"$group": {
            "_id": {
                "hospital": "$_id.hospital",
                "city": "$_id.city"
            },
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
    # First, perform the normal aggregation
    donor_stats = aggregate_donor_data_by_location(db)
    inventory_stats = aggregate_inventory_by_location(db)
    merged_data = merge_secondary_data(donor_stats, inventory_stats)
    
    # Complete missing blood type data for every hospital.
    complete_blood_types = ["O+", "A+", "B+", "AB+", "O-", "A-", "B-", "AB-"]
    # Get all hospitals from the locations collection
    hospitals = list(db.locations.find())
    # Create a dictionary of merged data keyed by (hospital, city)
    merged_dict = {(record["hospital"], record["city"]): record for record in merged_data}
    
    # Ensure every hospital has a record and complete missing blood types.
    for hosp in hospitals:
        key = (hosp["name"], hosp["city"])
        if key not in merged_dict:
            merged_dict[key] = {
                "hospital": hosp["name"],
                "city": hosp["city"],
                "bloodTypeStats": [],
                "inventoryStats": []
            }
        record = merged_dict[key]
        # Complete donor stats
        existing_bt_stats = {bt["bloodType"]: bt for bt in record.get("bloodTypeStats", [])}
        completed_bt_stats = []
        for bt in complete_blood_types:
            if bt in existing_bt_stats:
                completed_bt_stats.append(existing_bt_stats[bt])
            else:
                completed_bt_stats.append({"bloodType": bt, "donorCount": 0, "surplus": False, "shortage": False})
        record["bloodTypeStats"] = completed_bt_stats
        
        # Complete inventory stats
        existing_inv_stats = {inv["bloodType"]: inv for inv in record.get("inventoryStats", [])}
        completed_inv_stats = []
        for bt in complete_blood_types:
            if bt in existing_inv_stats:
                completed_inv_stats.append(existing_inv_stats[bt])
            else:
                completed_inv_stats.append({"bloodType": bt, "totalBloodCC": 0})
        record["inventoryStats"] = completed_inv_stats
    
    completed_merged_data = list(merged_dict.values())
    create_secondary_collection(db, completed_merged_data)
    print("Secondary collection 'donorStats' updated with complete data for all blood types.")

#######################################
# Donor and Inventory Management Functions
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

def update_hospital_inventory(db, hospital, city, bloodType, delta_count):
    location = db.locations.find_one({"name": hospital, "city": city})
    if not location:
        print("Location not found!")
        return
    lid = location["lid"]
    
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
            {"$lookup": {
                "from": "bloodBags",
                "localField": "bbid",
                "foreignField": "bbid",
                "as": "bag"
            }},
            {"$unwind": "$bag"},
            {"$match": {
                "lid": lid,
                "available": True,
                "bag.bloodType": bloodType
            }}
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
        {"$match": {
            "loc.name": hospital,
            "loc.city": city,
            "available": True
        }},
        {"$group": {
            "_id": "$bag.bloodType",
            "totalBloodCC": {"$sum": "$bag.quantityCC"}
        }},
        {"$project": {
            "_id": 0,
            "bloodType": "$_id",
            "totalBloodCC": 1
        }}
    ]
    current_inventory = list(db.globalInventory.aggregate(pipeline_inventory))
    print("Current Inventory by Blood Type:")
    for inv in current_inventory:
        print(inv)

def update_inventory_flag(db, hospital, city, blood_type, surplus=None, shortage=None):
    update_fields = {}
    if surplus is not None:
        update_fields["bloodTypeStats.$.surplus"] = surplus
    if shortage is not None:
        update_fields["bloodTypeStats.$.shortage"] = shortage
    if update_fields:
        result = db.donorStats.update_one(
            {"hospital": hospital, "city": city, "bloodTypeStats.bloodType": blood_type},
            {"$set": update_fields}
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
    
    # Example: Add a new hospital.
    hospital_data = {
        "name": "Central Medical Center",
        "city": "Boston, MA",
        "coordinates": {"lat": 42.3601, "lon": -71.0589}
    }
    new_hosp = add_hospital(db, hospital_data)
    hosp_name = new_hosp["name"]
    hosp_city = new_hosp["city"]
    
    # For each blood type, add 5 blood bags and set the surplus flag to True.
    blood_types = ["O+", "A+", "B+", "AB+", "O-", "A-", "B-", "AB-"]
    for bt in blood_types:
        update_hospital_inventory(db, hosp_name, hosp_city, bt, 5)
        update_inventory_flag(db, hosp_name, hosp_city, bt, surplus=True, shortage=False)
    
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
    remove_donor_and_update(db, "P1111111")
    
    # Example: Update hospital inventory.
    update_hospital_inventory(db, hosp_name, hosp_city, "O+", 2)
    
    # Example: Search for the new hospital in the secondary collection.
    result = search_secondary(db, hosp_name, hosp_city)
    print(f"\nSearch result for {hosp_name} in {hosp_city}:")
    print(result)
    
if __name__ == "__main__":
    main()
