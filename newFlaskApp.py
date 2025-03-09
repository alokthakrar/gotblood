# flaskApp.py
from flask import Flask, request, Response
from flask_cors import CORS
from pymongo import MongoClient
from bson.json_util import dumps
from hospital_matching import (
    match_surplus_for_shortage,
    match_shortage_for_surplus,
    match_donors_for_shortage,
    match_donors_for_surplus
)
from hospital_data import get_complete_hospital_data, get_complete_hospital_data_with_location
from managmentAuth import (
    add_hospital,
    add_donor_and_update,
    remove_donor_and_update,
    update_hospital_inventory,
    update_inventory_flag,
    update_secondary_data
)

app = Flask(__name__)
CORS(app)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["americanRedCrossDB"]

# ---------------------------
# Hospital Endpoints
# ---------------------------
@app.route("/hospital/create", methods=["POST"])
def create_hospital_endpoint():
    """
    Creates a new hospital.
    Expects JSON payload:
    {
      "name": "Example Hospital",
      "city": "New York, NY",
      "coordinates": {"lat": 40.7128, "lon": -74.0060},
      "password": "testPassword",           // Will be ignored in non-auth mode.
      "flagSettings": {  
         "O+": {"surplus": true, "shortage": false},
         "A+": {"surplus": false, "shortage": true},
         ... // for all blood types
      }
    }
    """
    data = request.get_json(force=True)
    required = ["name", "city", "coordinates", "password"]
    if not all(field in data for field in required):
        return Response(dumps({"error": "Missing required fields: name, city, coordinates, and password"}), mimetype="application/json"), 400

    new_hosp = add_hospital(db, data)
    if not new_hosp:
        return Response(dumps({"error": "Hospital creation failed."}), mimetype="application/json"), 500
    update_secondary_data(db)
    return Response(dumps({"message": f"Hospital '{new_hosp['name']}' created successfully.", "hospital": new_hosp}), mimetype="application/json"), 201

@app.route("/hospital/inventory/update", methods=["POST"])
def update_inventory_endpoint():
    """
    Updates hospital blood inventory.
    Expects JSON payload:
    {
      "hospital": "Example Hospital",
      "city": "New York, NY",
      "bloodType": "A+",
      "delta_count": 5
    }
    """
    data = request.get_json(force=True)
    required = ["hospital", "city", "bloodType", "delta_count"]
    if not all(field in data for field in required):
        return Response(dumps({"error": "Missing required fields."}), mimetype="application/json"), 400
    try:
        delta = int(data["delta_count"])
    except ValueError:
        return Response(dumps({"error": "delta_count must be an integer."}), mimetype="application/json"), 400

    # Note: In non-auth mode, the password is ignored.
    update_hospital_inventory(db, data["hospital"], data["city"], data["bloodType"], delta, password=None)
    update_secondary_data(db)
    return Response(dumps({"message": "Inventory updated successfully."}), mimetype="application/json"), 200

@app.route("/hospital/flag/update", methods=["POST"])
def update_flag_endpoint():
    """
    Updates a hospital's blood type flag (surplus/shortage).
    Expects JSON payload:
    {
      "hospital": "Example Hospital",
      "city": "New York, NY",
      "bloodType": "A+",
      "surplus": true,         // optional
      "shortage": false        // optional
    }
    """
    data = request.get_json(force=True)
    required = ["hospital", "city", "bloodType"]
    if not all(field in data for field in required):
        return Response(dumps({"error": "Missing required fields."}), mimetype="application/json"), 400

    update_inventory_flag(db, data["hospital"], data["city"], data["bloodType"],
                          surplus=data.get("surplus"), shortage=data.get("shortage"),
                          password=None)
    update_secondary_data(db)
    return Response(dumps({"message": "Inventory flags updated successfully."}), mimetype="application/json"), 200

@app.route("/hospital/data", methods=["GET"])
def hospital_data_endpoint():
    """
    Returns aggregated hospital data as JSON.
    """
    data = get_complete_hospital_data(db)
    return Response(dumps(data), mimetype="application/json"), 200

@app.route("/hospital/data/loc", methods=["GET"])
def hospital_data_loc_endpoint():
    """
    Returns aggregated hospital data along with coordinates as JSON.
    """
    data = get_complete_hospital_data_with_location(db)
    return Response(dumps(data), mimetype="application/json"), 200

# ---------------------------
# Donor Endpoints
# ---------------------------
@app.route("/donor/add", methods=["POST"])
def add_donor_endpoint():
    """
    Adds a donor.
    Expects JSON payload:
    {
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
      "contact_info": {"email": "johndoe@example.com", "phone": "123-456-7890"}
    }
    """
    donor_data = request.get_json(force=True)
    required = ["donor_id", "first_name", "last_name", "age", "blood_type", "location"]
    if not all(field in donor_data for field in required):
        return Response(dumps({"error": "Missing required donor fields."}), mimetype="application/json"), 400

    from hospital_managment import add_donor_and_update
    add_donor_and_update(db, donor_data)
    return Response(dumps({"message": "Donor added successfully."}), mimetype="application/json"), 201

