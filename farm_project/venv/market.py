import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

class MarketService:
    def __init__(self, data_file="data/final_dataset.csv"):
        """Initialize market service with dataset"""
        self.df = self._load_and_clean_data(data_file)
        self.models = {}
        self._train_models()
        
    def _load_and_clean_data(self, data_file):
        """Load and clean the market dataset"""
        try:
            df = pd.read_csv(data_file)
            
            # Convert date columns
            df['Arrival_Date'] = pd.to_datetime(df['Arrival_Date'], format='%d-%m-%Y', errors='coerce')
            
            # Clean numeric columns
            numeric_cols = ['Min Price', 'Max Price', 'Modal Price']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Drop rows with invalid dates or prices
            df = df.dropna(subset=['Arrival_Date', 'Modal Price'])
            
            return df
            
        except Exception as e:
            print(f"Error loading market data: {e}")
            return pd.DataFrame()
    
    def _train_models(self):
        """Train price prediction models for each crop-market combination"""
        try:
            # Group by commodity and market
            for (commodity, market), group in self.df.groupby(['Commodity', 'Market']):
                if len(group) < 5:  # Need at least 5 data points
                    continue
                
                # Sort by date
                group = group.sort_values('Arrival_Date')
                
                # Create features: days since first record
                start_date = group['Arrival_Date'].min()
                group['days_since_start'] = (group['Arrival_Date'] - start_date).dt.days
                
                # Prepare training data
                X = group[['days_since_start']].values
                y = group['Modal Price'].values
                
                # Train linear regression model
                model = LinearRegression()
                model.fit(X, y)
                
                # Store model and metadata
                self.models[(commodity, market)] = {
                    'model': model,
                    'start_date': start_date,
                    'min_price': group['Modal Price'].min(),
                    'max_price': group['Modal Price'].max(),
                    'avg_price': group['Modal Price'].mean(),
                    'price_volatility': group['Modal Price'].std()
                }
                
        except Exception as e:
            print(f"Error training models: {e}")
    
    def get_market_forecast(self, place_name, crop_name):
        """
        Get market forecast for a specific place and crop
        
        Args:
            place_name (str): Name of the place/market
            crop_name (str): Name of the crop/commodity
            
        Returns:
            dict: Market forecast data in the required format
        """
        try:
            # Find the best matching market and crop
            market_key = self._find_best_match(place_name, crop_name)
            
            if not market_key:
                return self._get_default_response(f"No market data found for {place_name} and {crop_name}")
            
            commodity, market = market_key
            model_info = self.models[market_key]
            
            # Get today's date
            today = datetime.now()
            
            # Calculate days since start of dataset
            days_since_start = (today - model_info['start_date']).days
            
            # Predict current price
            current_price = model_info['model'].predict([[days_since_start]])[0]
            
            # Predict price in 7 days for trend calculation
            price_7d = model_info['model'].predict([[days_since_start + 7]])[0]
            
            # Calculate trend slope (Rs/day)
            trend_slope_7d = (price_7d - current_price) / 7
            
            # Predict price in 3 days
            price_3d = model_info['model'].predict([[days_since_start + 3]])[0]
            price_delta_3d = price_3d - current_price
            
            # Determine price trend
            if trend_slope_7d > 5:
                price_trend = "up"
            elif trend_slope_7d < -5:
                price_trend = "down"
            else:
                price_trend = "stable"
            
            # Check if current price is above monthly average
            month_ago = today - timedelta(days=30)
            monthly_data = self.df[
                (self.df['Commodity'] == commodity) & 
                (self.df['Market'] == market) &
                (self.df['Arrival_Date'] >= month_ago)
            ]
            
            monthly_avg = monthly_data['Modal Price'].mean() if not monthly_data.empty else current_price
            price_above_month_avg = current_price > monthly_avg
            
            # Calculate best selling window (find max price in next 15 days)
            future_prices = []
            for i in range(15):
                future_day = days_since_start + i
                future_price = model_info['model'].predict([[future_day]])[0]
                future_prices.append(future_price)
            
            best_sell_day = np.argmax(future_prices)
            
            return {
                "price_today": round(float(current_price), 0),
                "price_trend": price_trend,
                "price_trend_slope_7d": round(float(trend_slope_7d), 1),
                "expected_price_delta_3d": round(float(price_delta_3d), 0),
                "price_above_month_avg_flag": bool(price_above_month_avg),
                "best_sell_window_days": int(best_sell_day)
            }
            
        except Exception as e:
            print(f"Error in market forecast: {e}")
            return self._get_default_response(f"Error processing market data: {str(e)}")
    
    def _find_best_match(self, place_name, crop_name):
        """Find the best matching market and crop combination"""
        # First try exact matches
        for (commodity, market) in self.models.keys():
            if (commodity.lower() == crop_name.lower() and 
                market.lower() == place_name.lower()):
                return (commodity, market)
        
        # Try partial matches
        for (commodity, market) in self.models.keys():
            if (crop_name.lower() in commodity.lower() or 
                commodity.lower() in crop_name.lower()):
                if (place_name.lower() in market.lower() or 
                    market.lower() in place_name.lower()):
                    return (commodity, market)
        
        # Return first available model if no match found
        if self.models:
            return list(self.models.keys())[0]
        
        return None
    
    def _get_default_response(self, error_msg):
        """Return default response when there's an error"""
        return {
            "price_today": 1500,
            "price_trend": "stable",
            "price_trend_slope_7d": 0.0,
            "expected_price_delta_3d": 0,
            "price_above_month_avg_flag": False,
            "best_sell_window_days": 3,
            "error": error_msg
        }
    
    def get_available_crops(self):
        """Get list of available crops in the dataset"""
        return sorted(self.df['Commodity'].unique().tolist())
    
    def get_available_markets(self):
        """Get list of available markets in the dataset"""
        return sorted(self.df['Market'].unique().tolist())

# Global instance for easy access
market_service = MarketService()

def get_market_forecast(place_name, crop_name):
    """Convenience function to get market forecast"""
    return market_service.get_market_forecast(place_name, crop_name)

if __name__ == "__main__":
    # Test the market service
    service = MarketService()
    result = service.get_market_forecast("Etawah", "Cucumbar")
    print("Market Forecast Result:")
    print(result)
    
    print("\nAvailable crops:", service.get_available_crops()[:5])
    print("Available markets:", service.get_available_markets()[:5])
