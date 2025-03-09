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
from managmentAuth import add_hospital, update_secondary_data, verify_auth0_user

app = Flask(__name__)
CORS(app)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["americanRedCrossDB"]

@app.route("/hospital/matching/surplus", methods=["GET"])
def matching_surplus():
    """
    Expects query parameters:
      - shortage_hospital: Hospital with a shortage.
      - shortage_city: Its city.
      - blood_type: Blood type needed.
      - max_results: (Optional) Maximum number of matches (default 5).
      
    Returns JSON: list of surplus hospital matches.
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
    Expects query parameters:
      - surplus_hospital: Hospital with a surplus.
      - surplus_city: Its city.
      - blood_type: Blood type in surplus.
      - max_results: (Optional) Maximum number of matches (default 5).
      
    Returns JSON: list of shortage hospital matches.
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
    For a hospital with a donor shortage of a given blood type, returns a list of donors
    from other hospitals sorted by distance from the shortage hospital.
    
    Expects query parameters:
      - shortage_hospital: Hospital with donor shortage.
      - shortage_city: Its city.
      - blood_type: Blood type of interest.
      - max_results: (Optional) Maximum number of donor matches (default 5).
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
    For a hospital with a donor surplus (or for matching purposes), returns a list of donors
    from other hospitals with the specified blood type sorted by distance from the surplus hospital.
    
    Expects query parameters:
      - surplus_hospital: Hospital with donor surplus.
      - surplus_city: Its city.
      - blood_type: Blood type.
      - max_results: (Optional) Maximum number of donor matches (default 5).
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

@app.route("/hospital/data", methods=["GET"])
def hospital_data_endpoint():
     """
     Returns aggregated hospital data as JSON.
     """
     data = get_complete_hospital_data(db)
     return Response(dumps(data), mimetype="application/json"), 200

@app.route("/hospital/dataLoc", methods=["GET"])
def hospital_dataLoc_endpoint():
     """
     Returns aggregated hospital data as JSON.
     """
     data = get_complete_hospital_data_with_location(db)
     return Response(dumps(data), mimetype="application/json"), 200

@app.route("/hospital/login", methods=["POST"])
def hospital_login():
     """
     Expects JSON payload:
     {
       "hospital": "Central Medical Center",
       "password": "pass123"
     }
     If authentication succeeds, returns a JSON response with an access token.
     """
     data = request.get_json(force=True)
     if "hospital" not in data or "password" not in data:
         return Response(dumps({"error": "Missing hospital or password"}), mimetype="application/json"), 400
 
     hospital = data["hospital"]
     password = data["password"]
     auth_response = verify_auth0_user(hospital, password)
     if auth_response:
         # In TEST_MODE, we return a dummy token; in production, the actual JWT from Auth0.
         return Response(
             dumps({"message": "Login successful", "access_token": auth_response.get("access_token")}),
             mimetype="application/json"
         ), 200
     else:
         return Response(dumps({"error": "Invalid credentials"}), mimetype="application/json"), 401
 
@app.route("/blood/update", methods=["POST"])
def update_blood_inventory():
     """
     Expects JSON payload:
     {
        "hospital": "Central Medical Center",
        "city": "Boston, MA",
        "bloodType": "A+",
        "delta_count": 5,  # positive to add, negative to remove
        "password": "pass123"
     }
     Returns a JSON response.
     """
     try:
         data = request.get_json(force=True)
     except Exception as e:
         return Response(dumps({"error": str(e)}), mimetype="application/json"), 400
 
     required_fields = ["hospital", "city", "bloodType", "delta_count", "password"]
     if not all(field in data for field in required_fields):
         return Response(dumps({"error": "Missing required fields."}), mimetype="application/json"), 400
 
     try:
         delta_count = int(data["delta_count"])
     except ValueError:
         return Response(dumps({"error": "delta_count must be an integer."}), mimetype="application/json"), 400
 
     # Call your update function from management module
     from hospital_managment import update_hospital_inventory, update_secondary_data, search_secondary
     update_hospital_inventory(db, data["hospital"], data["city"], data["bloodType"], delta_count, password=data["password"])
     update_secondary_data(db)
     updated = search_secondary(db, data["hospital"], data["city"])
     return Response(dumps({"message": "Blood inventory updated successfully.", "updated_record": updated}),
                     mimetype="application/json"), 200

@app.route("/hospital/create", methods=["POST"])
def create_hospital_endpoint():
    """
    Creates a new hospital. Expects JSON payload:
    {
      "name": "Hospital Example",
      "city": "City, State",
      "coordinates": {"lat": 40.7128, "lon": -74.0060},
      "password": "yourPassword",
      "flagSettings": {    // optional
          "A+": {"surplus": true, "shortage": false},
          "O+": {"surplus": false, "shortage": true},
          ...
      }
    }
    Registers the hospital with Auth0 and inserts it into the database.
    """
    data = request.get_json(force=True)
    required_fields = ["name", "city", "coordinates", "password"]
    if not all(field in data for field in required_fields):
        return Response(dumps({"error": "Missing required fields: name, city, coordinates, and password"}), mimetype="application/json"), 400

    new_hosp = add_hospital(db, data)
    if new_hosp is None:
        return Response(dumps({"error": "Hospital creation failed."}), mimetype="application/json"), 500
    
    # Optionally update aggregated data.
    update_secondary_data(db)
    return Response(dumps({"message": f"Hospital '{new_hosp['name']}' created successfully.", "hospital": new_hosp}), mimetype="application/json"), 201


@app.route("/test", methods=["GET"])
def test_endpoint():
    return Response("Hello, Flask!", mimetype="text/plain"), 200

if __name__ == "__main__":
    app.run(debug=True, port=5001)