@app.route("/donor/remove", methods=["POST"])
def remove_donor_endpoint():
    """
    Removes a donor.
    Expects JSON payload:
    {
      "donor_id": "D0000001"
    }
    """
    data = request.get_json(force=True)
    if "donor_id" not in data:
        return Response(dumps({"error": "Missing donor_id."}), mimetype="application/json"), 400

    from hospital_managment import remove_donor_and_update
    remove_donor_and_update(db, data["donor_id"])
    return Response(dumps({"message": "Donor removed successfully."}), mimetype="application/json"), 200

# ---------------------------
# Matching Endpoints
# ---------------------------
@app.route("/hospital/matching/surplus", methods=["GET"])
def matching_surplus():
    """
    For a hospital with a shortage, returns up to max_results hospitals with a surplus for the given blood type.
    Query parameters:
      - shortage_hospital: Hospital with a shortage.
      - shortage_city: Its city.
      - blood_type: Blood type needed.
      - max_results: (Optional) Default is 5.
    """
    shortage_hospital = request.args.get("shortage_hospital")
    shortage_city = request.args.get("shortage_city")
    blood_type = request.args.get("blood_type")
    try:
        max_results = int(request.args.get("max_results", 5))
    except ValueError:
        return Response(dumps({"error": "max_results must be an integer"}), mimetype="application/json"), 400

    if not shortage_hospital or not shortage_city or not blood_type:
        return Response(dumps({"error": "Missing required parameters"}), mimetype="application/json"), 400

    matches = match_surplus_for_shortage(db, shortage_hospital, shortage_city, blood_type, max_results)
    return Response(dumps(matches), mimetype="application/json"), 200

@app.route("/hospital/matching/shortage", methods=["GET"])
def matching_shortage():
    """
    For a hospital with a surplus, returns up to max_results hospitals with a shortage for the given blood type.
    Query parameters:
      - surplus_hospital: Hospital with a surplus.
      - surplus_city: Its city.
      - blood_type: Blood type.
      - max_results: (Optional) Default is 5.
    """
    surplus_hospital = request.args.get("surplus_hospital")
    surplus_city = request.args.get("surplus_city")
    blood_type = request.args.get("blood_type")
    try:
        max_results = int(request.args.get("max_results", 5))
    except ValueError:
        return Response(dumps({"error": "max_results must be an integer"}), mimetype="application/json"), 400

    if not surplus_hospital or not surplus_city or not blood_type:
        return Response(dumps({"error": "Missing required parameters"}), mimetype="application/json"), 400

    matches = match_shortage_for_surplus(db, surplus_hospital, surplus_city, blood_type, max_results)
    return Response(dumps(matches), mimetype="application/json"), 200

@app.route("/donor/matching/shortage", methods=["GET"])
def donor_matching_shortage():
    """
    For a hospital with a donor shortage, returns up to max_results donors (from other hospitals)
    with the specified blood type, sorted by distance from the shortage hospital.
    Query parameters:
      - shortage_hospital: Hospital with donor shortage.
      - shortage_city: Its city.
      - blood_type: Blood type.
      - max_results: (Optional) Default is 5.
    """
    shortage_hospital = request.args.get("shortage_hospital")
    shortage_city = request.args.get("shortage_city")
    blood_type = request.args.get("blood_type")
    try:
        max_results = int(request.args.get("max_results", 5))
    except ValueError:
        return Response(dumps({"error": "max_results must be an integer"}), mimetype="application/json"), 400

    if not shortage_hospital or not shortage_city or not blood_type:
        return Response(dumps({"error": "Missing required parameters"}), mimetype="application/json"), 400

    matches = match_donors_for_shortage(db, shortage_hospital, shortage_city, blood_type, max_results)
    return Response(dumps(matches), mimetype="application/json"), 200

@app.route("/donor/matching/surplus", methods=["GET"])
def donor_matching_surplus():
    """
    For a hospital with a donor surplus, returns up to max_results donors (from other hospitals)
    with the specified blood type, sorted by distance from the surplus hospital.
    Query parameters:
      - surplus_hospital: Hospital with donor surplus.
      - surplus_city: Its city.
      - blood_type: Blood type.
      - max_results: (Optional) Default is 5.
    """
    surplus_hospital = request.args.get("surplus_hospital")
    surplus_city = request.args.get("surplus_city")
    blood_type = request.args.get("blood_type")
    try:
        max_results = int(request.args.get("max_results", 5))
    except ValueError:
        return Response(dumps({"error": "max_results must be an integer"}), mimetype="application/json"), 400

    if not surplus_hospital or not surplus_city or not blood_type:
        return Response(dumps({"error": "Missing required parameters"}), mimetype="application/json"), 400

    matches = match_donors_for_surplus(db, surplus_hospital, surplus_city, blood_type, max_results)
    return Response(dumps(matches), mimetype="application/json"), 200

@app.route("/test", methods=["GET"])
def test_endpoint():
    return Response("Hello, Flask!", mimetype="text/plain"), 200

if __name__ == "__main__":
    app.run(debug=True, port=5001)
