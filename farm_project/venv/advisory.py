import pandas as pd
from datetime import datetime
from weather import get_weather_forecast
from market import get_market_forecast
from satellite import get_satellite_data
class AdvisoryService:
    def __init__(self):
        """Initialize advisory service"""
        pass
    
    def generate_advisory(self, place_name, crop_name):
        """
        Generate comprehensive farming advisory based on weather and market data
        
        Args:
            place_name (str): Name of the place/district
            crop_name (str): Name of the crop
            
        Returns:
            dict: Comprehensive advisory with weather, market, and recommendations
        """
        try:
            # Initialize advisory structure
            advisory = {
                "weather": {},
                "market": {},
                "satellite": {},
            }
            
            # Get weather forecast
            weather_data = get_weather_forecast(place_name, crop_name)
            advisory["weather"] = weather_data
            
            # Get market forecast
            market_data = get_market_forecast(place_name, crop_name)
            advisory["market"] = market_data

            try:
                satellite_info = get_satellite_data(place_name)
                advisory["satellite"] = satellite_info
            except Exception as e:
                advisory["satellite_error"] = str(e)
            
            return advisory
            
        except Exception as e:
            return {
                "error": f"Error generating advisory: {str(e)}",
                "place": place_name,
                "crop": crop_name,
                "timestamp": datetime.now().isoformat()
            }
    
    def _generate_recommendations(self, weather_data, market_data):
        """Generate farming recommendations based on weather and market data"""
        recommendations = []
        
        # Weather-based recommendations
        if weather_data.get("extreme_weather_flag"):
            recommendations.append("⚠️ Extreme weather expected - take necessary precautions")
        
        harvest_window = weather_data.get("optimal_harvest_window_days", 0)
        if harvest_window >= 3:
            recommendations.append(f"✅ Good harvesting conditions expected for {harvest_window} days")
        elif harvest_window > 0:
            recommendations.append(f"⚠️ Limited harvesting window: only {harvest_window} days available")
        else:
            recommendations.append("❌ Poor harvesting conditions - consider delaying harvest")
        
        # Market-based recommendations
        price_trend = market_data.get("price_trend", "stable")
        if price_trend == "up":
            recommendations.append("📈 Market prices are rising - consider waiting before selling")
        elif price_trend == "down":
            recommendations.append("📉 Market prices are falling - consider selling soon")
        else:
            recommendations.append("➡️ Market prices are stable")
        
        best_sell_days = market_data.get("best_sell_window_days", 0)
        if best_sell_days <= 3:
            recommendations.append(f"🚀 Optimal selling window: sell within {best_sell_days} days for best prices")
        
        # Combined recommendations
        if (harvest_window > 0 and price_trend == "up"):
            recommendations.append("🎯 Perfect timing: Harvest now and wait for better prices")
        elif (harvest_window > 0 and price_trend == "down"):
            recommendations.append("⚡ Harvest now and sell quickly before prices drop further")
        
        return recommendations
    
    def _assess_risks(self, weather_data, market_data):
        """Assess risks based on weather and market conditions"""
        risks = {
            "weather_risk": "low",
            "market_risk": "low",
            "overall_risk": "low",
            "risk_factors": []
        }
        
        # Weather risk assessment
        weather_risk_score = 0
        if weather_data.get("extreme_weather_flag"):
            weather_risk_score += 3
            risks["risk_factors"].append("Extreme weather conditions")
        
        harvest_window = weather_data.get("optimal_harvest_window_days", 0)
        if harvest_window == 0:
            weather_risk_score += 2
            risks["risk_factors"].append("No suitable harvesting window")
        elif harvest_window <= 2:
            weather_risk_score += 1
            risks["risk_factors"].append("Limited harvesting time")
        
        # Market risk assessment
        market_risk_score = 0
        price_trend = market_data.get("price_trend", "stable")
        if price_trend == "down":
            market_risk_score += 2
            risks["risk_factors"].append("Declining market prices")
        
        price_delta = market_data.get("expected_price_delta_3d", 0)
        if price_delta < -100:
            market_risk_score += 1
            risks["risk_factors"].append("Significant price drop expected")
        
        # Overall risk assessment
        total_risk = weather_risk_score + market_risk_score
        
        if total_risk >= 4:
            risks["overall_risk"] = "high"
        elif total_risk >= 2:
            risks["overall_risk"] = "medium"
        else:
            risks["overall_risk"] = "low"
        
        # Set individual risk levels
        risks["weather_risk"] = "high" if weather_risk_score >= 2 else "medium" if weather_risk_score >= 1 else "low"
        risks["market_risk"] = "high" if market_risk_score >= 2 else "medium" if market_risk_score >= 1 else "low"
        
        return risks
    
    def _generate_action_items(self, weather_data, market_data, recommendations):
        """Generate specific action items for farmers"""
        actions = []
        
        # Immediate actions based on weather
        if weather_data.get("extreme_weather_flag"):
            actions.append("🔒 Secure crops and equipment immediately")
            actions.append("📱 Monitor weather alerts and updates")
        
        # Harvest timing actions
        harvest_window = weather_data.get("optimal_harvest_window_days", 0)
        if harvest_window > 0:
            actions.append(f"🌾 Plan harvest within next {harvest_window} days")
        else:
            actions.append("⏳ Delay harvest until weather improves")
        
        # Market timing actions
        best_sell_days = market_data.get("best_sell_window_days", 0)
        if best_sell_days <= 3:
            actions.append(f"💰 Prepare to sell within {best_sell_days} days for optimal prices")
        
        # Price monitoring actions
        if market_data.get("price_trend") == "up":
            actions.append("📊 Monitor price trends daily")
        elif market_data.get("price_trend") == "down":
            actions.append("⚡ Consider immediate sale to minimize losses")
        
        # General actions
        actions.append("📈 Track both weather and market conditions daily")
        actions.append("🤝 Consult local agricultural experts for specific advice")
        
        return actions
    
    def get_summary(self, advisory):
        """Generate a summary of the advisory"""
        summary = {
            "place": advisory.get("place"),
            "crop": advisory.get("crop"),
            "overall_risk": advisory.get("risk_assessment", {}).get("overall_risk", "unknown"),
            "key_recommendation": advisory.get("recommendations", [""])[0] if advisory.get("recommendations") else "No recommendations available",
            "harvest_window": advisory.get("weather", {}).get("optimal_harvest_window_days", 0),
            "price_trend": advisory.get("market", {}).get("price_trend", "unknown"),
            "best_sell_timing": advisory.get("market", {}).get("best_sell_window_days", 0)
        }
        
        return summary

