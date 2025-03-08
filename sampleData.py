# sampleData.py
from pymongo import MongoClient
from datetime import datetime, timedelta
import random

# Import the necessary functions from your functions file.
from hospital_managment import update_secondary_data, update_inventory_flag

#have make each hospital have a password thats needed to add, subtract, or update data

def wipe_database(db_name="americanRedCrossDB"):
    client = MongoClient("mongodb://localhost:27017")
    client.drop_database(db_name)
    print(f"Database '{db_name}' has been dropped.")

def generate_sample_hospitals(db):
    """
    Inserts manually defined hospital documents for easier testing.
    Here we create 5 hospitals.
    """
    hospitals = [
        {
            "lid": "L0001",
            "name": "Central Medical Center",
            "city": "Boston, MA",
            "locationCode": "HOSP",
            "coordinates": {"lat": 42.3601, "lon": -71.0589}
        },
        {
            "lid": "L0002",
            "name": "General Hospital 1",
            "city": "Los Angeles, CA",
            "locationCode": "HOSP",
            "coordinates": {"lat": 34.0522, "lon": -118.2437}
        },
        {
            "lid": "L0003",
            "name": "City Hospital 1",
            "city": "New York, NY",
            "locationCode": "HOSP",
            "coordinates": {"lat": 40.7128, "lon": -74.0060}
        },
        {
            "lid": "L0004",
            "name": "Regional Medical Center",
            "city": "Chicago, IL",
            "locationCode": "HOSP",
            "coordinates": {"lat": 41.8781, "lon": -87.6298}
        },
        {
            "lid": "L0005",
            "name": "Health Clinic",
            "city": "Houston, TX",
            "locationCode": "HOSP",
            "coordinates": {"lat": 29.7604, "lon": -95.3698}
        }
    ]
    db.locations.drop()
    db.locations.insert_many(hospitals)
    print(f"Inserted {len(hospitals)} sample hospitals.")

def generate_sample_donors(db):
    """
    Inserts manually defined donor documents.
    """
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
    """
    Inserts inventory records for every hospital and every blood type.
    Each hospital will have one blood bag record per blood type with a fixed quantity (500 CC).
    """
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
                "quantityCC": 500,  # Fixed quantity for testing.
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

def generate_all_sample_data():
    client = MongoClient("mongodb://localhost:27017")
    db = client["americanRedCrossDB"]
    wipe_database("americanRedCrossDB")
    generate_sample_hospitals(db)
    generate_sample_donors(db)
    generate_sample_inventory(db)
    print("All sample data generated.")
    
    # Update the secondary collection so that every hospital has data for every blood type.
    update_secondary_data(db)
    
    # Manually update flags so a match is possible.
    # For example, mark "General Hospital 1" in Los Angeles, CA as having a shortage for A+,
    # and "Central Medical Center" in Boston, MA as having a surplus for A+.
    update_inventory_flag(db, "General Hospital 1", "Los Angeles, CA", "A+", surplus=False, shortage=True)
    update_inventory_flag(db, "Central Medical Center", "Boston, MA", "A+", surplus=True, shortage=False)
    update_inventory_flag(db, "Health Clinic", "Houston, TX", "A+", surplus=True, shortage=False)
    update_inventory_flag(db, "City Hospital 1", "New York, NY", "A+", surplus=True, shortage=False)
    
    # Refresh secondary data after manual flag updates.
    update_secondary_data(db)

if __name__ == "__main__":
    generate_all_sample_data()
