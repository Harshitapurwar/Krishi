import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class WeatherService:
    def __init__(self, data_file="data/final_dataset.csv"):
        """Initialize weather service with dataset"""
        self.df = self._load_and_clean_data(data_file)
        
    def _load_and_clean_data(self, data_file):
        """Load and clean the weather dataset"""
        try:
            df = pd.read_csv(data_file)
            
            # Convert date columns
            df['Arrival_Date'] = pd.to_datetime(df['Arrival_Date'], format='%d-%m-%Y', errors='coerce')
            
            # Clean numeric columns
            numeric_cols = ['rainfall_mm', 'temp_max_degC', 'temp_min_degC', 
                           'humidity_morning_pct', 'humidity_evening_pct',
                           'wind_speed_kmph', 'wind_direction_deg', 'cloud_cover_octa']
            
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Drop rows with invalid dates
            df = df.dropna(subset=['Arrival_Date'])
            
            return df
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame()
    
    def get_weather_forecast(self, place_name, crop_name):
        """
        Get weather forecast for the next 7 days for a specific place and crop
        
        Args:
            place_name (str): Name of the place/district
            crop_name (str): Name of the crop
            
        Returns:
            dict: Weather forecast data in the required format
        """
        try:
            # Filter data by place (case-insensitive)
            place_mask = (
                (self.df['District'].astype(str).str.lower() == place_name.lower()) |
                (self.df['Market'].astype(str).str.lower() == place_name.lower())
            )
            
            place_data = self.df[place_mask].copy()
            
            if place_data.empty:
                return self._get_default_response(f"No data found for place: {place_name}")
            
            # Get today's date and next 7 days
            today = datetime.now().date()
            next_7_days = [today + timedelta(days=i) for i in range(7)]
            
            # Get weather data for next 7 days
            weather_forecast = []
            temperatures = []
            extreme_weather_days = 0
            
            for day in next_7_days:
                # Find closest date in our dataset
                day_data = place_data[place_data['Arrival_Date'].dt.date == day]
                
                if not day_data.empty:
                    # Use actual data if available
                    rainfall = day_data['rainfall_mm'].iloc[0] if not pd.isna(day_data['rainfall_mm'].iloc[0]) else 0
                    temp_max = day_data['temp_max_degC'].iloc[0] if not pd.isna(day_data['temp_max_degC'].iloc[0]) else 30
                    temp_min = day_data['temp_min_degC'].iloc[0] if not pd.isna(day_data['temp_min_degC'].iloc[0]) else 20
                    wind_speed = day_data['wind_speed_kmph'].iloc[0] if not pd.isna(day_data['wind_speed_kmph'].iloc[0]) else 5
                    warning = day_data['warning'].iloc[0] if not pd.isna(day_data['warning'].iloc[0]) else 'Nil'
                    
                    # Check for extreme weather
                    is_extreme = (
                        rainfall > 50 or  # Heavy rainfall
                        wind_speed > 40 or  # High wind speed
                        warning in ['HEAVY-RAIN', 'THUNDERSTORM', 'STORM']
                    )
                    
                    if is_extreme:
                        extreme_weather_days += 1
                    
                    weather_forecast.append(round(rainfall, 1))
                    temperatures.append((temp_max + temp_min) / 2)
                    
                else:
                    # Generate synthetic data based on historical patterns
                    avg_rainfall = place_data['rainfall_mm'].mean()
                    avg_temp = (place_data['temp_max_degC'].mean() + place_data['temp_min_degC'].mean()) / 2
                    
                    # Add some randomness
                    rainfall = max(0, np.random.normal(avg_rainfall, 5))
                    temp = np.random.normal(avg_temp, 3)
                    
                    weather_forecast.append(round(rainfall, 1))
                    temperatures.append(temp)
            
            # Calculate optimal harvest window (days with low rainfall and moderate temperature)
            harvest_window = 0
            for i, (rain, temp) in enumerate(zip(weather_forecast, temperatures)):
                if rain < 10 and 15 <= temp <= 35:  # Good conditions for harvesting
                    harvest_window += 1
            
            # Determine extreme weather flag
            extreme_weather_flag = extreme_weather_days > 0
            
            return {
                "rain_forecast_next_7d": weather_forecast,
                "avg_temp_next_7d": round(np.mean(temperatures), 1),
                "extreme_weather_flag": extreme_weather_flag,
                "optimal_harvest_window_days": harvest_window
            }
            
        except Exception as e:
            print(f"Error in weather forecast: {e}")
            return self._get_default_response(f"Error processing weather data: {str(e)}")
    
    def _get_default_response(self, error_msg):
        """Return default response when there's an error"""
        return {
            "rain_forecast_next_7d": [0, 0, 0, 0, 0, 0, 0],
            "avg_temp_next_7d": 30.0,
            "extreme_weather_flag": False,
            "optimal_harvest_window_days": 3,
            "error": error_msg
        }

# Global instance for easy access
weather_service = WeatherService()

def get_weather_forecast(place_name, crop_name):
    """Convenience function to get weather forecast"""
    return weather_service.get_weather_forecast(place_name, crop_name)

if __name__ == "__main__":
    # Test the weather service
    service = WeatherService()
    result = service.get_weather_forecast("Etawah", "Cucumbar")
    print("Weather Forecast Result:")
    print(result)