"""
Markets API routes
Real-time market data, quotes, technical analysis
"""
import logging
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from datetime import datetime, timedelta

from src.backend.core.logging_config import get_logger
from src.backend.app.live_data_manager import live_data, is_live_data_available
from src.backend.integrations.free.free_data_sources import get_free_data_sources_manager

router = APIRouter()
logger = get_logger(__name__)

# Initialize free data sources manager
free_data_manager = get_free_data_sources_manager()


@router.get("/quotes/{symbol}")
async def get_quote(
    symbol: str,
    interval: Optional[str] = Query("1d", description="Time interval (1m, 5m, 1h, 1d, 1w, 1mo)")
):
    """
    Get real-time quote for a symbol
    Args:
        symbol: Stock symbol (e.g., AAPL, MSFT)
        interval: Time interval
    Returns:
        Quote data
    """
    logger.info(f"Fetching quote for {symbol}")

    try:
        quote = await live_data.get_quote(symbol.upper())
        if quote:
            return {
                "symbol": quote.symbol,
                "price": quote.price,
                "change": quote.change,
                "change_percent": quote.change_percent,
                "volume": quote.volume,
                "timestamp": quote.timestamp.isoformat(),
                "source": quote.source.value,
                "bid": quote.bid,
                "ask": quote.ask
            }
        else:
            raise HTTPException(status_code=404, detail="Quote not found")
    except Exception as e:
        logger.error(f"Error fetching quote for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quotes")
async def get_quotes(
    symbols: str = Query(..., description="Comma-separated list of symbols"),
    interval: Optional[str] = Query("1d", description="Time interval")
):
    """
    Get real-time quotes for multiple symbols
    Args:
        symbols: Comma-separated stock symbols (e.g., AAPL,MSFT,GOOGL)
        interval: Time interval
    Returns:
        Quote data for all symbols
    """
    logger.info(f"Fetching quotes for {symbols}")

    try:
        symbol_list = [s.strip().upper() for s in symbols.split(',')]
        quotes = await live_data.get_quotes(symbol_list)
        
        return {
            "quotes": [
                {
                    "symbol": quote.symbol,
                    "price": quote.price,
                    "change": quote.change,
                    "change_percent": quote.change_percent,
                    "volume": quote.volume,
                    "timestamp": quote.timestamp.isoformat(),
                    "source": quote.source.value
                }
                for quote in quotes.values()
            ],
            "count": len(quotes)
        }
    except Exception as e:
        logger.error(f"Error fetching quotes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/historical/{symbol}")
async def get_historical(
    symbol: str,
    days: int = Query(30, ge=1, le=365, description="Number of days of historical data"),
    interval: Optional[str] = Query("1d", description="Time interval")
):
    """
    Get historical OHLCV data for a symbol
    Args:
        symbol: Stock symbol
        days: Number of days of data
        interval: Time interval
    Returns:
        Historical data
    """
    logger.info(f"Fetching historical data for {symbol} ({days} days)")

    try:
        historical = await live_data.get_historical_data(symbol.upper(), days)
        
        return {
            "symbol": symbol.upper(),
            "data": [
                {
                    "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                    "open": h.open,
                    "high": h.high,
                    "low": h.low,
                    "close": h.close,
                    "volume": h.volume,
                    "vwap": h.vwap
                }
                for i, h in enumerate(reversed(historical))
            ],
            "count": len(historical)
        }
    except Exception as e:
        logger.error(f"Error fetching historical data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_markets(q: str, limit: int = Query(10, le=100)):
    """
    Search for market instruments
    Args:
        q: Search query
        limit: Max results
    Returns:
        Search results
    """
    logger.info(f"Searching markets: {q}")

    try:
        # Use free data sources to search
        company_data = await free_data_manager.get_company_data(q.upper())
        
        if company_data:
            return {
                "query": q,
                "results": [
                    {
                        "symbol": company_data.symbol,
                        "name": company_data.company_name,
                        "type": "stock",
                        "sector": company_data.sector,
                        "industry": company_data.industry
                    }
                ],
                "total": 1
            }
        else:
            # Return mock results if no data found
            return {
                "query": q,
                "results": [],
                "total": 0
            }
    except Exception as e:
        logger.error(f"Error searching markets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending")
async def get_trending():
    """Get trending symbols"""
    logger.info("Fetching trending symbols")

    try:
        # Get quotes for popular tech stocks as trending
        popular_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "AMD"]
        quotes = await live_data.get_quotes(popular_symbols)
        
        # Sort by change percent
        sorted_quotes = sorted(
            quotes.values(),
            key=lambda x: abs(x.change_percent),
            reverse=True
        )[:10]
        
        return {
            "trending": [
                {
                    "symbol": q.symbol,
                    "price": q.price,
                    "change": q.change,
                    "change_percent": q.change_percent,
                    "volume": q.volume
                }
                for q in sorted_quotes
            ],
            "count": len(sorted_quotes)
        }
    except Exception as e:
        logger.error(f"Error fetching trending symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/company/{symbol}")
async def get_company_info(symbol: str):
    """
    Get comprehensive company information
    Args:
        symbol: Stock symbol
    Returns:
        Company data
    """
    logger.info(f"Fetching company info for {symbol}")

    try:
        company_data = await free_data_manager.get_company_data(symbol.upper())
        
        if company_data:
            return {
                "symbol": company_data.symbol,
                "company_name": company_data.company_name,
                "sector": company_data.sector,
                "industry": company_data.industry,
                "market_cap": company_data.market_cap,
                "fundamentals": company_data.fundamentals,
                "source": company_data.source
            }
        else:
            raise HTTPException(status_code=404, detail="Company not found")
    except Exception as e:
        logger.error(f"Error fetching company info for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/financials/{symbol}")
async def get_financials(
    symbol: str,
    statement_type: str = Query("income", description="Statement type (income, balance, cash)"),
    period: str = Query("annual", description="Period (annual, quarterly)")
):
    """
    Get financial statements
    Args:
        symbol: Stock symbol
        statement_type: Type of statement
        period: Period type
    Returns:
        Financial statements
    """
    logger.info(f"Fetching financials for {symbol}")

    try:
        statements = await free_data_manager.get_financial_statements(
            symbol.upper(),
            statement_type,
            period
        )
        
        return {
            "symbol": symbol.upper(),
            "statement_type": statement_type,
            "period": period,
            "data": statements,
            "count": len(statements)
        }
    except Exception as e:
        logger.error(f"Error fetching financials for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/indicators/{symbol}")
async def get_indicators(
    symbol: str,
    indicators: str = Query("RSI,MACD,MA", description="Comma-separated indicator names")
):
    """
    Get technical indicators
    Args:
        symbol: Stock symbol
        indicators: Comma-separated indicator names
    Returns:
        Technical indicators
    """
    logger.info(f"Fetching indicators for {symbol}")

    try:
        indicator_list = [i.strip() for i in indicators.split(',')]
        indicators_data = await free_data_manager.get_technical_indicators(
            symbol.upper(),
            indicator_list
        )
        
        return {
            "symbol": symbol.upper(),
            "indicators": indicators_data,
            "count": len(indicators_data)
        }
    except Exception as e:
        logger.error(f"Error fetching indicators for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_data_status():
    """Get status of data sources"""
    logger.info("Fetching data source status")

    try:
        live_stats = live_data.get_data_source_stats()
        free_sources_status = free_data_manager.get_sources_status()
        
        return {
            "live_data": live_stats,
            "free_sources": free_sources_status,
            "is_live_available": is_live_data_available()
        }
    except Exception as e:
        logger.error(f"Error fetching data status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
