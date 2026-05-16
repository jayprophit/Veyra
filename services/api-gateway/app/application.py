from datetime import datetime, timezone
from pathlib import Path
import os
import secrets
import sys
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import (
    PaperOrder,
    ResearchDocument,
    ResearchSourcePage,
    RefreshToken,
    database_backend,
    database_healthcheck,
    get_session,
    hash_refresh_token,
    init_db,
)


MARKET_DATA_PATH = Path(__file__).resolve().parents[2] / "market-data"
if str(MARKET_DATA_PATH) not in sys.path:
    sys.path.insert(0, str(MARKET_DATA_PATH))

from normalizer import MarketNormalizationError, MarketNormalizer  # noqa: E402

AI_ENGINE_PATH = Path(__file__).resolve().parents[2] / "ai-engine"
if str(AI_ENGINE_PATH) not in sys.path:
    sys.path.insert(0, str(AI_ENGINE_PATH))

CRAWLER_PATH = Path(__file__).resolve().parents[2] / "crawler"
if str(CRAWLER_PATH) not in sys.path:
    sys.path.insert(0, str(CRAWLER_PATH))

BROWSER_AUTOMATION_PATH = Path(__file__).resolve().parents[2] / "browser-automation"
if str(BROWSER_AUTOMATION_PATH) not in sys.path:
    sys.path.insert(0, str(BROWSER_AUTOMATION_PATH))

from automation import BrowserAutomationUnavailable, providers, snapshot_page  # noqa: E402
from crawler import CrawlError, CrawledSite, crawl_paginated_site, crawl_readable_page  # noqa: E402
from ollama_client import OllamaClient, OllamaError  # noqa: E402
from pagination import paginate_text  # noqa: E402


def _csv_env(name: str, default: str) -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


APP_VERSION = "0.1.0"
_normalizer = MarketNormalizer()
_ollama = OllamaClient()
init_db()


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=1)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=16)


class OrderCreate(BaseModel):
    symbol: str = Field(..., min_length=1)
    side: Literal["buy", "sell"]
    quantity: float = Field(..., gt=0)
    price: float | None = Field(default=None, ge=0)


class AIChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=12000)
    system_prompt: str | None = Field(default=None, max_length=4000)
    model: str | None = Field(default=None, min_length=1, max_length=128)
    temperature: float = Field(default=0.2, ge=0, le=2)


class ResearchCrawlRequest(BaseModel):
    url: str = Field(..., min_length=8, max_length=2048)
    page_size: int = Field(default=1200, ge=200, le=5000)
    follow_pagination: bool = False
    max_source_pages: int = Field(default=5, ge=1, le=25)
    same_domain_only: bool = True


class BrowserSnapshotRequest(BaseModel):
    url: str = Field(..., min_length=8, max_length=2048)


class BrowserPlanRequest(BaseModel):
    objective: str = Field(..., min_length=3, max_length=2000)
    current_url: str | None = Field(default=None, max_length=2048)
    visible_text: str = Field(..., min_length=1, max_length=12000)


class BrowserResearchRequest(BaseModel):
    objective: str = Field(..., min_length=3, max_length=2000)
    url: str = Field(..., min_length=8, max_length=2048)
    page_size: int = Field(default=1200, ge=200, le=5000)
    max_source_pages: int = Field(default=5, ge=1, le=25)
    same_domain_only: bool = True


app = FastAPI(
    title="Veyra API",
    description="Local-first financial intelligence API for private development.",
    version=APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_csv_env(
        "VEYRA_CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["System"])
async def root() -> dict:
    return {
        "name": "Veyra",
        "version": APP_VERSION,
        "mode": "local-first",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["System"])
async def health_check() -> dict:
    db_health = database_healthcheck()
    if not db_health["connected"]:
        raise HTTPException(status_code=503, detail="database unavailable")

    return {
        "status": "ok",
        "version": APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dependencies": {
            "database": db_health,
            "market_data": "canonical-normalizer",
        },
    }


@app.get("/status", tags=["System"])
async def status_check() -> dict:
    return {
        "platform": "Veyra",
        "version": APP_VERSION,
        "phase": "private-foundation",
        "features": {
            "api_gateway": "active",
            "database": database_backend(),
            "market_normalization": "active",
            "portfolio": "mock-local",
            "paper_trading": "database-backed",
            "research_reader": "active",
            "local_ai": "active-when-ollama-online",
            "browser_automation": "bounded-research-active",
            "broker_execution": "roadmap",
            "ai_agents": "roadmap",
        },
    }


@app.post("/auth/login", tags=["Authentication"])
async def login(payload: LoginRequest, session: Session = Depends(get_session)) -> dict:
    expected_email = os.getenv("VEYRA_DEV_EMAIL", "local@veyra.dev")
    expected_password = os.getenv("VEYRA_DEV_PASSWORD", "change-me")

    if payload.email != expected_email or payload.password != expected_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid local development credentials",
        )

    access_token = secrets.token_urlsafe(32)
    refresh_token = secrets.token_urlsafe(48)
    session.add(
        RefreshToken(
            token_hash=hash_refresh_token(refresh_token),
            email=payload.email,
        )
    )
    session.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 1800,
    }


