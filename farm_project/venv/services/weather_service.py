import pandas as pd

class WeatherService:
    def __init__(self, path="data/weather_data.csv"):
        self.data = pd.read_csv(path)

    def get_weather(self, region):
        return self.data[self.data["region"] == region]
