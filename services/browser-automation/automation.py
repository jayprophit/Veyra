from dataclasses import dataclass
from importlib.util import find_spec


class BrowserAutomationUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class BrowserProvider:
    name: str
    installed: bool
    role: str


def providers() -> list[BrowserProvider]:
    return [
        BrowserProvider("playwright", find_spec("playwright") is not None, "direct-control"),
        BrowserProvider("crawl4ai", find_spec("crawl4ai") is not None, "adaptive-crawling"),
        BrowserProvider("browser-use", find_spec("browser_use") is not None, "agentic-browser"),
    ]


async def snapshot_page(url: str) -> dict:
    if find_spec("playwright") is None:
        raise BrowserAutomationUnavailable(
            "Playwright is not installed. Install the optional browser stack first."
        )

    from playwright.async_api import async_playwright

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        title = await page.title()
        text = await page.locator("body").inner_text()
        final_url = page.url
        await browser.close()

    return {
        "url": final_url,
        "title": title,
        "text": text,
        "provider": "playwright",
    }
