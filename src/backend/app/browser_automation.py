"""Browser Automation with Playwright - Data extraction and testing."""

import asyncio
from typing import Dict, Any, Optional

class PlaywrightAutomation:
    """Advanced browser automation for financial websites."""
    
    def __init__(self):
        self.browser = None
        self.page = None
    
    async def init(self, headless: bool = True):
        from playwright.async_api import async_playwright
        self.pw = await async_playwright().start()
        self.browser = await self.pw.chromium.launch(headless=headless)
        self.page = await self.browser.new_page()
        await self.page.set_viewport_size({"width": 1920, "height": 1080})
    
    async def scrape_trading212(self) -> Dict[str, Any]:
        """Automated login and data export from Trading 212."""
        await self.page.goto("https://www.trading212.com/sign-in")
        # Note: Requires manual login or credentials
        await self.page.wait_for_selector("[data-testid='portfolio-button']", timeout=30000)
        
        # Navigate to history
        await self.page.click("[data-testid='history-tab']")
        await self.page.wait_for_load_state("networkidle")
        
        # Download CSV
        async with self.page.expect_download() as download_info:
            await self.page.click("[data-testid='export-csv']")
        download = await download_info.value
        path = await download.path()
        
        return {"download_path": str(path), "status": "success"}
    
    async def scrape_yahoo_batch(self, tickers: list) -> list:
        """Batch scrape Yahoo Finance for multiple tickers."""
        results = []
        for ticker in tickers:
            try:
                await self.page.goto(f"https://finance.yahoo.com/quote/{ticker}", timeout=10000)
                price = await self.page.locator("[data-field='regularMarketPrice']").first.text_content(timeout=5000)
                results.append({"ticker": ticker, "price": price})
            except:
                results.append({"ticker": ticker, "error": "failed"})
        return results
    
    async def test_dashboard(self, url: str = "http://localhost:5173") -> Dict[str, Any]:
        """Automated testing of React dashboard."""
        await self.page.goto(url)
        
        # Test navigation
        tests = {}
        
        # Portfolio page
        await self.page.click("text=Portfolio")
        tests["portfolio_nav"] = await self.page.locator("h1:has-text('Portfolio')").is_visible()
        
        # Tax page
        await self.page.click("text=Tax Center")
        tests["tax_nav"] = await self.page.locator("h1:has-text('Tax')").is_visible()
        
        # Agents page
        await self.page.click("text=Agents")
        tests["agents_nav"] = await self.page.locator("h1:has-text('Agents')").is_visible()
        
        return tests
    
    async def close(self):
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'pw'):
            await self.pw.stop()

class SeleniumAutomation:
    """Selenium-based automation as Playwright fallback."""
    
    def __init__(self):
        self.driver = None
    
    def init(self, headless: bool = True):
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        opts = Options()
        if headless:
            opts.add_argument("--headless")
        opts.add_argument("--window-size=1920,1080")
        self.driver = webdriver.Chrome(options=opts)
    
    def screenshot_dashboard(self, url: str = "http://localhost:5173") -> str:
        self.driver.get(url)
        filename = f"dashboard_test_{asyncio.datetime.now():%Y%m%d_%H%M%S}.png"
        self.driver.save_screenshot(filename)
        return filename
    
    def close(self):
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    print("Browser automation ready")
    print("Usage: python -c \"import asyncio; from browser_automation import PlaywrightAutomation; p = PlaywrightAutomation(); asyncio.run(p.init()); asyncio.run(p.test_dashboard())\"")
