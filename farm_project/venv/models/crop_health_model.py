class CropHealthModel:
    def predict_action(self, crop_health, ripeness, weather):
        if crop_health < 0.5:
            return "Apply pesticide immediately"
        elif ripeness >= 70 and weather["rainfall_mm"].values[0] > 40:
            return "Harvest early due to heavy rain forecast"
        else:
            return "Crop is healthy, wait for better ripening"
