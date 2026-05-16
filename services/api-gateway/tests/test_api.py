from pathlib import Path
import os
import sys

from fastapi.testclient import TestClient


API_PATH = Path(__file__).resolve().parents[1]
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
sys.path.insert(0, str(API_PATH))

from main import app


client = TestClient(app)


def test_health_status_and_openapi_load():
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert health.json()["dependencies"]["database"]["connected"] is True

    status = client.get("/status")
    assert status.status_code == 200
    assert status.json()["phase"] == "private-foundation"

    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
    assert "paths" in openapi.json()


def test_local_auth_flow():
    login = client.post(
        "/auth/login",
        json={"email": "local@veyra.dev", "password": "change-me"},
    )
    assert login.status_code == 200
    refresh_token = login.json()["refresh_token"]

    refresh = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh.status_code == 200
    assert refresh.json()["token_type"] == "bearer"


def test_market_quote_uses_canonical_shape():
    response = client.get("/api/markets/quotes/AAPL")
    assert response.status_code == 200
    body = response.json()
    assert body["symbol"] == "AAPL"
    assert body["exchange"] == "SIM"
    assert body["source"] == "LOCAL-MOCK"
    assert body["currency"] == "USD"
    assert body["price"] >= 0


def test_paper_orders_are_database_backed():
    created = client.post(
        "/api/trading/orders/create",
        json={"symbol": "msft", "side": "buy", "quantity": 2},
    )
    assert created.status_code == 201
    order_id = created.json()["order_id"]

    listed = client.get("/api/trading/orders")
    assert listed.status_code == 200
    assert any(order["order_id"] == order_id for order in listed.json()["orders"])

    canceled = client.delete(f"/api/trading/orders/{order_id}")
    assert canceled.status_code == 200
    assert canceled.json()["status"] == "canceled"

    history = client.get("/api/trading/history")
    assert history.status_code == 200
    assert any(order["order_id"] == order_id for order in history.json()["trades"])


def test_ai_status_is_safe_when_provider_is_offline():
    response = client.get("/api/ai/status")
    assert response.status_code == 200
    assert response.json()["provider"] == "ollama"
    assert "available" in response.json()


def test_research_reader_supports_pagination(monkeypatch):
    from app import application
    from crawler import CrawledPage

    async def fake_crawl(_url: str) -> CrawledPage:
        return CrawledPage(
            url="https://example.test/article",
            title="Example",
            text="A" * 2500,
        )

    monkeypatch.setattr(application, "crawl_readable_page", fake_crawl)

    created = client.post(
        "/api/research/crawl",
        json={"url": "https://example.test/article", "page_size": 1000},
    )
    assert created.status_code == 201
    body = created.json()
    assert body["page_count"] == 3
    assert body["page"] == 1

    next_page = client.get(
        f"/api/research/documents/{body['document_id']}",
        params={"page": 2},
    )
    assert next_page.status_code == 200
    assert next_page.json()["page"] == 2
    assert next_page.json()["has_previous"] is True


def test_browser_research_preserves_source_pages(monkeypatch):
    from app import application
    from crawler import CrawledPage, CrawledSite

    async def fake_paginated_site(*_args, **_kwargs) -> CrawledSite:
        return CrawledSite(
            pages=(
                CrawledPage(
                    url="https://example.test/page/1",
                    title="Page One",
                    text="first page text",
                ),
                CrawledPage(
                    url="https://example.test/page/2",
                    title="Page Two",
                    text="second page text",
                ),
            )
        )

    monkeypatch.setattr(application, "crawl_paginated_site", fake_paginated_site)

    created = client.post(
        "/api/browser/research",
        json={
            "objective": "Collect readable pages",
            "url": "https://example.test/page/1",
            "page_size": 400,
            "max_source_pages": 2,
        },
    )
    assert created.status_code == 201
    body = created.json()
    assert body["mode"] == "bounded-research"
    assert len(body["steps"]) == 5
    assert len(body["source_pages"]) == 2

    source_pages = client.get(
        f"/api/research/documents/{body['document']['document_id']}/sources"
    )
    assert source_pages.status_code == 200
    assert [page["sequence"] for page in source_pages.json()["source_pages"]] == [1, 2]
