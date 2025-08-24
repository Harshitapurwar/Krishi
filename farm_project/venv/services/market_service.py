import pandas as pd

class MarketService:
    def __init__(self, path="data/market_data.csv"):
        self.data = pd.read_csv(path)

    def get_market_trends(self, crop_type, region):
        return self.data[(self.data["crop_type"] == crop_type) & (self.data["region"] == region)]
