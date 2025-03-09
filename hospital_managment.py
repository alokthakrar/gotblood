# hospital_matching.py
from pymongo import MongoClient
import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Computes the Haversine distance (in kilometers) between two latitude/longitude points.
    """
    R = 6371  # Earth's radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# ----- Hospital Matching Functions -----

def match_surplus_for_shortage(db, shortage_hospital, shortage_city, blood_type, max_results=5):
    """
    For a hospital with a shortage of a given blood type, finds up to max_results hospitals
    (other than the shortage hospital) that have a surplus for that blood type.
    Returns a list of dictionaries:
      { "hospital": <name>, "city": <city>, "distance_km": <distance> }
    """
    # Get shortage hospital location.
    sh_loc = db.locations.find_one({"name": shortage_hospital, "city": shortage_city})
    if not sh_loc or "coordinates" not in sh_loc:
        print("Shortage hospital location not found!")
        return []
    sh_lat = sh_loc["coordinates"]["lat"]
    sh_lon = sh_loc["coordinates"]["lon"]

    surplus_records = list(db.donorStats.find({
        "bloodTypeStats": {"$elemMatch": {"bloodType": blood_type, "surplus": True}}
    }))

    matching_hospitals = []
    for record in surplus_records:
        if record["hospital"] == shortage_hospital and record["city"] == shortage_city:
            continue  # skip the same hospital
        sp_loc = db.locations.find_one({"name": record["hospital"], "city": record["city"]})
        if not sp_loc or "coordinates" not in sp_loc:
            continue
        distance = haversine_distance(sh_lat, sh_lon, sp_loc["coordinates"]["lat"], sp_loc["coordinates"]["lon"])
        matching_hospitals.append({
            "hospital": record["hospital"],
            "city": record["city"],
            "distance_km": round(distance, 2)
        })
    matching_hospitals.sort(key=lambda x: x["distance_km"])
    return matching_hospitals[:max_results]

def match_shortage_for_surplus(db, surplus_hospital, surplus_city, blood_type, max_results=5):
    """
    For a hospital with a surplus of a given blood type, finds up to max_results hospitals
    (other than the surplus hospital) that have a shortage for that blood type.
    Returns a list of dictionaries:
      { "hospital": <name>, "city": <city>, "distance_km": <distance> }
    """
    sp_loc = db.locations.find_one({"name": surplus_hospital, "city": surplus_city})
    if not sp_loc or "coordinates" not in sp_loc:
        print("Surplus hospital location not found!")
        return []
    sp_lat = sp_loc["coordinates"]["lat"]
    sp_lon = sp_loc["coordinates"]["lon"]

    shortage_records = list(db.donorStats.find({
        "bloodTypeStats": {"$elemMatch": {"bloodType": blood_type, "shortage": True}}
    }))

    matching_hospitals = []
    for record in shortage_records:
        if record["hospital"] == surplus_hospital and record["city"] == surplus_city:
            continue  # skip same hospital
        sh_loc = db.locations.find_one({"name": record["hospital"], "city": record["city"]})
        if not sh_loc or "coordinates" not in sh_loc:
            continue
        distance = haversine_distance(sp_lat, sp_lon, sh_loc["coordinates"]["lat"], sh_loc["coordinates"]["lon"])
        matching_hospitals.append({
            "hospital": record["hospital"],
            "city": record["city"],
            "distance_km": round(distance, 2)
        })
    matching_hospitals.sort(key=lambda x: x["distance_km"])
    return matching_hospitals[:max_results]

# ----- Donor Matching Functions -----

def match_donors_for_shortage(db, shortage_hospital, shortage_city, blood_type, max_results=5):
    """
    For a hospital with a shortage of donors for a given blood type, find donors (from other hospitals)
    with that blood type sorted by distance from the shortage hospital.
    
    Returns a list of donor info dictionaries:
      { "pid": <donor id>, "firstName": <first>, "lastName": <last>, "hospital": <hospital>, "city": <city>, "distance_km": <distance> }
    """
    # Get shortage hospital location.
    sh_loc = db.locations.find_one({"name": shortage_hospital, "city": shortage_city})
    if not sh_loc or "coordinates" not in sh_loc:
        print("Shortage hospital location not found!")
        return []
    sh_lat = sh_loc["coordinates"]["lat"]
    sh_lon = sh_loc["coordinates"]["lon"]

    # Query donors with the specified blood type.
    donors = list(db.persons.find({"role": "donor", "donorDetails.bloodType": blood_type}))
    matched_donors = []
    for donor in donors:
        # Exclude donors from the shortage hospital (optional).
        if donor.get("hospital") == shortage_hospital and donor.get("city") == shortage_city:
            continue
        donor_loc = db.locations.find_one({"name": donor.get("hospital"), "city": donor.get("city")})
        if not donor_loc or "coordinates" not in donor_loc:
            continue
        distance = haversine_distance(sh_lat, sh_lon, donor_loc["coordinates"]["lat"], donor_loc["coordinates"]["lon"])
        matched_donors.append({
            "pid": donor.get("pid"),
            "firstName": donor.get("firstName"),
            "lastName": donor.get("lastName"),
            "hospital": donor.get("hospital"),
            "city": donor.get("city"),
            "distance_km": round(distance, 2)
        })
    matched_donors.sort(key=lambda x: x["distance_km"])
    return matched_donors[:max_results]

def match_donors_for_surplus(db, surplus_hospital, surplus_city, blood_type, max_results=5):
    """
    For a hospital with a surplus (or simply for matching purposes), find donors (from other hospitals)
    with the specified blood type sorted by distance from the surplus hospital.
    
    Returns a list of donor info dictionaries:
      { "pid": <donor id>, "firstName": <first>, "lastName": <last>, "hospital": <hospital>, "city": <city>, "distance_km": <distance> }
    """
    sp_loc = db.locations.find_one({"name": surplus_hospital, "city": surplus_city})
    if not sp_loc or "coordinates" not in sp_loc:
        print("Surplus hospital location not found!")
        return []
    sp_lat = sp_loc["coordinates"]["lat"]
    sp_lon = sp_loc["coordinates"]["lon"]

    donors = list(db.persons.find({"role": "donor", "donorDetails.bloodType": blood_type}))
    matched_donors = []
    for donor in donors:
        # Exclude donors from the surplus hospital.
        if donor.get("hospital") == surplus_hospital and donor.get("city") == surplus_city:
            continue
        donor_loc = db.locations.find_one({"name": donor.get("hospital"), "city": donor.get("city")})
        if not donor_loc or "coordinates" not in donor_loc:
            continue
        distance = haversine_distance(sp_lat, sp_lon, donor_loc["coordinates"]["lat"], donor_loc["coordinates"]["lon"])
        matched_donors.append({
            "pid": donor.get("pid"),
            "firstName": donor.get("firstName"),
            "lastName": donor.get("lastName"),
            "hospital": donor.get("hospital"),
            "city": donor.get("city"),
            "distance_km": round(distance, 2)
        })
    matched_donors.sort(key=lambda x: x["distance_km"])
    return matched_donors[:max_results]

def main():
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017")
    db = client["americanRedCrossDB"]

    blood_type = "A+"
    
    print("----- Matching surplus hospitals for a shortage -----")
    shortage_hospital = "General Hospital 1"
    shortage_city = "Los Angeles, CA"
    surplus_matches = match_surplus_for_shortage(db, shortage_hospital, shortage_city, blood_type, max_results=5)
    print("Shortage Hospital:", {"hospital": shortage_hospital, "city": shortage_city})
    for m in surplus_matches:
        print(m)
    
    print("\n----- Matching shortage hospitals for a surplus -----")
    surplus_hospital = "Central Medical Center"
    surplus_city = "Boston, MA"
    shortage_matches = match_shortage_for_surplus(db, surplus_hospital, surplus_city, blood_type, max_results=5)
    print("Surplus Hospital:", {"hospital": surplus_hospital, "city": surplus_city})
    for m in shortage_matches:
        print(m)
    
    print("\n----- Matching donors for a shortage -----")
    donor_matches_shortage = match_donors_for_shortage(db, shortage_hospital, shortage_city, blood_type, max_results=5)
    for d in donor_matches_shortage:
        print(d)
    
    print("\n----- Matching donors for a surplus -----")
    donor_matches_surplus = match_donors_for_surplus(db, surplus_hospital, surplus_city, blood_type, max_results=5)
    for d in donor_matches_surplus:
        print(d)

if __name__ == "__main__":
    main()
