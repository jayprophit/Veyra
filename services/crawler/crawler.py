from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup


class CrawlError(RuntimeError):
    pass


@dataclass(frozen=True)
class CrawledPage:
    url: str
    title: str
    text: str


@dataclass(frozen=True)
class CrawledSite:
    pages: tuple[CrawledPage, ...]


def _validate_url(url: str) -> str:
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise CrawlError("url must use http or https")
    return parsed.geturl()


async def crawl_readable_page(url: str) -> CrawledPage:
    page, _ = await _crawl_page(url)
    return page


async def crawl_paginated_site(
    url: str,
    *,
    max_pages: int = 5,
    same_domain_only: bool = True,
) -> CrawledSite:
    if max_pages < 1 or max_pages > 25:
        raise CrawlError("max_pages must be between 1 and 25")

    normalized_url = _validate_url(url)
    seed_domain = urlparse(normalized_url).netloc
    seen_urls: set[str] = set()
    pages: list[CrawledPage] = []
    next_url: str | None = normalized_url

    while next_url and len(pages) < max_pages and next_url not in seen_urls:
        page, soup = await _crawl_page(next_url)
        seen_urls.add(page.url)
        pages.append(page)
        next_url = _find_next_page_url(
            soup,
            page.url,
            seen_urls=seen_urls,
            same_domain=seed_domain if same_domain_only else None,
        )

    return CrawledSite(pages=tuple(pages))


async def _crawl_page(url: str) -> tuple[CrawledPage, BeautifulSoup]:
    normalized_url = _validate_url(url)
    headers = {
        "User-Agent": "VeyraResearchBot/0.1 (+local-first)",
        "Accept": "text/html,application/xhtml+xml",
    }

    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers=headers) as client:
            response = await client.get(normalized_url)
            response.raise_for_status()
    except Exception as exc:
        raise CrawlError(str(exc)) from exc

    content_type = response.headers.get("content-type", "")
    if "html" not in content_type:
        raise CrawlError("only HTML pages are supported by the starter crawler")

    soup = BeautifulSoup(response.text, "html.parser")
    for node in soup(["script", "style", "noscript", "svg", "canvas", "template"]):
        node.decompose()

    title = soup.title.get_text(" ", strip=True) if soup.title else normalized_url
    text = "\n".join(
        line.strip()
        for line in soup.get_text("\n").splitlines()
        if line.strip()
    )
    if not text:
        raise CrawlError("page did not contain readable text")

    return CrawledPage(url=str(response.url), title=title, text=text), soup


def _find_next_page_url(
    soup: BeautifulSoup,
    current_url: str,
    *,
    seen_urls: set[str],
    same_domain: str | None,
) -> str | None:
    candidates: list[str] = []

    for node in soup.select('link[rel~="next"], a[rel~="next"]'):
        href = node.get("href")
        if href:
            candidates.append(href)

    for node in soup.find_all("a", href=True):
        label = " ".join(
            filter(
                None,
                [
                    node.get_text(" ", strip=True),
                    node.get("aria-label", ""),
                    node.get("title", ""),
                ],
            )
        ).strip().lower()
        if label in {"next", "next page", "older", "older posts", "more"}:
            candidates.append(node["href"])

    for href in candidates:
        resolved = urljoin(current_url, href)
        parsed = urlparse(resolved)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            continue
        if same_domain and parsed.netloc != same_domain:
            continue
        if resolved in seen_urls:
            continue
        return resolved

    return None
