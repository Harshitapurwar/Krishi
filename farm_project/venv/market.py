import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

# Load dataset globally
df_market = pd.read_csv("data/uttar_pradesh_data2.csv")
df_market['date'] = pd.to_datetime(df_market['Arrival_Date'], format="%d-%m-%Y", errors="coerce", dayfirst=True)


# Train models for each crop+market
market_models = {}
for (commodity, market), group in df_market.groupby(["Commodity", "Market"]):
    group = group.sort_values("Arrival_Date")
    X = (group["Arrival_Date"] - group["Arrival_Date"].min()).dt.days.values.reshape(-1, 1)
    y = group["Modal Price"].values

    model = LinearRegression()
    model.fit(X, y)

    market_models[(commodity, market)] = {
        "model": model,
        "start_date": group["Arrival_Date"].min()
    }

def predict_market(crop_type, market_name, target_date):
    """
    Predict market prices and trends for a given crop and market.
    """
    key = (crop_type, market_name)
    if key not in market_models:
        return None

    model_info = market_models[key]
    model = model_info["model"]
    start_date = model_info["start_date"]

    days_since_start = (target_date - start_date).days
    price_today = model.predict(np.array([[days_since_start]]))[0]

    # Trend slope (7 days)
    price_next = model.predict(np.array([[days_since_start + 7]]))[0]
    slope_7d = (price_next - price_today) / 7

    # Delta in 3 days
    price_3d = model.predict(np.array([[days_since_start + 3]]))[0]
    delta_3d = price_3d - price_today

    # Monthly avg
    past_month_start = target_date - timedelta(days=30)
    mask = (
        (df_market["Commodity"] == crop_type) &
        (df_market["Market"] == market_name) &
        (df_market["Arrival_Date"] >= past_month_start) &
        (df_market["Arrival_Date"] <= target_date)
    )
    month_avg = df_market.loc[mask, "Modal Price"].mean() if not df_market.loc[mask].empty else price_today
    above_month_avg = price_today > month_avg

    # Best sell window (max price in next 15 days)
    future_days = np.arange(days_since_start, days_since_start + 15).reshape(-1, 1)
    future_prices = model.predict(future_days)
    best_sell_day = int(np.argmax(future_prices))

    # Trend direction
    if slope_7d > 5:
        trend = "up"
    elif slope_7d < -5:
        trend = "down"
    else:
        trend = "stable"

    return {
        "price_today": round(float(price_today), 2),
        "price_trend": trend,
        "price_trend_slope_7d": round(float(slope_7d), 2),
        "expected_price_delta_3d": round(float(delta_3d), 2),
        "price_above_month_avg_flag": bool(above_month_avg),
        "best_sell_window_days": int(best_sell_day)
    }
