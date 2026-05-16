"""Autonomous Web Browser - AI-driven web automation with pagination.

Features:
- Autonomous navigation with LLM guidance
- Multi-page scraping with pagination
- Form filling and submission
- Screenshot documentation
- JavaScript execution
- Rate limiting and anti-detection
"""

import asyncio
import time
import random
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('AutonomousBrowser')

@dataclass
class ScrapingTask:
    """Task definition for autonomous scraping."""
    url: str
    goal: str
    selectors: Dict[str, str] = field(default_factory=dict)
    max_pages: int = 1
    scroll_to_bottom: bool = True
    wait_for: Optional[str] = None
    extract_images: bool = False
    download_files: bool = False

@dataclass
class ScrapedData:
    """Result of scraping operation."""
    url: str
    data: List[Dict[str, Any]]
    screenshots: List[str]
    pages_scraped: int
    timestamp: datetime
    errors: List[str] = field(default_factory=list)

class AutonomousBrowser:
    """
    AI-driven autonomous browser with pagination support.
    Uses Playwright for modern async browser control.
    """
    
    def __init__(self, headless: bool = True, slow_mo: int = 0):
        self.headless = headless
        self.slow_mo = slow_mo
        self.browser = None
        self.context = None
        self.page = None
        self.llm = None  # Will be set for AI guidance
        self.session_data: List[Dict] = []
    
    async def init(self):
        """Initialize browser with stealth mode."""
        from playwright.async_api import async_playwright
        
        self.pw = await async_playwright().start()
        
        # Launch with stealth settings
        self.browser = await self.pw.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process'
            ]
        )
        
        # Create context with realistic viewport and user agent
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-GB',
            timezone_id='Europe/London'
        )
        
        # Inject stealth script
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            window.chrome = { runtime: {} };
        """)
        
        self.page = await self.context.new_page()
        logger.info("✓ Autonomous browser initialized")
    
    async def navigate(self, url: str, wait_for: str = "networkidle"):
        """Navigate to URL and wait for load."""
        try:
            await self.page.goto(url, wait_until=wait_for, timeout=30000)
            logger.info(f"✓ Navigated to: {url}")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to navigate: {url} - {e}")
            return False
    
    async def scroll_page(self, direction: str = "down", amount: int = None):
        """Scroll page with human-like behavior."""
        if not amount:
            amount = random.randint(300, 800)
        
        if direction == "down":
            await self.page.mouse.wheel(0, amount)
        else:
            await self.page.mouse.wheel(0, -amount)
        
        # Random pause
        await asyncio.sleep(random.uniform(0.5, 2.0))
    
    async def scroll_to_bottom(self):
        """Scroll to bottom of page with incremental scrolling."""
        last_height = await self.page.evaluate("document.body.scrollHeight")
        
        while True:
            await self.scroll_page("down", random.randint(500, 1000))
            
            new_height = await self.page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            
            # Small random delay
            await asyncio.sleep(random.uniform(0.3, 1.0))
        
        logger.info("✓ Scrolled to bottom")
    
    async def find_pagination(self) -> Optional[str]:
        """Find pagination elements (Next, Load More, etc.)."""
        selectors = [
            "a:has-text('Next')",
            "a:has-text('next')",
            "button:has-text('Load more')",
            "button:has-text('Show more')",
            "[aria-label='Next']",
            "[rel='next']",
            ".pagination-next",
            ".next",
            "#next",
            "[class*='pagination'] a:last-child",
            "[class*='pager'] a:last-child"
        ]
        
        for selector in selectors:
            try:
                element = await self.page.locator(selector).first
                if await element.is_visible(timeout=1000):
                    return selector
            except:
                continue
        
        return None
    
    async def click_next_page(self) -> bool:
        """Click next page button and wait for content."""
        selector = await self.find_pagination()
        
        if not selector:
            return False
        
        try:
            # Scroll to pagination element
            await self.page.locator(selector).scroll_into_view_if_needed()
            
            # Click with random delay
            await asyncio.sleep(random.uniform(0.5, 1.5))
            await self.page.click(selector)
            
            # Wait for new content to load
            await asyncio.sleep(random.uniform(2, 4))
            
            logger.info("✓ Navigated to next page")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to click next: {e}")
            return False
    
    async def extract_data(self, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Extract data using CSS selectors."""
        data = {}
        
        for key, selector in selectors.items():
            try:
                elements = await self.page.locator(selector).all()
                
                if len(elements) == 1:
                    text = await elements[0].text_content()
                    data[key] = text.strip() if text else None
                else:
                    texts = []
                    for el in elements:
                        text = await el.text_content()
                        if text:
                            texts.append(text.strip())
                    data[key] = texts
                    
            except Exception as e:
                logger.warning(f"Failed to extract {key}: {e}")
                data[key] = None
        
        return data
    
    async def scrape_with_pagination(
        self,
        task: ScrapingTask,
        progress_callback: Callable[[int, int], None] = None
    ) -> ScrapedData:
        """
        Scrape data across multiple pages with pagination.
        
        Args:
            task: Scraping task definition
            progress_callback: Called with (current_page, total_pages)
        
        Returns:
            ScrapedData with all pages combined
        """
        all_data = []
        screenshots = []
        errors = []
        
        # Navigate to initial page
        if not await self.navigate(task.url):
            return ScrapedData(
                url=task.url,
                data=[],
                screenshots=[],
                pages_scraped=0,
                timestamp=datetime.now(),
                errors=["Failed to navigate to initial page"]
            )
        
        for page_num in range(1, task.max_pages + 1):
            logger.info(f"Scraping page {page_num}/{task.max_pages}")
            
            if progress_callback:
                progress_callback(page_num, task.max_pages)
            
            # Scroll if requested
            if task.scroll_to_bottom:
                await self.scroll_to_bottom()
            
            # Wait for specific element if requested
            if task.wait_for:
                try:
                    await self.page.wait_for_selector(task.wait_for, timeout=10000)
                except:
                    errors.append(f"Timeout waiting for {task.wait_for} on page {page_num}")
            
            # Extract data
            page_data = await self.extract_data(task.selectors)
            page_data['_page'] = page_num
            page_data['_url'] = self.page.url
            page_data['_timestamp'] = datetime.now().isoformat()
            
            all_data.append(page_data)
            
            # Screenshot
            screenshot_file = f"page_{page_num}_{datetime.now():%Y%m%d_%H%M%S}.png"
            await self.page.screenshot(path=screenshot_file, full_page=True)
            screenshots.append(screenshot_file)
            
            # Try to go to next page
            if page_num < task.max_pages:
                has_next = await self.click_next_page()
                if not has_next:
                    logger.info(f"No more pages after page {page_num}")
                    break
        
        return ScrapedData(
            url=task.url,
            data=all_data,
            screenshots=screenshots,
            pages_scraped=len(all_data),
            timestamp=datetime.now(),
            errors=errors
        )
    
    async def scrape_financial_news(
        self,
        source: str = "yahoo",
        ticker: str = None,
        max_pages: int = 3
    ) -> ScrapedData:
        """Scrape financial news with pagination."""
        
        urls = {
            "yahoo": f"https://finance.yahoo.com/quote/{ticker}/news" if ticker else "https://finance.yahoo.com/news",
            "bloomberg": "https://www.bloomberg.com/markets",
            "ft": "https://www.ft.com/markets",
            "reuters": "https://www.reuters.com/markets/"
        }
        
        url = urls.get(source, urls["yahoo"])
        
        task = ScrapingTask(
            url=url,
            goal=f"Extract financial news from {source}",
            selectors={
                "headlines": "h3",
                "summaries": "p",
                "dates": "time",
                "links": "a[href*='/news/'], a[href*='/article/']"
            },
            max_pages=max_pages,
            scroll_to_bottom=True,
            wait_for="h3"
        )
        
        return await self.scrape_with_pagination(task)
    
    async def scrape_trading212_history(self) -> ScrapedData:
        """Automated extraction of Trading 212 history."""
        task = ScrapingTask(
            url="https://www.trading212.com/history",
            goal="Extract transaction history",
            selectors={
                "actions": "[data-testid='action']",
                "tickers": "[data-testid='ticker']",
                "dates": "[data-testid='date']",
                "amounts": "[data-testid='amount']"
            },
            max_pages=10,
            scroll_to_bottom=False
        )
        
        # Note: Requires login
        logger.warning("Trading 212 scraping requires manual login first")
        
        return await self.scrape_with_pagination(task)
    
    async def autonomous_search_and_scrape(
        self,
        query: str,
        llm_guidance: bool = True
    ) -> List[ScrapedData]:
        """
        AI-driven autonomous search and scrape.
        Uses LLM to determine what to scrape.
        """
        results = []
        
        # Search Google
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        await self.navigate(search_url)
        
        # Extract search results
        links = await self.page.locator("a[href^='http']").all()
        urls = []
        
        for link in links[:5]:  # Top 5 results
            href = await link.get_attribute('href')
            if href and 'google' not in href:
                urls.append(href)
        
        # Scrape each result
        for url in urls[:3]:  # Limit to 3 pages
            task = ScrapingTask(
                url=url,
                goal=f"Extract relevant information about: {query}",
                selectors={
                    "title": "h1",
                    "content": "p",
                    "headings": "h2, h3"
                },
                max_pages=1
            )
            
            result = await self.scrape_with_pagination(task)
            results.append(result)
            
            # Rate limiting
            await asyncio.sleep(random.uniform(2, 5))
        
        return results
    
    async def fill_form(self, form_data: Dict[str, str]):
        """Fill form fields."""
        for selector, value in form_data.items():
            try:
                await self.page.fill(selector, value)
                await asyncio.sleep(random.uniform(0.2, 0.5))
            except Exception as e:
                logger.warning(f"Failed to fill {selector}: {e}")
    
    async def submit_form(self, submit_selector: str = "button[type='submit']"):
        """Submit form."""
        try:
            await self.page.click(submit_selector)
            await asyncio.sleep(2)
            return True
        except:
            return False
    
    async def execute_javascript(self, script: str) -> Any:
        """Execute JavaScript on page."""
        return await self.page.evaluate(script)
    
    async def wait_for_element(self, selector: str, timeout: int = 10000):
        """Wait for element to appear."""
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except:
            return False
    
    async def close(self):
        """Clean up browser resources."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'pw'):
            await self.pw.stop()
        logger.info("✓ Browser closed")

# Example usage functions
async def example_scrape_yahoo_news():
    """Example: Scrape Yahoo Finance news."""
    browser = AutonomousBrowser(headless=False)
    await browser.init()
    
    result = await browser.scrape_financial_news(
        source="yahoo",
        ticker="AAPL",
        max_pages=2
    )
    
    print(f"Scraped {result.pages_scraped} pages")
    print(f"Data: {result.data}")
    
    await browser.close()

async def example_multi_page_scrape():
    """Example: Scrape multiple pages with pagination."""
    browser = AutonomousBrowser(headless=False, slow_mo=100)
    await browser.init()
    
    task = ScrapingTask(
        url="https://example-site.com/products",
        goal="Extract product listings",
        selectors={
            "names": ".product-name",
            "prices": ".product-price",
            "images": ".product-image img"
        },
        max_pages=5,
        scroll_to_bottom=True
    )
    
    def progress(current, total):
        print(f"Progress: {current}/{total} pages")
    
    result = await browser.scrape_with_pagination(task, progress)
    
    print(f"\nScraped {result.pages_scraped} pages")
    print(f"Screenshots saved: {result.screenshots}")
    
    await browser.close()

if __name__ == "__main__":
    print("Autonomous Browser ready")
    print("\nUsage:")
    print("  import asyncio")
    print("  from autonomous_browser import AutonomousBrowser, ScrapingTask")
    print()
    print("  async def main():")
    print("      browser = AutonomousBrowser(headless=False)")
    print("      await browser.init()")
    print()
    print("      task = ScrapingTask(")
    print("          url='https://example.com',")
    print("          goal='Extract data',")
    print("          selectors={'title': 'h1', 'content': 'p'},")
    print("          max_pages=3")
    print("      )")
    print()
    print("      result = await browser.scrape_with_pagination(task)")
    print("      print(result.data)")
    print()
    print("      await browser.close()")
    print()
    print("  asyncio.run(main())")
