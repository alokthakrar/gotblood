# readDataApp.py
from flask import Flask, jsonify
from pymongo import MongoClient
from hospital_data import get_complete_hospital_data, get_complete_hospital_data_with_location
# Optionally, if you have a donors retrieval function:
# from donors_db import get_all_donors

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["americanRedCrossDB"]

@app.route("/hospital/data", methods=["GET"])
def hospital_data_endpoint():
    """
    Returns aggregated hospital data as JSON.
    This endpoint returns data from the secondary collection.
    """
    data = get_complete_hospital_data(db)
    return jsonify(data)

@app.route("/hospital/data/loc", methods=["GET"])
def hospital_data_with_location_endpoint():
    """
    Returns aggregated hospital data including coordinates.
    """
    data = get_complete_hospital_data_with_location(db)
    return jsonify(data)

# If you want an endpoint to get all donors from the donors collection:
@app.route("/donor/data", methods=["GET"])
def donor_data_endpoint():
    """
    Returns all donor documents as JSON.
    """
    donors = list(db.donors.find())
    return jsonify(donors)

@app.route("/test", methods=["GET"])
def test_endpoint():
    return "Hello, Flask! This endpoint only retrieves data.", 200

if __name__ == "__main__":
    app.run(debug=True, port=5001)
