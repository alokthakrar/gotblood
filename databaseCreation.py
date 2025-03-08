from pymongo import MongoClient
from datetime import datetime

def setup_primary_database(db):
    """
    Sets up the primary database with sample data.
    Each donor document includes separate 'hospital' and 'city' fields.
    Also sets up sample locations, bloodBags, and globalInventory collections.
    """
    # Clear and insert persons data (donors, patients, nurses)
    db.persons.drop()
    persons_data = [
        {
            "pid": "P1234567",
            "firstName": "John",
            "lastName": "Doe",
            "age": 35,
            "role": "donor",
            "hospital": "General Hospital",
            "city": "Sample City",
            "donorDetails": {
                "bloodType": "O+",
                "weightLBS": 180,
                "heightIN": 70,
                "gender": "M",
                "nextSafeDonation": datetime(2025, 6, 1)
            }
        },
        {
            "pid": "P7654321",
            "firstName": "Jane",
            "lastName": "Smith",
            "age": 28,
            "role": "patient",
            "hospital": "General Hospital",
            "city": "Sample City",
            "patientDetails": {
                "bloodType": "A-",
                "needStatus": "high",
                "weightLBS": 140
            }
        },
        {
            "pid": "P9999999",
            "firstName": "Alice",
            "lastName": "Brown",
            "age": 40,
            "role": "nurse",
            "hospital": "General Hospital",
            "city": "Sample City",
            "nurseDetails": {
                "yearsExperienced": 15
            }
        },
        # Additional donor records
        {
            "pid": "P1111111",
            "firstName": "Bob",
            "lastName": "Taylor",
            "age": 30,
            "role": "donor",
            "hospital": "Community Health Center",
            "city": "Other City",
            "donorDetails": {
                "bloodType": "A+",
                "weightLBS": 170,
                "heightIN": 68,
                "gender": "M",
                "nextSafeDonation": datetime(2025, 7, 1)
            }
        },
        {
            "pid": "P2222222",
            "firstName": "Carol",
            "lastName": "Johnson",
            "age": 45,
            "role": "donor",
            "hospital": "General Hospital",
            "city": "Sample City",
            "donorDetails": {
                "bloodType": "O+",
                "weightLBS": 160,
                "heightIN": 65,
                "gender": "F",
                "nextSafeDonation": datetime(2025, 6, 15)
            }
        }
    ]
    db.persons.insert_many(persons_data)
    
    # Setup locations collection
    db.locations.drop()
    locations_data = [
        {
            "lid": "L0001",
            "name": "General Hospital",
            "city": "Sample City",
            "locationCode": "HOSP"
        },
        {
            "lid": "L0002",
            "name": "Community Health Center",
            "city": "Other City",
            "locationCode": "CHC"
        }
    ]
    db.locations.insert_many(locations_data)
    
    # Setup bloodBags collection (each blood bag has a quantity in CC)
    db.bloodBags.drop()
    blood_bags_data = [
        {
            "bbid": "BB0001",
            "donationType": "Whole Blood",
            "quantityCC": 450,
            "bloodType": "O+",
            "available": True
        },
        {
            "bbid": "BB0002",
            "donationType": "Whole Blood",
            "quantityCC": 300,
            "bloodType": "A+",
            "available": True
        }
    ]
    db.bloodBags.insert_many(blood_bags_data)
    
    # Setup globalInventory collection to map blood bags to locations
    db.globalInventory.drop()
    global_inventory_data = [
        {
            "bbid": "BB0001",
            "lid": "L0001",
            "available": True
        },
        {
            "bbid": "BB0002",
            "lid": "L0002",
            "available": True
        }
    ]
    db.globalInventory.insert_many(global_inventory_data)

