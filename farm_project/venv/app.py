from flask import Flask, request, jsonify
from flask_cors import CORS
from advisory import generate_advisory
from weather import get_weather_forecast
from market import get_market_forecast
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route("/", methods=["GET"])
def home():
    """Home endpoint with API information"""
    return jsonify({
        "message": "Krishi - Smart Farming Advisory API",
        "version": "1.0.0",
        "endpoints": {
            "/advisory": "POST - Get comprehensive farming advisory",
            "/weather": "POST - Get weather forecast",
            "/market": "POST - Get market forecast",
            "/health": "GET - API health check"
        },
        "usage": {
            "input_format": {
                "place_name": "string (e.g., 'Etawah', 'Agra')",
                "crop_name": "string (e.g., 'Cucumbar', 'Wheat')"
            },
            "example": {
                "place_name": "Etawah",
                "crop_name": "Cucumbar"
            }
        }
    })

@app.route("/advisory", methods=["POST"])
def advisory_endpoint():
    """
    Main advisory endpoint that provides comprehensive farming advice
    combining weather and market data
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        place_name = data.get("place_name")
        crop_name = data.get("crop_name")
        
        if not place_name or not crop_name:
            return jsonify({
                "error": "Missing required parameters",
                "required": ["place_name", "crop_name"],
                "received": list(data.keys()) if data else []
            }), 400
        
        # Generate comprehensive advisory
        result = generate_advisory(place_name, crop_name)
        
        if "error" in result:
            return jsonify(result), 500
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "place_name": place_name if 'place_name' in locals() else None,
            "crop_name": crop_name if 'crop_name' in locals() else None
        }), 500

@app.route("/weather", methods=["POST"])
def weather_endpoint():
    """
    Weather forecast endpoint that provides weather data for the next 7 days
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        place_name = data.get("place_name")
        crop_name = data.get("crop_name")
        
        if not place_name or not crop_name:
            return jsonify({
                "error": "Missing required parameters",
                "required": ["place_name", "crop_name"],
                "received": list(data.keys()) if data else []
            }), 400
        
        # Get weather forecast
        result = get_weather_forecast(place_name, crop_name)
        
        if "error" in result:
            return jsonify(result), 500
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "place_name": place_name if 'place_name' in locals() else None,
            "crop_name": crop_name if 'crop_name' in locals() else None
        }), 500

@app.route("/market", methods=["POST"])
def market_endpoint():
    """
    Market forecast endpoint that provides price predictions and trends
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        place_name = data.get("place_name")
        crop_name = data.get("crop_name")
        
        if not place_name or not crop_name:
            return jsonify({
                "error": "Missing required parameters",
                "required": ["place_name", "crop_name"],
                "received": list(data.keys()) if data else []
            }), 400
        
        # Get market forecast
        result = get_market_forecast(place_name, crop_name)
        
        if "error" in result:
            return jsonify(result), 500
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "place_name": place_name if 'place_name' in locals() else None,
            "crop_name": crop_name if 'crop_name' in locals() else None
        }), 500

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "service": "Krishi API"
    })

@app.route("/test", methods=["GET"])
def test_endpoint():
    """Test endpoint with sample data"""
    sample_data = {
        "place_name": "Etawah",
        "crop_name": "Cucumbar"
    }
    
    return jsonify({
        "message": "Test endpoint - use this data to test other endpoints",
        "sample_request": {
            "endpoint": "/advisory",
            "method": "POST",
            "data": sample_data
        },
        "curl_example": f"curl -X POST http://localhost:5000/advisory -H 'Content-Type: application/json' -d '{json.dumps(sample_data)}'"
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": [
            "/",
            "/advisory",
            "/weather", 
            "/market",
            "/health",
            "/test"
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        "error": "Internal server error",
        "message": "Something went wrong on our end. Please try again later."
    }), 500

if __name__ == "__main__":
    print("🚀 Starting Krishi - Smart Farming Advisory API...")
    print("📖 API Documentation available at: http://localhost:5000/")
    print("🧪 Test endpoint available at: http://localhost:5000/test")
    print("🔧 Health check available at: http://localhost:5000/health")
    print("\n📝 Example usage:")
    print("POST /advisory with: {\"place_name\": \"Etawah\", \"crop_name\": \"Cucumbar\"}")
    
    app.run(debug=True, host="0.0.0.0", port=5000)
