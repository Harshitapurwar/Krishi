# from flask import Flask, request, jsonify
# import pandas as pd
# import numpy as np
# from sklearn.linear_model import LinearRegression
# from datetime import datetime, timedelta

# app = Flask(__name__)

# # Load dataset
# df = pd.read_csv("data/uttar_pradesh_data_last2years_compact.csv")

# # Convert date
# df["Arrival_Date"] = pd.to_datetime(df["Arrival_Date"], format="%d-%m-%Y")

# # Train models for each crop+market
# models = {}
# for (commodity, market), group in df.groupby(["Commodity", "Market"]):
#     group = group.sort_values("Arrival_Date")
#     X = (group["Arrival_Date"] - group["Arrival_Date"].min()).dt.days.values.reshape(-1, 1)
#     y = group["Modal Price"].values
    
#     model = LinearRegression()
#     model.fit(X, y)
    
#     models[(commodity, market)] = {
#         "model": model,
#         "start_date": group["Arrival_Date"].min()
#     }

# def predict_price(commodity, market, target_date):
#     key = (commodity, market)
#     if key not in models:
#         return None
    
#     model_info = models[key]
#     model = model_info["model"]
#     start_date = model_info["start_date"]
    
#     days_since_start = (target_date - start_date).days
#     price_today = model.predict(np.array([[days_since_start]]))[0]
    
#     # Trend slope (7 days)
#     price_next = model.predict(np.array([[days_since_start+7]]))[0]
#     slope_7d = (price_next - price_today) / 7
    
#     # Delta in 3 days
#     price_3d = model.predict(np.array([[days_since_start+3]]))[0]
#     delta_3d = price_3d - price_today
    
#     # Monthly avg
#     past_month_start = target_date - timedelta(days=30)
#     mask = (df["Commodity"] == commodity) & (df["Market"] == market) & (df["Arrival_Date"] >= past_month_start) & (df["Arrival_Date"] <= target_date)
#     month_avg = df.loc[mask, "Modal Price"].mean() if not df.loc[mask].empty else price_today
#     above_month_avg = price_today > month_avg
    
#     # Best sell window (when max price in next 15 days occurs)
#     future_days = np.arange(days_since_start, days_since_start+15).reshape(-1, 1)
#     future_prices = model.predict(future_days)
#     best_sell_day = int(np.argmax(future_prices))  # in how many days
    
#     # Trend direction
#     if slope_7d > 5:
#         trend = "up"
#     elif slope_7d < -5:
#         trend = "down"
#     else:
#         trend = "stable"
    
#     return {
#         "price_today": round(float(price_today), 2),
#         "price_trend": trend,
#         "price_trend_slope_7d": round(float(slope_7d), 2),
#         "expected_price_delta_3d": round(float(delta_3d), 2),
#         "price_above_month_avg_flag": bool(above_month_avg),
#         "best_sell_window_days": int(best_sell_day)
#     }

# @app.route("/predict", methods=["POST"])
# def predict():
#     data = request.json
#     crop_type = data.get("crop_type")
#     market = data.get("market")
#     date_str = data.get("date")  # e.g. "2026-03-01"
    
#     try:
#         target_date = datetime.strptime(date_str, "%Y-%m-%d")
#     except:
#         return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400
    
#     result = predict_price(crop_type, market, target_date)
#     if result is None:
#         return jsonify({"error": "No model found for given crop and market"}), 404
    
#     return jsonify(result)
# @app.route("/predict_batch", methods=["POST"])
# def predict_batch():
#     data = request.json  # Expecting a list of requests
    
#     if not isinstance(data, list):
#         return jsonify({"error": "Input must be a list of requests"}), 400

#     results = []
#     for item in data:
#         crop_type = item.get("crop_type")
#         market = item.get("market")
#         date_str = item.get("date")

#         try:
#             target_date = datetime.strptime(date_str, "%Y-%m-%d")
#         except:
#             results.append({
#                 "crop_type": crop_type,
#                 "market": market,
#                 "error": "Invalid date format, use YYYY-MM-DD"
#             })
#             continue

#         result = predict_price(crop_type, market, target_date)
#         if result is None:
#             results.append({
#                 "crop_type": crop_type,
#                 "market": market,
#                 "error": "No model found for given crop and market"
#             })
#         else:
#             result.update({"crop_type": crop_type, "market": market})
#             results.append(result)

#     return jsonify(results)

# if __name__ == "__main__":
#     app.run(debug=True)


# app.py

# app.py
# from flask import Flask, request, jsonify
# from advisory import generate_advisory

# app = Flask(__name__)

# @app.route("/get-advisory", methods=["POST"])
# def get_advisory():
#     data = request.get_json()
#     place = data.get("place")
#     crop = data.get("crop")
#     weather_csv = data.get("data/weather_csv", "weather.csv")
#     market_csv = data.get("data/market_csv", "uttar_pradesh_data.csv")

#     if not place or not crop:
#         return jsonify({"error": "Please provide place and crop"}), 400

#     report = generate_advisory(place, crop, weather_csv, market_csv)
#     return jsonify(report)

# if __name__ == "__main__":
#     app.run(debug=True)


# app.py
from flask import Flask, request, jsonify
from advisory import generate_advisory

app = Flask(__name__)

@app.route("/advisory", methods=["POST"])
def advisory_endpoint():
    try:
        data = request.get_json()
        place_name = data.get("place_name", "")
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