# Global instance for easy access
advisory_service = AdvisoryService()

def generate_advisory(place_name, crop_name):
    """Convenience function to generate advisory"""
    return advisory_service.generate_advisory(place_name, crop_name)

if __name__ == "__main__":
    # Test the advisory service
    service = AdvisoryService()
    result = service.generate_advisory("Etawah", "Cucumbar")
    
    print("=== FARMING ADVISORY ===")
    print(f"Place: {result['place']}")
    print(f"Crop: {result['crop']}")
    print(f"Timestamp: {result['timestamp']}")
    
    print("\n=== WEATHER DATA ===")
    for key, value in result['weather'].items():
        print(f"{key}: {value}")
    
    print("\n=== MARKET DATA ===")
    for key, value in result['market'].items():
        print(f"{key}: {value}")
    
    print("\n=== RECOMMENDATIONS ===")
    for rec in result['recommendations']:
        print(f"• {rec}")
    
    print("\n=== RISK ASSESSMENT ===")
    for key, value in result['risk_assessment'].items():
        print(f"{key}: {value}")
    
    print("\n=== ACTION ITEMS ===")
    for action in result['action_items']:
        print(f"• {action}")
    
    print("\n=== SUMMARY ===")
    summary = service.get_summary(result)
    for key, value in summary.items():
        print(f"{key}: {value}")
