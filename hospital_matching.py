from pymongo import MongoClient
import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Computes the Haversine distance between two latitude/longitude points in kilometers.
    """
    R = 6371  # Earth's radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def match_hospital_with_shortage_to_surplus(db, shortage_hospital_name, shortage_city, blood_type, max_results=5):
    """
    For a hospital with a shortage of a specific blood type, this function:
    
    1. Retrieves the shortage hospital's aggregated record from the secondary collection (donorStats)
       and verifies that it has a shortage flag set to True for the given blood type.
    2. Retrieves the shortage hospital's location data to obtain its coordinates.
    3. Searches the secondary collection for hospitals (other than the shortage hospital)
       that have the given blood type flagged with surplus=True.
    4. Calculates the distance (using haversine_distance) between the shortage hospital and each candidate.
    5. Returns the top 5 closest matching hospitals.
    
    Returns a list of dictionaries in the format:
      { "hospital": <name>, "city": <city>, "distance_km": <distance>, "donorCount": <donorCount> }
    """
    # Retrieve the shortage hospital's aggregated record.
    shortage_record = db.donorStats.find_one({"hospital": shortage_hospital_name, "city": shortage_city})
    if not shortage_record:
        print("Shortage hospital record not found in secondary collection!")
        return []
    
    # Verify the shortage flag is True for the specified blood type.
    shortage_flag = False
    for bt_stat in shortage_record.get("bloodTypeStats", []):
        if bt_stat["bloodType"] == blood_type and bt_stat.get("shortage") == True:
            shortage_flag = True
            break
    if not shortage_flag:
        print(f"Hospital {shortage_hospital_name} in {shortage_city} does not have a shortage for {blood_type}.")
        return []
    
    # Retrieve shortage hospital's coordinates.
    shortage_hosp = db.locations.find_one({"name": shortage_hospital_name, "city": shortage_city})
    if not shortage_hosp or "coordinates" not in shortage_hosp:
        print("Shortage hospital not found or missing coordinates in locations!")
        return []
    sh_coords = shortage_hosp["coordinates"]
    
    # Query the secondary collection for hospitals with surplus for the specified blood type.
    potential_matches = list(db.donorStats.find({
        "bloodTypeStats": {"$elemMatch": {"bloodType": blood_type, "surplus": True}}
    }))
    
    matching_hospitals = []
    for record in potential_matches:
        # Exclude the shortage hospital itself.
        if record["hospital"] == shortage_hospital_name and record["city"] == shortage_city:
            continue
        # Retrieve candidate hospital's location.
        hosp_doc = db.locations.find_one({"name": record["hospital"], "city": record["city"]})
        if not hosp_doc or "coordinates" not in hosp_doc:
            continue
        hosp_coords = hosp_doc["coordinates"]
        distance = haversine_distance(sh_coords["lat"], sh_coords["lon"],
                                      hosp_coords["lat"], hosp_coords["lon"])
        # Retrieve donor count for the specified blood type.
        donor_count = 0
        for bt_stat in record.get("bloodTypeStats", []):
            if bt_stat["bloodType"] == blood_type:
                donor_count = bt_stat.get("donorCount", 0)
                break
        matching_hospitals.append({
            "hospital": record["hospital"],
            "city": record["city"],
            "distance_km": distance,
            "donorCount": donor_count
        })
    
    # Sort candidates by distance and return the top 5.
    matching_hospitals = sorted(matching_hospitals, key=lambda x: x["distance_km"])
    return matching_hospitals[:max_results]

def main():
    client = MongoClient("mongodb://localhost:27017")
    db = client["americanRedCrossDB"]
    
    # Example usage:
    shortage_hospital_name = "General Hospital 1"
    shortage_city = "Los Angeles, CA"
    blood_type = "A+"
    
    #return top 5 closest matchest with their data in an endpoint
    matches = match_hospital_with_shortage_to_surplus(db, shortage_hospital_name, shortage_city, blood_type, max_results=5)
    print(f"Top matching hospitals for {shortage_hospital_name} in {shortage_city} needing {blood_type}:")
    for match in matches:
        print(match)

if __name__ == "__main__":
    main()
