from pymongo import MongoClient
from datetime import datetime

def setup_primary_database(db):
    # Insert sample data into the persons collection.
    # Each donor now includes a "location" field (hospital name).
    persons_data = [
        {
            "pid": "P1234567",
            "firstName": "John",
            "lastName": "Doe",
            "age": 35,
            "role": "donor",
            "location": "General Hospital",
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
            "location": "General Hospital",
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
            "location": "General Hospital",
            "nurseDetails": {
                "yearsExperienced": 15
            }
        },
        # Additional donor records for aggregation demonstration.
        {
            "pid": "P1111111",
            "firstName": "Bob",
            "lastName": "Taylor",
            "age": 30,
            "role": "donor",
            "location": "Community Health Center",
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
            "location": "General Hospital",
            "donorDetails": {
                "bloodType": "O+",
                "weightLBS": 160,
                "heightIN": 65,
                "gender": "F",
                "nextSafeDonation": datetime(2025, 6, 15)
            }
        }
    ]
    db.persons.drop()  # Clear existing data for a fresh start
    db.persons.insert_many(persons_data)
    
    # Insert sample data into the donationTypes collection.
    donation_types_data = [
        {"_id": "Whole Blood", "frequencyDays": 56},
        {"_id": "Plasma", "frequencyDays": 28},
        {"_id": "Platelets", "frequencyDays": 7}
    ]
    db.donationTypes.drop()
    db.donationTypes.insert_many(donation_types_data)
    
    # Insert a sample donation document.
    donation_data = {
        "donationId": "D0001",
        "donorId": "P1234567",  # Reference to a donor in persons
        "nurseId": "P9999999",  # Reference to a nurse in persons
        "donationDate": datetime(2025, 3, 1),
        "preExam": {
            "hemoglobin": 13.5,
            "temperature": 98.6,
            "bloodPressure": "120/80",
            "pulseRate": 70
        },
        "amountDonatedCC": 450,
        "donationType": "Whole Blood"
    }
    db.donations.drop()
    db.donations.insert_one(donation_data)
    
    # Insert a sample bloodBags document.
    blood_bags_data = {
        "bbid": "BB0001",
        "donationType": "Whole Blood",
        "quantityCC": 450,
        "bloodType": "O+",
        "available": True
    }
    db.bloodBags.drop()
    db.bloodBags.insert_one(blood_bags_data)
    
    # Insert sample location documents.
    # One for General Hospital and one for Community Health Center.
    location_data = [
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
    db.locations.drop()
    db.locations.insert_many(location_data)
    
    # Insert a sample globalInventory document.
    global_inventory_data = {
        "bbid": "BB0001",  # Reference to a blood bag in bloodBags
        "lid": "L0001",    # Reference to a location in locations
        "available": True
    }
    db.globalInventory.drop()
    db.globalInventory.insert_one(global_inventory_data)
    
    # Insert a sample request document.
    request_data = {
        "rqid": "RQ0001",
        "lid": "L0001",
        "bloodTypeRequested": "O+",
        "dateRequested": datetime(2025, 3, 5),
        "quantityRequestedPints": 2
    }
    db.requests.drop()
    db.requests.insert_one(request_data)

def aggregate_donor_data_by_location(db):
    # Aggregation pipeline to group donors by location and blood type,
    # then lookup additional details (city and hospital name) from the locations collection.
    pipeline = [
        {"$match": {"role": "donor"}},
        {"$group": {
            "_id": {
                "location": "$location",
                "bloodType": "$donorDetails.bloodType"
            },
            "donorCount": {"$sum": 1}
        }},
        {"$group": {
            "_id": "$_id.location",
            "bloodTypeStats": {
                "$push": {
                    "bloodType": "$_id.bloodType",
                    "donorCount": "$donorCount",
                    "surplus": False,
                    "shortage": False
                }
            }
        }},
        {"$project": {
            "_id": 0,
            "location": "$_id",
            "bloodTypeStats": 1
        }},
        # Lookup location details from the locations collection.
        {"$lookup": {
             "from": "locations",
             "localField": "location",
             "foreignField": "name",
             "as": "locationInfo"
        }},
        {"$unwind": "$locationInfo"},
        {"$project": {
             "location": 1,
             "hospital": "$locationInfo.name",
             "city": "$locationInfo.city",
             "bloodTypeStats": 1
        }}
    ]
    return list(db.persons.aggregate(pipeline))

def create_secondary_collection(db, aggregated_data):'
    db.donorStats.drop() 
    db.donorStats.insert_many(aggregated_data)

def main():
    client = MongoClient("mongodb://localhost:27017")
    
    primary_db = client["americanRedCrossDB"]

    setup_primary_database(primary_db)
    
    aggregated_data = aggregate_donor_data_by_location(primary_db)
    print("Aggregated Donor Data by Location (with City and Hospital):")
    for doc in aggregated_data:
        print(doc)
    
    #Secondary database ie the stuff thats used by us the other stuff that we get from the hospital need to be black boxed and encypted
    donor_stats_db = client["donorStatsDB"]
    donor_stats_db.donorInventory.drop()
    donor_stats_db.donorInventory.insert_many(aggregated_data)
    print("\nSecondary database 'donorStatsDB' with collection 'donorInventory' created.")

if __name__ == "__main__":
    main()
