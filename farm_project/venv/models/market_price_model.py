class MarketPriceModel:
    def predict_sell_time(self, price, demand):
        if demand.values[0] == "High" and price.values[0] > 1800:
            return "Sell now for maximum profit"
        else:
            return "Wait for demand/price increase"
