# hospitalData.py
from pymongo import MongoClient

def get_complete_hospital_data(db):
    """
    Retrieves aggregated data from the secondary collection 'donorStats' and
    ensures that each hospital's data includes all eight blood types.
    Returns a list of tuples in the format:
      (hospitalName, city, [ (bloodType, totalBloodCC, surplus, shortage), ... ])
    For any blood type missing in a hospital's data, 0 is used as the amount and flags are set to False.
    """
    complete_blood_types = ["O+", "A+", "B+", "AB+", "O-", "A-", "B-", "AB-"]
    hospitals = list(db.donorStats.find())
    results = []
    for hosp in hospitals:
        hospital_name = hosp.get("hospital")
        city = hosp.get("city")
        
        # Build lookup dictionaries for inventory amounts and flag settings.
        inv_lookup = { inv.get("bloodType"): inv.get("totalBloodCC", 0) 
                       for inv in hosp.get("inventoryStats", []) }
        flag_lookup = { bt.get("bloodType"): (bt.get("surplus", False), bt.get("shortage", False))
                        for bt in hosp.get("bloodTypeStats", []) }
        
        # Create a complete list of blood type data.
        blood_data = []
        for bt in complete_blood_types:
            total = inv_lookup.get(bt, 0)
            surplus, shortage = flag_lookup.get(bt, (False, False))
            blood_data.append((bt, total, surplus, shortage))
        
        results.append((hospital_name, city, blood_data))
    return results

def main():

    #return all this data with an endpoint
    client = MongoClient("mongodb://localhost:27017")
    db = client["americanRedCrossDB"]
    hospitals_data = get_complete_hospital_data(db)
    for hospital in hospitals_data:
        print(f"Hospital: {hospital[0]}, City: {hospital[1]}")
        for bt_info in hospital[2]:
            print(f"  Blood Type: {bt_info[0]}, Amount: {bt_info[1]} CC, Surplus: {bt_info[2]}, Shortage: {bt_info[3]}")
        print("-----")

if __name__ == "__main__":
    main()
