from flask import Flask, request, jsonify, send_from_directory
from twilio.rest import Client
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

API_KEY = "SECRET123"

# Store last reported location in memory for quick checks
last_location = None

# Twilio credentials from environment variables
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE_NUMBER")

# Initialize Twilio client
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
else:
    twilio_client = None

@app.route("/trigger", methods=["POST"])
def trigger_sms():
    data = request.get_json(silent=True) or {}

    if data.get("api_key") != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    if data.get("event") == "BUTTON_TRIPLE_PRESS":
        phone_number = data.get("phone")
        lat = data.get("lat")
        lon = data.get("lon")
        accuracy = data.get("accuracy")
        
        if not lat or not lon:
            return jsonify({"error": "lat and lon required in request"}), 400
        
        if not phone_number:
            return jsonify({"error": "Phone number required"}), 400
        
        if not twilio_client:
            return jsonify({"error": "Twilio not configured"}), 500

        accuracy_text = f"Accuracy: {accuracy} m" if accuracy else ""
        message_text = (
            f"Location: {lat}, {lon}\n"
            f"{accuracy_text}"
        ).strip()

        try:
            message = twilio_client.messages.create(
                body=message_text,
                from_=TWILIO_PHONE,
                to=phone_number
            )
            return jsonify({
                "action": "SMS_SENT",
                "message_sid": message.sid,
                "status": "success"
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"action": "NONE"})

@app.route("/")
def home():
    return send_from_directory("static", "index.html")

@app.route("/location", methods=["POST"])
def save_location():
    global last_location
    data = request.get_json(silent=True) or {}

    if data.get("api_key") != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    lat = data.get("lat")
    lon = data.get("lon")
    accuracy = data.get("accuracy")
    timestamp = data.get("timestamp")

    if lat is None or lon is None:
        return jsonify({"error": "lat and lon required"}), 400

    last_location = {
        "lat": lat,
        "lon": lon,
        "accuracy": accuracy,
        "timestamp": timestamp,
        "source": "browser"
    }

    return jsonify({"status": "saved", "location": last_location})

@app.route("/location/latest", methods=["GET"])
def get_latest_location():
    if not last_location:
        return jsonify({"error": "No location reported yet"}), 404

    return jsonify({"location": last_location})

@app.route("/location/send", methods=["POST"])
def send_latest_location():
    data = request.get_json(silent=True) or {}

    if data.get("api_key") != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    phone_number = data.get("phone")
    if not phone_number:
        return jsonify({"error": "Phone number required"}), 400

    if not last_location:
        return jsonify({"error": "No location reported yet"}), 404

    if not twilio_client:
        return jsonify({"error": "Twilio not configured"}), 500

    lat = last_location.get("lat")
    lon = last_location.get("lon")
    accuracy = last_location.get("accuracy")
    timestamp = last_location.get("timestamp")

    message_text = (
        "Location update:\n"
        f"Lat: {lat}\n"
        f"Lon: {lon}\n"
        f"Accuracy: {accuracy} m\n"
        f"Timestamp: {timestamp}"
    )

    try:
        message = twilio_client.messages.create(
            body=message_text,
            from_=TWILIO_PHONE,
            to=phone_number
        )
        return jsonify({
            "action": "SMS_SENT",
            "message_sid": message.sid,
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
