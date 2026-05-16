"""Financial Data Scraper using Autonomous Browser."""

import asyncio
from datetime import datetime
from autonomous_browser import AutonomousBrowser, ScrapingTask

class YahooFinanceScraper:
    def __init__(self):
        self.browser = None
    
    async def init(self, headless=True):
        self.browser = AutonomousBrowser(headless=headless)
        await self.browser.init()
    
    async def get_quote(self, ticker: str):
        """Get stock price with pagination support."""
        task = ScrapingTask(
            url=f"https://finance.yahoo.com/quote/{ticker}",
            goal=f"Get {ticker} price",
            selectors={
                "price": f"[data-symbol='{ticker}'][data-field='regularMarketPrice']",
                "change": f"[data-symbol='{ticker}'][data-field='regularMarketChange']"
            },
            max_pages=1
        )
        result = await self.browser.scrape_with_pagination(task)
        return result.data[0] if result.data else None
    
    async def get_news(self, ticker: str, pages: int = 3):
        """Get news with pagination."""
        task = ScrapingTask(
            url=f"https://finance.yahoo.com/quote/{ticker}/news",
            goal="Get news articles",
            selectors={"headlines": "h3", "summaries": "p"},
            max_pages=pages,
            scroll_to_bottom=True
        )
        return await self.browser.scrape_with_pagination(task)
    
    async def close(self):
        if self.browser:
            await self.browser.close()

async def example():
    scraper = YahooFinanceScraper()
    await scraper.init(headless=False)
    
    # Get quote
    quote = await scraper.get_quote("AAPL")
    print(f"Quote: {quote}")
    
    # Get news (with pagination!)
    news = await scraper.get_news("AAPL", pages=3)
    print(f"Scraped {news.pages_scraped} pages")
    
    await scraper.close()

if __name__ == "__main__":
    asyncio.run(example())
