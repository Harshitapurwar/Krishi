import pandas as pd

class SatelliteService:
    def __init__(self, path="data/satellite_data.csv"):
        self.data = pd.read_csv(path)

    def get_crop_health(self, region):
        return self.data[self.data["region"] == region]
