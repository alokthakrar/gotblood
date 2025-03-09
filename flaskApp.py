from flask import Flask, request, Response
from pymongo import MongoClient
from bson.json_util import dumps
from hospital_data import get_complete_hospital_data
from hospital_matching import match_hospital_with_shortage_to_surplus
from managementAuth import verify_auth0_user

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["americanRedCrossDB"]

@app.route("/hospital/data", methods=["GET"])
def hospital_data_endpoint():
    """
    Returns aggregated hospital data as JSON.
    """
    data = get_complete_hospital_data(db)
    return Response(dumps(data), mimetype="application/json"), 200

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

@app.route("/hospital/matching", methods=["GET"])
def hospital_matching_endpoint():
    """
    Expects query parameters:
      - shortage_hospital: Name of hospital with shortage.
      - shortage_city: City of that hospital.
      - blood_type: Blood type for which a match is needed.
      - max_results: (Optional) Maximum number of results (default 5).
    Returns matching hospitals as JSON.
    """
    shortage_hospital = request.args.get("shortage_hospital")
    shortage_city = request.args.get("shortage_city")
    blood_type = request.args.get("blood_type")
    try:
        max_results = int(request.args.get("max_results", 5))
    except ValueError:
        return Response(dumps({"error": "max_results must be an integer"}), mimetype="application/json"), 400

    if not shortage_hospital or not shortage_city or not blood_type:
        return Response(dumps({"error": "Missing required query parameters: shortage_hospital, shortage_city, blood_type"}),
                        mimetype="application/json"), 400

    matches = match_hospital_with_shortage_to_surplus(db, shortage_hospital, shortage_city, blood_type, max_results)
    return Response(dumps(matches), mimetype="application/json"), 200

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


@app.route("/test", methods=["GET"])
def test_endpoint():
    return Response("Hello, Flask!", mimetype="text/plain"), 200

if __name__ == "__main__":
    app.run(debug=True, port=5001)
