# flaskApp.py
from flask import Flask, request, Response
from pymongo import MongoClient
from bson.json_util import dumps
from hospital_matching import (
    match_surplus_for_shortage,
    match_shortage_for_surplus,
    match_donors_for_shortage,
    match_donors_for_surplus
)

from hospital_data import get_complete_hospital_data

app = Flask(__name__)

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

@app.route("/test", methods=["GET"])
def test_endpoint():
    return Response("Hello, Flask!", mimetype="text/plain"), 200

if __name__ == "__main__":
    app.run(debug=True, port=5001)
