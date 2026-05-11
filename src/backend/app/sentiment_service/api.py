"""
Sentiment API - FastAPI endpoints for sentiment data
"""

from fastapi import FastAPI, HTTPException, Query, WebSocket
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
import json

from .scraper import SentimentScraper
from .ml_models import SentimentAnalyzer
from .websocket_handler import SentimentWebSocket

app = FastAPI(title="Veyra Sentiment API", version="1.0.0")

# Initialize components
scraper = SentimentScraper()
analyzer = SentimentAnalyzer()
websocket_handler = SentimentWebSocket()

@app.get("/api/v1/sentiment/live")
async def get_live_sentiment(
    ticker: Optional[str] = Query(None, description="Filter by ticker symbol"),
    source: Optional[str] = Query(None, description="Filter by source (twitter, reddit, news)"),
    limit: int = Query(50, ge=1, le=200)
):
    """Get real-time sentiment data"""
    try:
        data = await scraper.get_recent_sentiment(
            ticker=ticker,
            source=source,
            limit=limit
        )
        return {
            "status": "success",
            "count": len(data),
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/sentiment/historical")
async def get_historical_sentiment(
    ticker: str = Query(..., description="Ticker symbol"),
    days: int = Query(7, ge=1, le=90),
    aggregation: str = Query("hourly", enum=["hourly", "daily", "weekly"])
):
    """Get historical sentiment trends"""
    try:
        data = await scraper.get_historical_sentiment(
            ticker=ticker,
            days=days,
            aggregation=aggregation
        )
        return {
            "status": "success",
            "ticker": ticker,
            "period_days": days,
            "aggregation": aggregation,
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/sentiment/ticker/{ticker}")
async def get_ticker_sentiment(ticker: str):
    """Get comprehensive sentiment for a specific ticker"""
    try:
        # Get latest sentiment
        latest = await scraper.get_recent_sentiment(ticker=ticker, limit=100)
        
        # Calculate aggregate scores
        if latest:
            avg_sentiment = sum(item['sentiment_score'] for item in latest) / len(latest)
            avg_confidence = sum(item['confidence'] for item in latest) / len(latest)
            positive_ratio = sum(1 for item in latest if item['sentiment_score'] > 0) / len(latest)
        else:
            avg_sentiment = 0
            avg_confidence = 0
            positive_ratio = 0
        
        return {
            "status": "success",
            "ticker": ticker,
            "summary": {
                "average_sentiment": round(avg_sentiment, 3),
                "average_confidence": round(avg_confidence, 3),
                "positive_ratio": round(positive_ratio, 3),
                "total_mentions": len(latest),
                "sentiment_label": "positive" if avg_sentiment > 0.1 else "negative" if avg_sentiment < -0.1 else "neutral"
            },
            "recent_mentions": latest[:10]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/sentiment/scrape")
async def trigger_manual_scrape(
    sources: List[str] = Query(default=["twitter", "reddit", "news"]),
    tickers: Optional[List[str]] = Query(None)
):
    """Manually trigger sentiment scraping"""
    try:
        result = await scraper.scrape_multiple(sources=sources, tickers=tickers)
        return {
            "status": "success",
            "scraped_count": result['count'],
            "sources": sources,
            "duration_seconds": result['duration'],
            "new_items": result['new_items']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/sentiment/sources")
async def get_active_sources():
    """List all active sentiment sources"""
    sources = [
        {"id": "twitter", "name": "Twitter/X", "status": "active", "latency_ms": 250},
        {"id": "reddit", "name": "Reddit", "status": "active", "latency_ms": 500},
        {"id": "news", "name": "Financial News", "status": "active", "latency_ms": 300},
        {"id": "sec", "name": "SEC Filings", "status": "active", "latency_ms": 1000},
        {"id": "yahoo", "name": "Yahoo Finance", "status": "active", "latency_ms": 200},
    ]
    return {"sources": sources}

@app.get("/api/v1/sentiment/jobs")
async def get_scraper_jobs():
    """Get status of background scraping jobs"""
    jobs = await scraper.get_job_status()
    return {"jobs": jobs}

@app.post("/api/v1/sentiment/analyze")
async def analyze_text(text: str, ticker: Optional[str] = None):
    """Analyze sentiment of provided text"""
    try:
        result = await analyzer.analyze(text, ticker=ticker)
        return {
            "status": "success",
            "analysis": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/sentiment")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time sentiment updates"""
    await websocket_handler.connect(websocket)
    try:
        while True:
            # Send updates every 30 seconds
            data = await scraper.get_recent_sentiment(limit=10)
            await websocket.send_json({
                "type": "sentiment_update",
                "timestamp": datetime.now().isoformat(),
                "data": data
            })
            await asyncio.sleep(30)
    except Exception as e:
        await websocket_handler.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
