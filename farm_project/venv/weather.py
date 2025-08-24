from flask import Flask, request, jsonify
import pandas as pd
import numpy as np

app = Flask(__name__)

DATA_FILE = "data/weather_forecast.csv"  # your cleaned CSV path

# Load & normalize
df = pd.read_csv(DATA_FILE)
# normalize column names (should already match, but safe)
df.rename(columns=lambda x: x.strip().lower().replace(" ", "_"), inplace=True)

# Map expected names (CSV uses forecast_date, rainfall_mm, temp_max_degC, etc.)
# Ensure required columns exist
REQUIRED = [
    "forecast_date", "district", "block", "rainfall_mm",
    "temp_max_degc", "temp_min_degc",
    "humidity_morning_pct", "humidity_evening_pct",
    "wind_speed_kmph", "wind_direction_deg", "cloud_cover_octa", "warning"
]
missing = [c for c in REQUIRED if c not in df.columns]
if missing:
    raise RuntimeError(f"Missing expected columns in {DATA_FILE}: {missing}")

# Convert types & clean strings
def clean_df(df):
    d = df.copy()
    # parse dates
    d["forecast_date"] = pd.to_datetime(d["forecast_date"], errors="coerce")
    # numeric conversions (coerce invalid to NaN)
    numcols = ["rainfall_mm", "temp_max_degc", "temp_min_degc",
               "humidity_morning_pct", "humidity_evening_pct",
               "wind_speed_kmph", "wind_direction_deg", "cloud_cover_octa"]
    for c in numcols:
        # remove commas / stray characters and convert
        d[c] = (d[c].astype(str)
                 .str.replace(",", "")
                 .str.replace("â€”", "")
                 .str.replace("Nil", "")
                 .str.strip()
                 .replace("", np.nan))
        d[c] = pd.to_numeric(d[c], errors="coerce")
    # normalize warning text
    d["warning"] = d["warning"].astype(str).replace("nan", "").str.strip()
    return d

df = clean_df(df)

# Crop thresholds (same as your earlier dict)
CROP_THRESHOLDS = {
    "rice": {"flood_mm": 150, "storm_wind": 80},
    "wheat": {"flood_mm": 100, "storm_wind": 70},
    "cotton": {"flood_mm": 80, "storm_wind": 60},
    "default": {"flood_mm": 120, "storm_wind": 75}
}


def compute_weather_data(region: str, date: str, crop_type: str, data: pd.DataFrame):
    """
    region: matches district or block (case-insensitive)
    date: YYYY-MM-DD (observation start)
    crop_type: used to pick thresholds
    Returns a dict with rain_forecast_next_7d, avg_temp_next_7d,
    extreme_weather_flag, optimal_harvest_window_days,
    plus rain_72h_mm, storm_window_days, flood_risk_flag
    """
    thresholds = CROP_THRESHOLDS.get(crop_type.lower(), CROP_THRESHOLDS["default"])

    try:
        obs_date = pd.to_datetime(date).normalize()
    except Exception:
        return None

    # Filter by region â€” match district OR block (case-insensitive)
    mask_region = (
        (data["district"].astype(str).str.lower() == region.lower()) |
        (data["block"].astype(str).str.lower() == region.lower())
    )
    subset = data[mask_region].copy()
    if subset.empty:
        return None

    # Focus on next 7 days from obs_date (daily rows)
    end_7 = obs_date + pd.Timedelta(days=7)
    window7 = subset[(subset["forecast_date"] >= obs_date) & (subset["forecast_date"] < end_7)]
    if window7.empty:
        return None

    # --- rain forecast next 7d (list of floats, days in chronological order) ---
    # group by date in case there are duplicates
    rf = (window7.groupby("forecast_date")["rainfall_mm"].sum()
                 .reindex(pd.date_range(obs_date, obs_date + pd.Timedelta(days=6), freq="D"), fill_value=0))
    rain_forecast_next_7d = [float(x) if not pd.isna(x) else 0.0 for x in rf.tolist()]

    # --- average temp next 7d: use mean of (max+min)/2 ---
    temps = window7.copy()
    temps["temp_mean"] = temps[["temp_max_degc", "temp_min_degc"]].mean(axis=1)
    avg_temp_next_7d = float(round(temps["temp_mean"].mean(), 2))

    # --- rain_72h = sum of rainfall over next 72h (daily -> sum of next 3 days) ---
    end_72 = obs_date + pd.Timedelta(days=3)
    window72 = subset[(subset["forecast_date"] >= obs_date) & (subset["forecast_date"] < end_72)]
    rain_72h_mm = float(window72["rainfall_mm"].sum())

    # --- storm window days (dates in next 72h where wind >= threshold) ---
    storm_days = (window72[window72["wind_speed_kmph"] >= thresholds["storm_wind"]]
                  ["forecast_date"].dt.strftime("%Y-%m-%d").unique().tolist())

    # --- flood risk flag: rainfall threshold OR warnings mentioning flood/heavy-rain ---
    flood_by_rain = rain_72h_mm >= thresholds["flood_mm"]
    warn_texts = " ".join(window72["warning"].dropna().astype(str).values).lower()
    flood_by_warn = ("flood" in warn_texts) or ("heavy-rain" in warn_texts) or ("heavy rain" in warn_texts)
    flood_risk_flag = bool(flood_by_rain or flood_by_warn)

    # --- extreme weather flag (either flood risk or storm days exist) ---
    extreme_weather_flag = bool(flood_risk_flag or len(storm_days) > 0)

    # --- optimal harvest window days: days in next 7 with low rain and low wind
    safe_mask = ( (rf < 10) &  # rainfall < 10 mm considered safe for harvesting
                  (window7.groupby("forecast_date")["wind_speed_kmph"].max().reindex(rf.index, fill_value=0) < thresholds["storm_wind"]) )
    optimal_harvest_window_days = int(safe_mask.sum())

    # Final output
    return {
        "rain_forecast_next_7d": [round(x, 2) for x in rain_forecast_next_7d],
        "avg_temp_next_7d": round(avg_temp_next_7d, 2),
        "extreme_weather_flag": bool(extreme_weather_flag),
        "optimal_harvest_window_days": int(optimal_harvest_window_days),
        # additional fields
        "rain_72h_mm": round(rain_72h_mm, 2),
        "storm_window_days": storm_days,
        "flood_risk_flag": bool(flood_risk_flag)
    }


@app.route('/weather-data', methods=['GET'])
def weather_data():
    region = request.args.get("region")
    date = request.args.get("date")
    crop_type = request.args.get("crop_type")

    if not region or not date or not crop_type:
        return jsonify({"error": "Please provide region, date, and crop_type"}), 400

    result = compute_weather_data(region, date, crop_type, df)
    if result is None:
        return jsonify({
            "error": "No data found for that region/date",
            "valid_districts": sorted(df['district'].dropna().astype(str).unique().tolist())[:50],
            "valid_blocks_sample": sorted(df['block'].dropna().astype(str).unique().tolist())[:50]
        }), 404

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)