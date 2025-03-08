# flask_app.py
from flask import Flask, jsonify, request
from pymongo import MongoClient
from hospital_data import get_complete_hospital_data
from hospital_matching import match_hospital_with_shortage_to_surplus
from mailchimp_marketing import Client
from mailchimp_marketing.api_client import ApiClientError
from flask.ext.elasticsearch import FlaskElasticsearch

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["americanRedCrossDB"]
es = FlaskElasticsearch("http://localhost:9200")
es.init_app(app)


# Mailchimp Configuration
mailchimp = Client()
mailchimp.set_config({
    "api_key": "58d63b0d8745d5bad45f51d9eaecd283-us14",  # Replace with your actual API key
    "server": "us14"  # Replace with your server prefix (e.g., 'us1', 'us20')
})
MAILCHIMP_LIST_ID = "got blood?" # Replace with your Mailchimp list ID
@app.route('/api/signup', methods=['POST'])
def signup():
    signup_data = request.get_json()

    if not signup_data or 'email' not in signup_data:
        return jsonify({"error": "Email is required for signup."}), 400

    email = signup_data.get('email')
    blood_type = signup_data.get('bloodType')
    latitude = signup_data.get('latitude')
    longitude = signup_data.get('longitude')

    try:
        member_info = {
            "email_address": email,
            "status": "subscribed",  # or 'pending' if you want double opt-in
            "merge_fields": {
                "BLOODTYPE": blood_type,  # Merge tag names must be in ALL CAPS and match your Mailchimp audience fields
                "LATITUDE": latitude,     # Adjust merge tag names as needed in Mailchimp
                "LONGITUDE": longitude
            }
        }

        response = mailchimp.lists.add_list_member(MAILCHIMP_LIST_ID, member_info)
        print(f"Mailchimp API Response: {response}") # Optional: Log the response for debugging
        return jsonify({"message": "Signup successful! Added to Mailchimp list."}), 200

    except ApiClientError as error:
        print(f"Mailchimp API Error: {error.text}")
        return jsonify({"error": "Mailchimp signup failed.", "mailchimp_error": error.text}), 500
    except Exception as e:
        print(f"Signup error: {e}")
        return jsonify({"error": "Signup failed due to an unexpected error."}), 500

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
