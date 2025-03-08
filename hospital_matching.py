# hospital_matching_no_location.py
from pymongo import MongoClient

def match_hospital_with_shortage_to_surplus_no_location(db, shortage_hospital_name, shortage_city, blood_type, max_results=5):
    """
    For a hospital with a shortage of a specific blood type, this function:
    
    1. Retrieves the shortage hospital's aggregated record from the secondary collection (donorStats)
       and verifies that it has a shortage flag set to True for the given blood type.
    2. Searches the secondary collection for hospitals (other than the shortage hospital) that have the given
       blood type flagged with surplus=True.
    3. Returns up to max_results matching hospitals.
    
    Returns a list of dictionaries in the format:
      { "hospital": <name>, "city": <city>, "donorCount": <donorCount> }
    """
    # Retrieve shortage hospital's aggregated record.
    shortage_record = db.donorStats.find_one({"hospital": shortage_hospital_name, "city": shortage_city})
    if not shortage_record:
        print("Shortage hospital record not found in secondary collection!")
        return []
    
    # Verify that the shortage hospital has a shortage flag for the given blood type.
    shortage_flag = False
    for bt_stat in shortage_record.get("bloodTypeStats", []):
        if bt_stat["bloodType"] == blood_type and bt_stat.get("shortage") == True:
            shortage_flag = True
            break
    if not shortage_flag:
        print(f"Hospital {shortage_hospital_name} in {shortage_city} does not have a shortage for {blood_type}.")
        return []
    
    # Query the secondary collection for hospitals with surplus for the specified blood type.
    potential_matches = list(db.donorStats.find({
        "bloodTypeStats": {"$elemMatch": {"bloodType": blood_type, "surplus": True}}
    }))
    
    matching_hospitals = []
    for record in potential_matches:
        # Exclude the shortage hospital itself.
        if record["hospital"] == shortage_hospital_name and record["city"] == shortage_city:
            continue
        # Retrieve the donor count for the specified blood type.
        donor_count = 0
        for bt_stat in record.get("bloodTypeStats", []):
            if bt_stat["bloodType"] == blood_type:
                donor_count = bt_stat.get("donorCount", 0)
                break
        matching_hospitals.append({
            "hospital": record["hospital"],
            "city": record["city"],
            "donorCount": donor_count
        })
    
    # For this version, we do not sort by distance; we simply return up to max_results.
    return matching_hospitals[:max_results]

def main():
    client = MongoClient("mongodb://localhost:27017")
    db = client["americanRedCrossDB"]
    
    # Example usage:
    shortage_hospital_name = "General Hospital 1"
    shortage_city = "Los Angeles, CA"
    blood_type = "A+"
    
    matches = match_hospital_with_shortage_to_surplus_no_location(db, shortage_hospital_name, shortage_city, blood_type, max_results=5)
    print(f"Matching hospitals for {shortage_hospital_name} in {shortage_city} needing {blood_type}:")
    for match in matches:
        print(match)

if __name__ == "__main__":
    main()
