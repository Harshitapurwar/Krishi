# satellite.py
import ee
import geemap
import numpy as np
import matplotlib.pyplot as plt
import requests
ee.Authenticate()
ee.Initialize(project="python-425801")

def get_satellite_data(place_name):
    # Get coordinates
    if place_name.strip() == "":
        try:
            response = requests.get("https://ipinfo.io/json").json()
            loc = response["loc"].split(",")
            lat, lon = float(loc[0]), float(loc[1])
        except:
            raise Exception("Could not fetch live location. Please enter manually.")
    else:
        geocode_results = geemap.geocode(place_name)
        if len(geocode_results) == 0:
            raise Exception("Place not found! Try a different name.")
        first_result = geocode_results[0]
        lon, lat = first_result.geometry['coordinates']

    point = ee.Geometry.Point([lon, lat])
    region = point.buffer(5000)

    # Load Sentinel-2 collection
    collection = (ee.ImageCollection('COPERNICUS/S2_SR')
                  .filterBounds(region)
                  .filterDate('2025-01-01', '2025-08-24')
                  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10))
                  .sort('CLOUDY_PIXEL_PERCENTAGE'))
    image = collection.first()
    if image is None:
        raise Exception("No suitable Sentinel-2 images found for this region and date range.")

    # NDVI
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    ndvi_map = geemap.ee_to_numpy(ndvi, region)
    ndvi_map = np.ma.masked_invalid(ndvi_map)

    # Crop parameters
    ndvi_min = float(np.nanmin(ndvi_map))
    ndvi_max = float(np.nanmax(ndvi_map))
    ndvi_mean = float(np.nanmean(ndvi_map))
    crop_health_index = (ndvi_mean - ndvi_min) / (ndvi_max - ndvi_min + 1e-6)
    ripeness_percent = int((1 - crop_health_index) * 100)
    unhealthy_area_percent = int((np.sum(ndvi_map < 0.3) / ndvi_map.size) * 100)
    expected_days_to_ripeness = int((1 - ripeness_percent / 100) * 20)

    # Optional: plot NDVI
    # plt.figure(figsize=(8, 6))
    # plt.imshow(ndvi_map, cmap='RdYlGn')
    # plt.colorbar(label='NDVI')
    # plt.title(f'NDVI Map of {place_name}')
    # plt.show()

    return {
        "crop_health_index": round(crop_health_index, 2),
        "ripeness_percent": ripeness_percent,
        "unhealthy_area_percent": unhealthy_area_percent,
        "expected_days_to_ripeness": expected_days_to_ripeness
    }

# Test
if __name__ == "__main__":
    result = get_satellite_data("")
    import json
    print(json.dumps(result, indent=2))