@app.post("/auth/refresh", tags=["Authentication"])
async def refresh_token(payload: RefreshRequest, session: Session = Depends(get_session)) -> dict:
    record = session.get(RefreshToken, hash_refresh_token(payload.refresh_token))
    if not record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    return {
        "access_token": secrets.token_urlsafe(32),
        "token_type": "bearer",
        "email": record.email,
        "expires_in": 1800,
    }


@app.get("/api/markets/quotes/{symbol}", tags=["Markets"])
async def get_quote(symbol: str) -> dict:
    event = _mock_market_event(symbol)
    return event.model_dump(mode="json")


@app.get("/api/markets/quotes", tags=["Markets"])
async def get_quotes(symbols: str = Query(..., description="Comma-separated symbols")) -> dict:
    symbol_list = [item.strip().upper() for item in symbols.split(",") if item.strip()]
    return {
        "quotes": [_mock_market_event(symbol).model_dump(mode="json") for symbol in symbol_list],
        "count": len(symbol_list),
    }


@app.get("/api/markets/search", tags=["Markets"])
async def search_markets(q: str, limit: int = Query(10, ge=1, le=50)) -> dict:
    query = q.strip().upper()
    if not query:
        return {"query": q, "results": [], "total": 0}

    results = [
        {
            "symbol": query[:8],
            "name": f"{query} local instrument",
            "type": "equity",
            "source": "local-mock",
        }
    ][:limit]
    return {"query": q, "results": results, "total": len(results)}


@app.get("/api/markets/status", tags=["Markets"])
async def market_status() -> dict:
    return {
        "normalizer": "active",
        "providers": [{"name": "local-mock", "status": "active"}],
        "live_data": "disabled",
    }


@app.get("/api/portfolio/overview", tags=["Portfolio"])
async def portfolio_overview() -> dict:
    return {
        "currency": "USD",
        "total_value": 100000.0,
        "cash": 25000.0,
        "invested": 75000.0,
        "today_change": 0.0,
        "positions_count": 2,
        "mode": "mock-local",
    }


@app.get("/api/portfolio/positions", tags=["Portfolio"])
async def portfolio_positions() -> dict:
    return {
        "positions": [
            {"symbol": "AAPL", "quantity": 10, "avg_cost": 150.0, "current_price": 175.0},
            {"symbol": "MSFT", "quantity": 5, "avg_cost": 300.0, "current_price": 330.0},
        ],
        "total": 2,
    }


@app.get("/api/portfolio/performance", tags=["Portfolio"])
async def portfolio_performance(period: str = "1y") -> dict:
    return {
        "period": period,
        "return_percent": 0.0,
        "benchmark_return_percent": 0.0,
        "sharpe_ratio": None,
        "max_drawdown_percent": None,
        "mode": "mock-local",
    }


