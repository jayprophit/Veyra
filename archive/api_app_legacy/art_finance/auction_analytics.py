"""Auction Analytics"""
class AuctionAnalytics:
    def hammer_analysis(self, low: float, high: float, hammer: float) -> dict:
        ratio = hammer / high if high > 0 else 0
        return {"sell_through": ratio > 0.8, "premium": ratio > 1.0}
