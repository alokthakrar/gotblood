# newFlaskApp.py
from flask import Flask, request, Response
from pymongo import MongoClient
from bson.json_util import dumps
from hospital_matching import (
    match_surplus_for_shortage,
    match_shortage_for_surplus,
    match_donors_for_shortage,
    match_donors_for_surplus
)
from hospital_data import get_complete_hospital_data, get_complete_hospital_data_with_location
from managementAuth import (
    add_hospital,
    add_donor_and_update,
    remove_donor_and_update,
    update_hospital_inventory,
    update_inventory_flag,
    update_secondary_data,
    verify_auth0_user,
    register_auth0_user
)

app = Flask(__name__)

# Connect to MongoDB (adjust connection string if needed)
client = MongoClient("mongodb://localhost:27017")
db = client["americanRedCrossDB"]

# ---------------------------
# Hospital Endpoints
# ---------------------------
@app.route("/hospital/create", methods=["POST"])
def create_hospital_endpoint():
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
    data = request.get_json(force=True)
    required = ["hospital", "city", "bloodType", "delta_count"]
    if not all(field in data for field in required):
        return Response(dumps({"error": "Missing required fields."}), mimetype="application/json"), 400
    try:
        delta = int(data["delta_count"])
    except ValueError:
        return Response(dumps({"error": "delta_count must be an integer."}), mimetype="application/json"), 400

    # In this version, we bypass authentication by not checking password.
    update_hospital_inventory(db, data["hospital"], data["city"], data["bloodType"], delta, password=None)
    update_secondary_data(db)
    return Response(dumps({"message": "Inventory updated successfully."}), mimetype="application/json"), 200

@app.route("/hospital/flag/update", methods=["POST"])
def update_flag_endpoint():
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
    data = get_complete_hospital_data(db)
    return Response(dumps(data), mimetype="application/json"), 200

@app.route("/hospital/data/loc", methods=["GET"])
def hospital_data_loc_endpoint():
    data = get_complete_hospital_data_with_location(db)
    return Response(dumps(data), mimetype="application/json"), 200

# ---------------------------
# Donor Endpoints
# ---------------------------
@app.route("/donor/add", methods=["POST"])
def add_donor_endpoint():
    donor_data = request.get_json(force=True)
    required = ["donor_id", "first_name", "last_name", "age", "blood_type", "location"]
    if not all(field in donor_data for field in required):
        return Response(dumps({"error": "Missing required donor fields."}), mimetype="application/json"), 400

    from managementAuth import add_donor_and_update
    add_donor_and_update(db, donor_data)
    return Response(dumps({"message": "Donor added successfully."}), mimetype="application/json"), 201

@app.route("/donor/remove", methods=["POST"])
def remove_donor_endpoint():
    data = request.get_json(force=True)
    if "donor_id" not in data:
        return Response(dumps({"error": "Missing donor_id."}), mimetype="application/json"), 400

    from managementAuth import remove_donor_and_update
    remove_donor_and_update(db, data["donor_id"])
    return Response(dumps({"message": "Donor removed successfully."}), mimetype="application/json"), 200

# ---------------------------
# Matching Endpoints (using POST with JSON body instead of GET query parameters)
# ---------------------------
@app.route("/hospital/matching/surplus", methods=["POST"])
def matching_surplus_endpoint():
    """
    Expects JSON payload:
    {
      "shortage_hospital": "General Hospital 1",
      "shortage_city": "Los Angeles, CA",
      "blood_type": "A+",
      "max_results": 5    // optional; default is 5
    }
    Returns a JSON list of surplus hospital matches.
    """
    data = request.get_json(force=True)
    required = ["shortage_hospital", "shortage_city", "blood_type"]
    if not all(field in data for field in required):
        return Response(dumps({"error": "Missing required parameters."}), mimetype="application/json"), 400

    max_results = data.get("max_results", 5)
    try:
        max_results = int(max_results)
    except ValueError:
        return Response(dumps({"error": "max_results must be an integer."}), mimetype="application/json"), 400

    matches = match_surplus_for_shortage(db, data["shortage_hospital"], data["shortage_city"], data["blood_type"], max_results)
    return Response(dumps(matches), mimetype="application/json"), 200

@app.route("/hospital/matching/shortage", methods=["POST"])
def matching_shortage_endpoint():
    """
    Expects JSON payload:
    {
      "surplus_hospital": "Central Medical Center",
      "surplus_city": "Boston, MA",
      "blood_type": "A+",
      "max_results": 5    // optional; default is 5
    }
    Returns a JSON list of shortage hospital matches.
    """
    data = request.get_json(force=True)
    required = ["surplus_hospital", "surplus_city", "blood_type"]
    if not all(field in data for field in required):
        return Response(dumps({"error": "Missing required parameters."}), mimetype="application/json"), 400

    max_results = data.get("max_results", 5)
    try:
        max_results = int(max_results)
    except ValueError:
        return Response(dumps({"error": "max_results must be an integer."}), mimetype="application/json"), 400

    matches = match_shortage_for_surplus(db, data["surplus_hospital"], data["surplus_city"], data["blood_type"], max_results)
    return Response(dumps(matches), mimetype="application/json"), 200

@app.route("/donor/matching/shortage", methods=["POST"])
def donor_matching_shortage_endpoint():
    """
    Expects JSON payload:
    {
      "shortage_hospital": "General Hospital 1",
      "shortage_city": "Los Angeles, CA",
      "blood_type": "A+",
      "max_results": 5    // optional; default is 5
    }
    Returns a JSON list of donor matches for a shortage hospital.
    """
    data = request.get_json(force=True)
    required = ["shortage_hospital", "shortage_city", "blood_type"]
    if not all(field in data for field in required):
        return Response(dumps({"error": "Missing required parameters."}), mimetype="application/json"), 400

    max_results = data.get("max_results", 5)
    try:
        max_results = int(max_results)
    except ValueError:
        return Response(dumps({"error": "max_results must be an integer."}), mimetype="application/json"), 400

    matches = match_donors_for_shortage(db, data["shortage_hospital"], data["shortage_city"], data["blood_type"], max_results)
    return Response(dumps(matches), mimetype="application/json"), 200

@app.route("/donor/matching/surplus", methods=["POST"])
def donor_matching_surplus_endpoint():
    """
    Expects JSON payload:
    {
      "surplus_hospital": "Central Medical Center",
      "surplus_city": "Boston, MA",
      "blood_type": "A+",
      "max_results": 5    // optional; default is 5
    }
    Returns a JSON list of donor matches for a surplus hospital.
    """
    data = request.get_json(force=True)
    required = ["surplus_hospital", "surplus_city", "blood_type"]
    if not all(field in data for field in required):
        return Response(dumps({"error": "Missing required parameters."}), mimetype="application/json"), 400

    max_results = data.get("max_results", 5)
    try:
        max_results = int(max_results)
    except ValueError:
        return Response(dumps({"error": "max_results must be an integer."}), mimetype="application/json"), 400

    matches = match_donors_for_surplus(db, data["surplus_hospital"], data["surplus_city"], data["blood_type"], max_results)
    return Response(dumps(matches), mimetype="application/json"), 200

@app.route("/test", methods=["GET"])
def test_endpoint():
    return Response("Hello, Flask!", mimetype="text/plain"), 200

if __name__ == "__main__":
    app.run(debug=True, port=5001)