@app.post("/api/trading/orders/create", status_code=201, tags=["Trading"])
async def create_order(order: OrderCreate, session: Session = Depends(get_session)) -> dict:
    order_id = f"PAPER-{secrets.token_hex(6).upper()}"
    record = PaperOrder(
        order_id=order_id,
        symbol=order.symbol.upper(),
        side=order.side,
        quantity=order.quantity,
        price=order.price,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return _serialize_order(record)


@app.get("/api/trading/orders", tags=["Trading"])
async def list_orders(session: Session = Depends(get_session)) -> dict:
    orders = session.scalars(select(PaperOrder).order_by(PaperOrder.created_at.desc())).all()
    return {"orders": [_serialize_order(order) for order in orders], "total": len(orders)}


@app.delete("/api/trading/orders/{order_id}", tags=["Trading"])
async def cancel_order(order_id: str, session: Session = Depends(get_session)) -> dict:
    record = session.get(PaperOrder, order_id)
    if not record:
        raise HTTPException(status_code=404, detail="Order not found")

    record.status = "canceled"
    record.canceled_at = datetime.now(timezone.utc)
    session.commit()
    session.refresh(record)
    return _serialize_order(record)


@app.get("/api/trading/history", tags=["Trading"])
async def trading_history(session: Session = Depends(get_session)) -> dict:
    completed = session.scalars(
        select(PaperOrder)
        .where(PaperOrder.status.in_(("filled", "canceled")))
        .order_by(PaperOrder.created_at.desc())
    ).all()
    return {
        "trades": [_serialize_order(order) for order in completed],
        "total": len(completed),
        "mode": "paper",
    }


@app.get("/api/ai/status", tags=["AI"])
async def ai_status() -> dict:
    status_payload = await _ollama.status()
    return {
        "provider": "ollama",
        "default_model": _ollama.default_model,
        "available": status_payload.available,
        "host": status_payload.host,
        "version": status_payload.version,
        "error": status_payload.error,
    }


@app.get("/api/ai/models", tags=["AI"])
async def ai_models() -> dict:
    status_payload = await _ollama.status()
    if not status_payload.available:
        return {
            "provider": "ollama",
            "available": False,
            "models": [],
            "error": status_payload.error,
        }

    try:
        models = await _ollama.list_models()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {
        "provider": "ollama",
        "available": True,
        "models": models,
        "default_model": _ollama.default_model,
    }


@app.post("/api/ai/chat", tags=["AI"])
async def ai_chat(payload: AIChatRequest) -> dict:
    try:
        return await _ollama.chat(
            payload.prompt,
            system_prompt=payload.system_prompt,
            model=payload.model,
            temperature=payload.temperature,
        )
    except OllamaError as exc:
        raise HTTPException(status_code=503, detail=f"ollama unavailable: {exc}") from exc


@app.get("/api/browser/providers", tags=["Browser Automation"])
async def browser_providers() -> dict:
    provider_rows = [provider.__dict__ for provider in providers()]
    return {
        "providers": provider_rows,
        "active": [provider["name"] for provider in provider_rows if provider["installed"]],
    }


@app.post("/api/browser/snapshot", tags=["Browser Automation"])
async def browser_snapshot(payload: BrowserSnapshotRequest) -> dict:
    try:
        return await snapshot_page(payload.url)
    except BrowserAutomationUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/api/browser/plan", tags=["Browser Automation"])
async def browser_plan(payload: BrowserPlanRequest) -> dict:
    prompt = (
        "Objective:\n"
        f"{payload.objective}\n\n"
        "Current URL:\n"
        f"{payload.current_url or 'unknown'}\n\n"
        "Visible page text:\n"
        f"{payload.visible_text}\n\n"
        "Return the next three safe browser actions only. "
        "Do not claim an action has happened. "
        "Flag any action that would submit data, spend money, or change an account."
    )
    try:
        return await _ollama.chat(
            prompt,
            system_prompt=(
                "You are a browser task planner. Be concise, factual, and cautious. "
                "Never fabricate page elements that are not visible."
            ),
            temperature=0.1,
        )
    except OllamaError as exc:
        raise HTTPException(status_code=503, detail=f"ollama unavailable: {exc}") from exc


@app.post("/api/browser/research", status_code=201, tags=["Browser Automation"])
async def browser_research(
    payload: BrowserResearchRequest,
    session: Session = Depends(get_session),
) -> dict:
    try:
        site = await crawl_paginated_site(
            payload.url,
            max_pages=payload.max_source_pages,
            same_domain_only=payload.same_domain_only,
        )
    except CrawlError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    document = _store_research_site(
        site,
        page_size=payload.page_size,
        session=session,
    )
    steps = _serialize_browser_steps(site)
    return {
        "run_id": f"RUN-{secrets.token_hex(6).upper()}",
        "objective": payload.objective,
        "mode": "bounded-research",
        "steps": steps,
        "document": _serialize_document(document, page=1),
        "source_pages": _serialize_source_pages(document.document_id, session),
    }


@app.post("/api/research/crawl", status_code=201, tags=["Research"])
async def crawl_research_document(
    payload: ResearchCrawlRequest,
    session: Session = Depends(get_session),
) -> dict:
    try:
        site = (
            await crawl_paginated_site(
                payload.url,
                max_pages=payload.max_source_pages,
                same_domain_only=payload.same_domain_only,
            )
            if payload.follow_pagination
            else CrawledSite(pages=(await crawl_readable_page(payload.url),))
        )
    except CrawlError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    document = _store_research_site(site, page_size=payload.page_size, session=session)
    response = _serialize_document(document, page=1)
    response["source_pages"] = _serialize_source_pages(document.document_id, session)
    return response


@app.get("/api/research/documents", tags=["Research"])
async def list_research_documents(session: Session = Depends(get_session)) -> dict:
    documents = session.scalars(
        select(ResearchDocument).order_by(ResearchDocument.created_at.desc())
    ).all()
    return {
        "documents": [_serialize_document_summary(document, session) for document in documents],
        "total": len(documents),
    }


@app.get("/api/research/documents/{document_id}", tags=["Research"])
async def get_research_document(
    document_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int | None = Query(default=None, ge=200, le=5000),
    session: Session = Depends(get_session),
) -> dict:
    document = session.get(ResearchDocument, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return _serialize_document(document, page=page, page_size=page_size)


@app.get("/api/research/documents/{document_id}/sources", tags=["Research"])
async def list_research_source_pages(
    document_id: str,
    session: Session = Depends(get_session),
) -> dict:
    document = session.get(ResearchDocument, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "document_id": document_id,
        "source_pages": _serialize_source_pages(document_id, session),
    }


def _mock_market_event(symbol: str):
    cleaned_symbol = symbol.strip().upper()
    if not cleaned_symbol:
        raise HTTPException(status_code=400, detail="symbol is required")

    price = round(50 + (sum(ord(char) for char in cleaned_symbol) % 500), 2)
    raw = {
        "symbol": cleaned_symbol,
        "Close": price,
        "Volume": 100000,
        "timestamp": datetime.now(timezone.utc),
        "source": "local-mock",
        "exchange": "SIM",
        "currency": "USD",
    }

    try:
        return _normalizer.normalize_yfinance(raw)
    except MarketNormalizationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def _serialize_order(order: PaperOrder) -> dict:
    return {
        "order_id": order.order_id,
        "symbol": order.symbol,
        "side": order.side,
        "quantity": order.quantity,
        "price": order.price if order.price is not None else "market",
        "status": order.status,
        "mode": order.mode,
        "created_at": order.created_at.isoformat(),
        "canceled_at": order.canceled_at.isoformat() if order.canceled_at else None,
    }


def _serialize_document_summary(document: ResearchDocument, session: Session) -> dict:
    page = paginate_text(document.content, page_size=document.page_size)
    return {
        "document_id": document.document_id,
        "url": document.url,
        "title": document.title,
        "page_count": page.page_count,
        "page_size": document.page_size,
        "source_page_count": len(_serialize_source_pages(document.document_id, session)),
        "created_at": document.created_at.isoformat(),
    }


def _serialize_document(
    document: ResearchDocument,
    *,
    page: int,
    page_size: int | None = None,
) -> dict:
    try:
        slice_ = paginate_text(
            document.content,
            page=page,
            page_size=page_size or document.page_size,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "document_id": document.document_id,
        "url": document.url,
        "title": document.title,
        "created_at": document.created_at.isoformat(),
        "page": slice_.page,
        "page_count": slice_.page_count,
        "page_size": slice_.page_size,
        "has_previous": slice_.has_previous,
        "has_next": slice_.has_next,
        "text": slice_.text,
    }


def _store_research_site(
    site: CrawledSite,
    *,
    page_size: int,
    session: Session,
) -> ResearchDocument:
    if not site.pages:
        raise HTTPException(status_code=400, detail="no readable pages were found")

    content = "\n\n".join(
        f"Source page {index}: {page.url}\n{page.text}"
        for index, page in enumerate(site.pages, start=1)
    )
    document = ResearchDocument(
        document_id=f"DOC-{secrets.token_hex(6).upper()}",
        url=site.pages[0].url,
        title=site.pages[0].title,
        content=content,
        page_size=page_size,
    )
    session.add(document)
    session.flush()
    for index, page in enumerate(site.pages, start=1):
        session.add(
            ResearchSourcePage(
                document_id=document.document_id,
                sequence=index,
                url=page.url,
                title=page.title,
                content=page.text,
            )
        )
    session.commit()
    session.refresh(document)
    return document


def _serialize_source_pages(document_id: str, session: Session) -> list[dict]:
    source_pages = session.scalars(
        select(ResearchSourcePage)
        .where(ResearchSourcePage.document_id == document_id)
        .order_by(ResearchSourcePage.sequence.asc())
    ).all()
    return [
        {
            "sequence": source_page.sequence,
            "url": source_page.url,
            "title": source_page.title,
        }
        for source_page in source_pages
    ]


def _serialize_browser_steps(site: CrawledSite) -> list[dict]:
    steps: list[dict] = []
    for index, page in enumerate(site.pages, start=1):
        steps.append({"step": len(steps) + 1, "action": "open", "url": page.url})
        steps.append(
            {
                "step": len(steps) + 1,
                "action": "extract_readable_text",
                "url": page.url,
                "source_page": index,
            }
        )
        if index < len(site.pages):
            steps.append(
                {
                    "step": len(steps) + 1,
                    "action": "follow_next_page",
                    "from_url": page.url,
                    "to_url": site.pages[index].url,
                }
            )
    return steps


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.getenv("VEYRA_API_HOST", "127.0.0.1"),
        port=int(os.getenv("VEYRA_API_PORT", "8000")),
        reload=os.getenv("VEYRA_RELOAD", "true").lower() == "true",
    )
