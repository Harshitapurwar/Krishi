import pandas as pd
import numpy as np
import ee
from satellite import get_satellite_data
from weather import compute_weather_data, df as weather_df
from market import predict_market, df_market

def generate_advisory(place_name, crop_name, weather_csv, market_csv):
    advisory = {"place": place_name, "crop": crop_name, "advice": []}

    # 1. Satellite NDVI
    try:
        satellite_info = get_satellite_data(place_name)
        advisory["satellite"] = satellite_info
    except Exception as e:
        advisory["satellite_error"] = str(e)

    # 2. Weather Forecast (use compute_weather_data)
    try:
        # Use today's date for forecast
        today = pd.Timestamp.today().strftime("%Y-%m-%d")
        weather_result = compute_weather_data(
            region=place_name,
            date=today,
            crop_type=crop_name,
            data=weather_df
        )
        if weather_result is not None:
            advisory["weather"] = weather_result
            if weather_result.get("extreme_weather_flag"):
                advisory["advice"].append("Extreme weather expected — take precautions.")
            if weather_result.get("optimal_harvest_window_days", 0) == 0:
                advisory["advice"].append("No optimal harvest window in next 7 days.")
        else:
            advisory["weather_error"] = f"No weather data found for {place_name}"
    except Exception as e:
        advisory["weather_error"] = str(e)

    # 3. Market Trends (use predict_market)
    try:
        # Use today's date for market prediction
        from datetime import datetime
        today = datetime.today()
        # Try to find a matching market for the place_name
        # Use the first matching market if multiple
        possible_markets = df_market[df_market["district"].str.lower() == place_name.lower()]["Market"].unique()
        market_name = possible_markets[0] if len(possible_markets) > 0 else None
        if market_name is None:
            # fallback: use any market
            market_name = df_market["Market"].iloc[0]
        market_result = predict_market(
            crop_type=crop_name,
            market_name=market_name,
            target_date=today
        )
        if market_result is not None:
            advisory["market"] = market_result
            if market_result.get("price_trend") == "up":
                advisory["advice"].append("Market prices are rising — consider waiting before selling.")
            elif market_result.get("price_trend") == "down":
                advisory["advice"].append("Market prices are falling — consider selling soon.")
            else:
                advisory["advice"].append("Market prices are stable.")
        else:
            advisory["market_error"] = f"No market data found for {place_name}"
    except Exception as e:
        advisory["market_error"] = str(e)

    return advisory
