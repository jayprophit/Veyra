"""Web Scraper - Alternative data from web sources"""
from typing import Dict

class WebScraper:
    """Scrape web data for investment signals"""
    
    def job_listing_tracker(self, company: str, job_count: int, job_change: float) -> Dict:
        return {"company": company, "jobs": job_count, "change": job_change, "signal": "expansion" if job_change > 20 else "contraction" if job_change < -20 else "stable"}
    
    def product_review_sentiment(self, avg_rating: float, review_count: int) -> Dict:
        return {"rating": avg_rating, "reviews": review_count, "sentiment": "positive" if avg_rating > 4 else "negative" if avg_rating < 3 else "neutral"}
