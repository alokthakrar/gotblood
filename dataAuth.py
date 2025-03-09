# sampleData.py
from pymongo import MongoClient
from datetime import datetime
client = MongoClient("mongodb://localhost:27017")
db = client["americanRedCrossDB"]

def generate_sample_hospitals(db):
    """
    Inserts 5 manually defined hospitals with plain text passwords,
    and registers them with Auth0 using the hospital name as username.
    """
    hospitals = [
        {"name": "Central Medical Center", "city": "Boston, MA", "coordinates": {"lat": 42.3601, "lon": -71.0589}, "password": "pass123"},
        {"name": "General Hospital 1", "city": "Los Angeles, CA", "coordinates": {"lat": 34.0522, "lon": -118.2437}, "password": "securePass"},
        {"name": "City Hospital 1", "city": "New York, NY", "coordinates": {"lat": 40.7128, "lon": -74.0060}, "password": "hospitalNY"},
        {"name": "Regional Medical Center", "city": "Chicago, IL", "coordinates": {"lat": 41.8781, "lon": -87.6298}, "password": "chicagoPass"},
        {"name": "Health Clinic", "city": "Houston, TX", "coordinates": {"lat": 29.7604, "lon": -95.3698}, "password": "houstonClinic"}
    ]
    db.locations.drop()
    for i, hosp in enumerate(hospitals, start=1):
        hosp["lid"] = "L{:04d}".format(i)
        from managmentAuth import register_auth0_user
        register_auth0_user(hosp["name"], hosp["password"])
    db.locations.insert_many(hospitals)
    print(f"Inserted {len(hospitals)} sample hospitals.")

def generate_sample_donors(db):
    donors = [
        {
            "pid": "P0000001",
            "firstName": "Alice",
            "lastName": "Smith",
            "age": 30,
            "role": "donor",
            "hospital": "Central Medical Center",
            "city": "Boston, MA",
            "donorDetails": {
                "bloodType": "A+",
                "weightLBS": 150,
                "heightIN": 65,
                "gender": "F",
                "nextSafeDonation": datetime(2025, 8, 1)
            }
        },
        {
            "pid": "P0000002",
            "firstName": "Bob",
            "lastName": "Jones",
            "age": 40,
            "role": "donor",
            "hospital": "Central Medical Center",
            "city": "Boston, MA",
            "donorDetails": {
                "bloodType": "O+",
                "weightLBS": 180,
                "heightIN": 70,
                "gender": "M",
                "nextSafeDonation": datetime(2025, 9, 1)
            }
        },
        {
            "pid": "P0000003",
            "firstName": "Charlie",
            "lastName": "Brown",
            "age": 35,
            "role": "donor",
            "hospital": "General Hospital 1",
            "city": "Los Angeles, CA",
            "donorDetails": {
                "bloodType": "B+",
                "weightLBS": 175,
                "heightIN": 68,
                "gender": "M",
                "nextSafeDonation": datetime(2025, 10, 1)
            }
        },
        {
            "pid": "P0000004",
            "firstName": "Diana",
            "lastName": "Prince",
            "age": 28,
            "role": "donor",
            "hospital": "City Hospital 1",
            "city": "New York, NY",
            "donorDetails": {
                "bloodType": "AB-",
                "weightLBS": 135,
                "heightIN": 64,
                "gender": "F",
                "nextSafeDonation": datetime(2025, 11, 1)
            }
        },
        {
            "pid": "P0000005",
            "firstName": "Edward",
            "lastName": "Norton",
            "age": 50,
            "role": "donor",
            "hospital": "Regional Medical Center",
            "city": "Chicago, IL",
            "donorDetails": {
                "bloodType": "O-",
                "weightLBS": 200,
                "heightIN": 72,
                "gender": "M",
                "nextSafeDonation": datetime(2025, 12, 1)
            }
        },
        {
            "pid": "P0000006",
            "firstName": "Fiona",
            "lastName": "Apple",
            "age": 33,
            "role": "donor",
            "hospital": "Health Clinic",
            "city": "Houston, TX",
            "donorDetails": {
                "bloodType": "AB+",
                "weightLBS": 140,
                "heightIN": 63,
                "gender": "F",
                "nextSafeDonation": datetime(2025, 7, 1)
            }
        }
    ]
    db.persons.drop()
    db.persons.insert_many(donors)
    print(f"Inserted {len(donors)} sample donors.")

def generate_sample_inventory(db):
    blood_types = ["O+", "A+", "B+", "AB+", "O-", "A-", "B-", "AB-"]
    db.bloodBags.drop()
    db.globalInventory.drop()
    
    hospitals = list(db.locations.find())
    blood_bags = []
    inventory = []
    bbid_counter = 1
    
    for hosp in hospitals:
        for bt in blood_types:
            bbid = "BB{:04d}".format(bbid_counter)
            bbid_counter += 1
            bag = {
                "bbid": bbid,
                "donationType": "Whole Blood",
                "quantityCC": 500,
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

def set_manual_flags(db):
    from managmentAuth import update_inventory_flag
    update_inventory_flag(db, "General Hospital 1", "Los Angeles, CA", "A+", surplus=False, shortage=True, password="securePass")
    update_inventory_flag(db, "Central Medical Center", "Boston, MA", "A+", surplus=True, shortage=False, password="pass123")
    update_inventory_flag(db, "City Hospital 1", "New York, NY", "A+", surplus=True, shortage=False, password="hospitalNY")
    update_inventory_flag(db, "Health Clinic", "Houston, TX", "A+", surplus=True, shortage=False, password="houstonClinic")
    print("Manually set surplus/shortage flags for testing matching.")

def generate_all_sample_data():
    from managmentAuth import update_secondary_data, update_hospital_inventory
    client = MongoClient("mongodb://localhost:27017")
    db = client["americanRedCrossDB"]
    wipe_database("americanRedCrossDB")
    generate_sample_hospitals(db)
    generate_sample_donors(db)
    generate_sample_inventory(db)
    print("All sample data generated.")
    
    update_secondary_data(db)
    set_manual_flags(db)
    
    # For demonstration, add extra inventory for "Central Medical Center" for A+.
    update_hospital_inventory(db, "Central Medical Center", "Boston, MA", "A+", 5, password="pass123")
    
    update_secondary_data(db)
    print("Final sample data generation complete.")

def wipe_database(db_name="americanRedCrossDB"):
    client = MongoClient("mongodb://localhost:27017")
    client.drop_database(db_name)
    print(f"Database '{db_name}' has been wiped.")

if __name__ == "__main__":
    generate_all_sample_data()
