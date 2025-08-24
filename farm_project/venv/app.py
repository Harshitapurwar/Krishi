

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

# from flask import Flask, request, jsonify
# import google.generativeai as genai
# import os

# # --- Configure Gemini ---
# genai.configure(api_key="AIzaSyDvCiTwlor31K4VxgGMuYYlvk52sfyILG0")

# # Load the Gemini model
# model = genai.GenerativeModel("gemini-1.5-flash")

# # Initialize Flask app
# app = Flask(__name__)

# @app.route("/analyze-leaf", methods=["POST"])
# def analyze_leaf():
#     try:
#         # Check if an image was uploaded
#         if "image" not in request.files:
#             return jsonify({"error": "No image uploaded"}), 400

#         image_file = request.files["image"]

#         # Read image data
#         image_data = image_file.read()

#         # Send image + prompt to Gemini
#         response = model.generate_content([
#             "Analyze this plant leaf and check if there is any disease. "
#             "If diseased, mention the possible disease name. Don't worry if it is wrong, "
#             "just give one disease name, a 4-line explanation, and how we can cure it.",
#             {"mime_type": "image/jpeg", "data": image_data}
#         ])

#         # Return response as JSON
#         return jsonify({"result": response.text})

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# if __name__ == "__main__":
#     app.run(debug=True, port=5000)
