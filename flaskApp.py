# flask_app.py
from flask import Flask, jsonify, request
from pymongo import MongoClient
from hospital_data import get_complete_hospital_data
from hospital_matching import match_hospital_with_shortage_to_surplus

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["americanRedCrossDB"]

@app.route("/hospital/data", methods=["GET"])
def hospital_data_endpoint():
    """
    Returns aggregated hospital data (complete data for all blood types)
    in JSON format.
    """
    data = get_complete_hospital_data(db)
    return jsonify(data), 200

@app.route("/test")
def test_endpoint():
    return "Hello, world!", 200


@app.route("/hospital/matching", methods=["GET"])
def hospital_matching_endpoint():
    """
    Expects query parameters:
      - shortage_hospital: The name of the hospital with shortage.
      - shortage_city: The city of the shortage hospital.
      - blood_type: The blood type for which a match is needed.
      - max_results: (Optional) The maximum number of matching hospitals to return (default is 5).
      
    Returns a JSON array of matching hospitals sorted by distance.
    """
    shortage_hospital = request.args.get("shortage_hospital")
    shortage_city = request.args.get("shortage_city")
    blood_type = request.args.get("blood_type")
    try:
        max_results = int(request.args.get("max_results", 5))
    except ValueError:
        return jsonify({"error": "max_results must be an integer"}), 400

    if not shortage_hospital or not shortage_city or not blood_type:
        return jsonify({"error": "Missing required query parameters: shortage_hospital, shortage_city, blood_type"}), 400

    matches = match_hospital_with_shortage_to_surplus(db, shortage_hospital, shortage_city, blood_type, max_results)
    return jsonify(matches), 200

if __name__ == "__main__":
    app.run(debug=True, port=5001)
