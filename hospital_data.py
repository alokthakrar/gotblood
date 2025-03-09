# hospital_data.py
from pymongo import MongoClient

def get_complete_hospital_data_with_location(db):
    """
    Retrieves aggregated data from the secondary collection 'donorStats'
    and ensures each hospital's data includes all eight blood types.
    Additionally, it looks up the hospital's coordinates from the locations collection.
    Returns a list of dictionaries with:
      {
        "hospital": <name>,
        "city": <city>,
        "coordinates": {"lat": <lat>, "lon": <lon>},
        "bloodData": [
             { "bloodType": ..., "totalBloodCC": ..., "surplus": ..., "shortage": ... },
             ...
        ]
      }
    """
    complete_blood_types = ["O+", "A+", "B+", "AB+", "O-", "A-", "B-", "AB-"]
    records = list(db.donorStats.find())
    results = []
    
    for rec in records:
        hospital_name = rec.get("hospital")
        city = rec.get("city")
        # Retrieve hospital's coordinates from the locations collection.
        loc = db.locations.find_one({"name": hospital_name, "city": city})
        coordinates = loc.get("coordinates") if loc and "coordinates" in loc else {}
        
        inv_lookup = {inv.get("bloodType"): inv.get("totalBloodCC", 0)
                      for inv in rec.get("inventoryStats", [])}
        flag_lookup = {bt.get("bloodType"): {"surplus": bt.get("surplus", False),
                                             "shortage": bt.get("shortage", False)}
                       for bt in rec.get("bloodTypeStats", [])}
        
        blood_data = []
        for bt in complete_blood_types:
            blood_data.append({
                "bloodType": bt,
                "totalBloodCC": inv_lookup.get(bt, 0),
                "surplus": flag_lookup.get(bt, {}).get("surplus", False),
                "shortage": flag_lookup.get(bt, {}).get("shortage", False)
            })
        
        results.append({
            "hospital": hospital_name,
            "city": city,
            "coordinates": coordinates,
            "bloodData": blood_data
        })
    return results

def get_complete_hospital_data(db):
    """
    Retrieves aggregated data from the secondary collection 'donorStats' and
    ensures that each hospital's data includes all eight blood types.
    
    Returns a list of dictionaries with the following format:
      {
         "hospital": <hospitalName>,
         "city": <city>,
         "bloodData": [
              {"bloodType": <bloodType>, "totalBloodCC": <amount>, "surplus": <bool>, "shortage": <bool>},
              ...
         ]
      }
    If a blood type is missing, it defaults to amount 0 and flags False.
    """
    complete_blood_types = ["O+", "A+", "B+", "AB+", "O-", "A-", "B-", "AB-"]
    # Retrieve all aggregated records from donorStats.
    records = list(db.donorStats.find())
    results = []
    
    for rec in records:
        hospital_name = rec.get("hospital")
        city = rec.get("city")
        
        # Build lookups for inventory amounts and flag settings.
        inv_lookup = {inv.get("bloodType"): inv.get("totalBloodCC", 0)
                      for inv in rec.get("inventoryStats", [])}
        flag_lookup = {bt.get("bloodType"): {"surplus": bt.get("surplus", False),
                                             "shortage": bt.get("shortage", False)}
                       for bt in rec.get("bloodTypeStats", [])}
        
        # Create a complete list for every blood type.
        blood_data = []
        for bt in complete_blood_types:
            blood_data.append({
                "bloodType": bt,
                "totalBloodCC": inv_lookup.get(bt, 0),
                "surplus": flag_lookup.get(bt, {}).get("surplus", False),
                "shortage": flag_lookup.get(bt, {}).get("shortage", False)
            })
        
        results.append({
            "hospital": hospital_name,
            "city": city,
            "bloodData": blood_data
        })
    return results

def main():
    client = MongoClient("mongodb://localhost:27017")
    db = client["americanRedCrossDB"]
    
    hospital_data = get_complete_hospital_data(db)
    for hosp in hospital_data:
        print(f"Hospital: {hosp['hospital']}, City: {hosp['city']}")
        for bt in hosp["bloodData"]:
            print(f"  Blood Type: {bt['bloodType']}, Amount: {bt['totalBloodCC']} CC, "
                  f"Surplus: {bt['surplus']}, Shortage: {bt['shortage']}")
        print("-----")

if __name__ == "__main__":
    main()