def aggregate_donor_data_by_location(db):
    """
    Aggregates donor data from the persons collection.
    Groups donors by 'hospital', 'city', and blood type,
    producing donor counts and default surplus/shortage flags.
    """
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
    """
    Aggregates the blood inventory from the globalInventory collection.
    Joins bloodBags and locations to sum the total quantity (in CC)
    available at each hospital (by hospital name and city).
    """
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
                "city": "$loc.city"
            },
            "totalBloodCC": {"$sum": "$bag.quantityCC"}
        }},
        {"$project": {
            "_id": 0,
            "hospital": "$_id.hospital",
            "city": "$_id.city",
            "totalBloodCC": 1
        }}
    ]
    return list(db.globalInventory.aggregate(pipeline))

def merge_secondary_data(donor_stats, inventory_stats):
    """
    Merges donor statistics and inventory statistics based on hospital and city.
    Returns a list of documents that include donor stats and total blood inventory.
    """
    # Create a lookup dictionary for inventory data keyed by (hospital, city)
    inv_lookup = {(doc["hospital"], doc["city"]): doc["totalBloodCC"] for doc in inventory_stats}
    
    merged = []
    for stat in donor_stats:
        key = (stat["hospital"], stat["city"])
        stat["totalBloodCC"] = inv_lookup.get(key, 0)
        merged.append(stat)
    return merged

def create_secondary_collection(db, merged_data):
    """
    Creates (or updates) the secondary collection 'donorStats'
    with merged donor and inventory statistics.
    """
    db.donorStats.drop()
    db.donorStats.insert_many(merged_data)

def update_secondary_data(db):
    """
    Re-aggregates donor and inventory data, merges the results,
    and updates the secondary collection.
    """
    donor_stats = aggregate_donor_data_by_location(db)
    inventory_stats = aggregate_inventory_by_location(db)
    merged_data = merge_secondary_data(donor_stats, inventory_stats)
    create_secondary_collection(db, merged_data)
    print("Secondary collection 'donorStats' updated.")

# Functions to add and remove donors (with secondary data update)

def add_donor(db, donor_data):
    """
    Adds a donor to the persons collection.
    donor_data must include keys: pid, firstName, lastName, age, hospital, city, and donorDetails.
    """
    donor_data["role"] = "donor"
    result = db.persons.insert_one(donor_data)
    print(f"Donor with pid {donor_data['pid']} added. Inserted ID: {result.inserted_id}")

def remove_donor(db, pid):
    """
    Removes a donor (with role 'donor') from the persons collection by pid.
    """
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

def search_secondary(db, hospital, city):
    """
    Searches the secondary collection 'donorStats' for a given hospital and city.
    Returns the matching document.
    """
    result = db.donorStats.find_one({"hospital": hospital, "city": city})
    return result

def main():
    # Connect to MongoDB (ensure your instance is running)
    client = MongoClient("mongodb://localhost:27017")
    primary_db = client["americanRedCrossDB"]

    # Setup primary database with sample data.
    setup_primary_database(primary_db)
    
    # Initial aggregation to build secondary collection.
    update_secondary_data(primary_db)
    
    # Example: Add a new donor and update secondary data.
    new_donor = {
        "pid": "P3333333",
        "firstName": "Derek",
        "lastName": "Miller",
        "age": 32,
        "hospital": "Community Health Center",
        "city": "Other City",
        "donorDetails": {
            "bloodType": "B+",
            "weightLBS": 175,
            "heightIN": 72,
            "gender": "M",
            "nextSafeDonation": datetime(2025, 8, 15)
        }
    }
    print("\nAdding new donor...")
    add_donor_and_update(primary_db, new_donor)
    
    # Example: Remove an existing donor and update secondary data.
    print("\nRemoving donor with pid P1111111...")
    remove_donor_and_update(primary_db, "P1111111")
    
    # Example: Search secondary data by hospital and city.
    hospital_search = "General Hospital"
    city_search = "Sample City"
    result = search_secondary(primary_db, hospital_search, city_search)
    print(f"\nSearch result for {hospital_search} in {city_search}:")
    print(result)

if __name__ == "__main__":
    main()
