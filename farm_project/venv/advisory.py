import pandas as pd
import numpy as np
from satellite import get_satellite_data

def generate_advisory(place_name, crop_name, weather_csv, market_csv):
    advisory = {"place": place_name, "crop": crop_name, "advice": []}

    # 1. Satellite NDVI
    try:
        satellite_info = get_satellite_data(place_name)
        advisory["satellite"] = satellite_info
    except Exception as e:
        advisory["satellite_error"] = str(e)

    # 2. Weather Forecast
    try:
        weather = pd.read_csv(weather_csv)
        weather['forecast_date'] = pd.to_datetime(weather['forecast_date'], errors="coerce")
        weather = weather.sort_values("forecast_date")

        latest_weather = weather.iloc[-1].to_dict()
        latest_weather = {k: (float(v) if isinstance(v, (np.float32, np.float64)) 
                              else int(v) if isinstance(v, (np.int32, np.int64)) 
                              else v)
                          for k, v in latest_weather.items()}
        advisory["weather"] = latest_weather

        if latest_weather.get("rainfall_mm", 0) > 20:
            advisory["advice"].append("Heavy rainfall expected — avoid irrigation.")
        else:
            advisory["advice"].append("No heavy rain — irrigation can be planned.")
        
        if latest_weather.get("temp_max_degC", 0) > 35:
            advisory["advice"].append("High temperature — consider mulching to conserve soil moisture.")
    except Exception as e:
        advisory["weather_error"] = str(e)

    # 3. Market Trends
    try:
        market = pd.read_csv(market_csv)
        market['date'] = pd.to_datetime(market['Arrival_Date'], errors="coerce", dayfirst=True)
        market = market.sort_values("date")

        latest_price = float(market["Modal Price"].iloc[-1])
        prev_price = float(market["Modal Price"].iloc[-2]) if len(market) > 1 else latest_price

        advisory["market"] = {
            "latest_price": latest_price,
            "prev_price": prev_price
        }

        if latest_price > prev_price:
            advisory["advice"].append("Market prices are rising — consider waiting before selling.")
        else:
            advisory["advice"].append("Market prices are falling — consider selling soon.")
    except Exception as e:
        advisory["market_error"] = str(e)

    return advisory
