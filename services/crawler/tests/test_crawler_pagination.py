from pathlib import Path
import sys

from bs4 import BeautifulSoup

CRAWLER_PATH = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CRAWLER_PATH))

from crawler import _find_next_page_url


def test_find_next_page_prefers_rel_next() -> None:
    soup = BeautifulSoup(
        """
        <html>
          <head><link rel="next" href="/page/2" /></head>
          <body><a href="/ignore">Next</a></body>
        </html>
        """,
        "html.parser",
    )

    assert (
        _find_next_page_url(
            soup,
            "https://example.com/page/1",
            seen_urls=set(),
            same_domain="example.com",
        )
        == "https://example.com/page/2"
    )


def test_find_next_page_rejects_external_domains() -> None:
    soup = BeautifulSoup(
        '<html><body><a href="https://outside.test/page/2">Next</a></body></html>',
        "html.parser",
    )

    assert (
        _find_next_page_url(
            soup,
            "https://example.com/page/1",
            seen_urls=set(),
            same_domain="example.com",
        )
        is None
    )
