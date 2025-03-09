from flask import Flask, request, Response
from flask_cors import CORS
from pymongo import MongoClient
from bson.json_util import dumps
from hospital_data import get_complete_hospital_data
from hospital_matching import match_hospital_with_shortage_to_surplus
from mailchimp_marketing import Client
from mailchimp_marketing.api_client import ApiClientError


app = Flask(__name__)
CORS(app)
# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["americanRedCrossDB"]


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

@app.route("/test", methods=["GET"])
def test_endpoint():
    return Response("Hello, Flask!", mimetype="text/plain"), 200

if __name__ == "__main__":
    app.run(debug=True, port=5001)
