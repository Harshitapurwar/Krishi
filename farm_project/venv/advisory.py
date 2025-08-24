# # advisory.py

# def generate_farm_advisory(satellite_data, weather_data, market_data):
#     """
#     Generates a full advisory report for the farmer based on satellite, weather, and market data.
    
#     Args:
#         satellite_data (dict): Crop health and ripeness info.
#         weather_data (dict): Weather forecast and harvest window info.
#         market_data (dict): Current and expected market price info.
    
#     Returns:
#         dict: Advisory report containing harvest advice, market advice, and health warnings.
#     """
#     advisory = {}

#     # --- Harvest Advisory ---
#     ripeness = satellite_data.get("ripeness_percent", 0)
#     crop_health = satellite_data.get("crop_health_index", 1)
#     unhealthy_area = satellite_data.get("unhealthy_area_percent", 0)
#     expected_days_to_ripeness = satellite_data.get("expected_days_to_ripeness", 0)

#     extreme_weather = weather_data.get("extreme_weather_flag", False)
#     optimal_harvest_window = weather_data.get("optimal_harvest_window_days", 0)

#     # Decide harvest timing
#     if ripeness >= 70:
#         if extreme_weather:
#             advisory['harvest'] = "Harvest immediately due to extreme weather!"
#         else:
#             days_to_harvest = min(expected_days_to_ripeness, optimal_harvest_window)
#             advisory['harvest'] = f"Harvest in {days_to_harvest} days"
#     else:
#         advisory['harvest'] = f"Crop not fully ripe. Expected {expected_days_to_ripeness} days to ripeness"

#     # --- Crop Health Warnings ---
#     if crop_health < 0.5 or unhealthy_area > 40:
#         advisory['health_warning'] = "Crop stress detected. Inspect fields and consider intervention."

#     # --- Market Advisory ---
#     price_trend = market_data.get("price_trend", "stable")
#     best_sell_window = market_data.get("best_sell_window_days", 0)

#     if ripeness >= 70:
#         if price_trend == "up":
#             sell_days = min(best_sell_window, optimal_harvest_window)
#             advisory['market'] = f"Consider selling in {sell_days} days for higher profit"
#         elif price_trend == "down":
#             advisory['market'] = "Sell immediately after harvest to avoid price drop"
#         else:
#             advisory['market'] = "Price is stable. Sell within harvest window as convenient"
#     else:
#         advisory['market'] = "Wait until crop is ripe before selling"

#     # --- Optional: Weather Advisory ---
#     rain_forecast = weather_data.get("rain_forecast_next_7d", [])
#     if any(r > 20 for r in rain_forecast):
#         advisory['weather_warning'] = "Heavy rain expected in the next 7 days. Plan harvest accordingly."

#     return advisory

# # advisory.py
# import json
# from satellite import get_satellite_data  # your satellite.py function
# import pandas as pd
# from datetime import datetime

# def load_weather_data(csv_path):
#     df = pd.read_csv(csv_path)
#     df['date'] = pd.to_datetime(df['date'], errors='coerce')
#     return df

# def load_market_data(csv_path):
#     df = pd.read_csv(csv_path)
#     df['arrival_date'] = pd.to_datetime(df['arrival_date'], errors='coerce')
#     return df

# def generate_advisory(place_name, crop_name, weather_csv, market_csv):
#     # Step 1: Satellite NDVI data
#     sat_data = get_satellite_data(place_name)

#     # Step 2: Weather data analysis
#     weather_df = load_weather_data(weather_csv)
#     today = pd.Timestamp(datetime.now().date())
#     recent_weather = weather_df[weather_df['date'] <= today].tail(7) 

#     avg_temp = recent_weather['temperature'].mean()
#     avg_rain = recent_weather['rainfall'].mean()

