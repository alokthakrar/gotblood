# donors_db.py
from pymongo import MongoClient
from datetime import datetime

def get_db(db_name="bloodDonationDB"):
    """Connects to MongoDB and returns the specified database."""
    client = MongoClient("mongodb://localhost:27017")
    return client[db_name]

def wipe_database(db_name="bloodDonationDB"):
    """Drops the specified database."""
    client = MongoClient("mongodb://localhost:27017")
    client.drop_database(db_name)
    print(f"Database '{db_name}' has been wiped.")

def create_donors_collection(db):
    """
    Ensures that the 'donors' collection exists and creates a unique index on donor_id.
    Returns the collection.
    """
    collection = db.donors
    collection.create_index("donor_id", unique=True)
    return collection

def add_donor(collection, donor_data):
    """
    Inserts a new donor into the donors collection.
    
    Expected donor_data fields:
      - donor_id: A unique identifier for the donor (e.g., "D0000001").
      - first_name: Donor's first name.
      - last_name: Donor's last name.
      - age: Donor's age.
      - blood_type: Donor's blood type (e.g., "O+", "A-", etc.).
      - location: A dictionary with at least:
            - city: e.g., "New York"
            - state: e.g., "NY"
            - coordinates: a dict with "lat" and "lon", e.g. {"lat": 40.7128, "lon": -74.0060}
      - contact_info: (Optional) A dictionary with "email", "phone", etc.
      - registration_date: (Optional) Defaults to current UTC time.
    
    Returns the inserted document's ID.
    """
    if "registration_date" not in donor_data:
        donor_data["registration_date"] = datetime.utcnow()
    result = collection.insert_one(donor_data)
    return result.inserted_id

def get_donors_by_city_and_blood(collection, city, blood_type):
    """
    Retrieves donors from the collection that are located in the specified city
    and have the specified blood type.
    
    Parameters:
      - collection: The MongoDB donors collection.
      - city: The city to filter on (e.g., "New York").
      - blood_type: The blood type to filter on (e.g., "O+").
    
    Returns:
      A list of donor documents.
    """
    query = {
        "location.city": city,
        "blood_type": blood_type
    }
    donors = list(collection.find(query))
    return donors

def initialize_donor():
    """
    Returns a sample donor document.
    """
    donor = {
         "donor_id": "D0000001",
         "first_name": "John",
         "last_name": "Doe",
         "age": 30,
         "blood_type": "O+",
         "location": {
             "city": "New York",
             "state": "NY",
             "coordinates": {"lat": 40.7128, "lon": -74.0060}
         },
         "contact_info": {
             "email": "johndoe@example.com",
             "phone": "123-456-7890"
         }
    }
    return donor

def main():
    # Wipe the database every time the script runs.
    wipe_database("bloodDonationDB")
    
    db = get_db("bloodDonationDB")
    donors_col = create_donors_collection(db)
    
    # Insert a sample donor.
    sample_donor = initialize_donor()
    inserted_id = add_donor(donors_col, sample_donor)
    print("Inserted donor with id:", inserted_id)
    
    # Retrieve and print donors in New York with blood type "O+".
    matching_donors = get_donors_by_city_and_blood(donors_col, "New York", "O+")
    print("Donors in New York with blood type O+:")
    for donor in matching_donors:
        print(donor)

if __name__ == "__main__":
    main()
