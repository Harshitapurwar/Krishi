

# app.py
from flask import Flask, request, jsonify
from advisory import generate_advisory

app = Flask(__name__)

@app.route("/advisory", methods=["POST"])
def advisory_endpoint():
    try:
        data = request.get_json()
        place_name = data.get("place_name", "Agra")
        crop_name = data.get("crop_name", "Wheat")

        # Input CSV paths (adjust as needed)
        weather_csv = "data/weather_forecast.csv"
        market_csv = "data/uttar_pradesh_data2.csv"

        result = generate_advisory(
            place_name=place_name,
            crop_name=crop_name,
            weather_csv=weather_csv,
            market_csv=market_csv
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