#     # Step 3: Market data analysis
#     market_df = load_market_data(market_csv)
#     recent_market = market_df[(market_df['Commodity'].str.lower() == crop_name.lower())]
#     recent_market = recent_market.sort_values('arrival_date', ascending=False).head(5)
#     avg_price = recent_market['Modal Price'].mean()

#     # Step 4: Generate advisory
#     advisory = {
#         "place": place_name,
#         "crop": crop_name,
#         "satellite_data": sat_data,
#         "weather_summary": {
#             "avg_temperature": round(avg_temp, 2),
#             "avg_rainfall": round(avg_rain, 2)
#         },
#         "market_summary": {
#             "avg_price_last_5_days": round(avg_price, 2),
#             "last_5_prices": recent_market[['arrival_date', 'Modal Price']].to_dict(orient='records')
#         },
#         "actionable_advice": []
#     }

#     # Step 5: Actionable advice heuristics
#     if sat_data['crop_health_index'] < 0.5:
#         advisory['actionable_advice'].append("Crop health is low, consider inspecting for pests or nutrient deficiency.")
#     if sat_data['expected_days_to_ripeness'] <= 5:
#         advisory['actionable_advice'].append("Crops are nearing ripeness, prepare for harvesting soon.")
#     if avg_rain > 20:
#         advisory['actionable_advice'].append("Heavy rainfall expected, check drainage to avoid crop damage.")
#     if avg_price > 0:
#         advisory['actionable_advice'].append(f"Current market price is good: ₹{round(avg_price,2)}, consider selling if crops are ready.")

#     return advisory

# # Test function (optional)
# if __name__ == "__main__":
#     place_name=input("Enter place name:")
#     report = generate_advisory(
#         place_name=place_name,
#         crop_name="Wheat",
#         weather_csv="data/weather_forecast.csv",
#         market_csv="data/uttar_pradesh_data2.csv"
#     )
#     print(json.dumps(report, indent=2))



import pandas as pd
from satellite import get_satellite_data

def generate_advisory(place_name, crop_name, weather_csv, market_csv):
    advisory = {"place": place_name, "crop": crop_name, "advice": []}

    # 1. Satellite NDVI and crop health
    try:
        satellite_info = get_satellite_data(place_name)
        advisory["satellite"] = satellite_info
    except Exception as e:
        print("a")
        advisory["satellite_error"] = str(e)

    # 2. Weather Forecast
    try:
        weather = pd.read_csv(weather_csv)
        # Ensure correct datetime column
        weather['forecast_date'] = pd.to_datetime(weather['forecast_date'], errors="coerce")
        weather = weather.sort_values("forecast_date")

        # Example: take the latest forecast
        latest_weather = weather.iloc[-1].to_dict()
        advisory["weather"] = latest_weather

        if latest_weather["rainfall_mm"] > 20:
            advisory["advice"].append("Heavy rainfall expected — avoid irrigation.")
        else:
            advisory["advice"].append("No heavy rain — irrigation can be planned.")
        
        if latest_weather["temp_max_degC"] > 35:
            advisory["advice"].append("High temperature — consider mulching to conserve soil moisture.")
    except Exception as e:
        print("b")
        advisory["weather_error"] = str(e)

    # 3. Market Trends
    try:
        market = pd.read_csv(market_csv)
        # Normalize date column
        market['date'] = pd.to_datetime(market['Arrival_Date'], errors="coerce",dayfirst=True)
        market = market.sort_values("date")

        latest_price = market["Modal Price"].iloc[-1]
        prev_price = market["Modal Price"].iloc[-2] if len(market) > 1 else latest_price

        advisory["market"] = {
            "latest_price": latest_price,
            "prev_price": prev_price
        }

        if latest_price > prev_price:
            advisory["advice"].append("Market prices are rising — consider waiting before selling.")
        else:
            advisory["advice"].append("Market prices are falling — consider selling soon.")
    except Exception as e:
        print("c")
        advisory["market_error"] = str(e)

    return advisory
