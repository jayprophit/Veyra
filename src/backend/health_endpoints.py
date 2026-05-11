# Add to main.py for Render health checks
from fastapi import FastAPI
from datetime import datetime
import asyncio
import aiohttp

app = FastAPI(title="Veyra API", version="1.0.0")

@app.get("/health")
async def health_check():
    """Health check endpoint for Render monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "service": "Veyra"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Veyra - 5-STAR+ Platform",
        "status": "operational",
        "docs": "/docs",
        "health": "/health"
    }

# Keep-alive service to prevent Render spin-down
async def keep_alive():
    """Ping the service every 10 minutes to prevent spin-down"""
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                await session.get("https://veyra.onrender.com/health")
        except Exception as e:
            print(f"Keep-alive ping failed: {e}")
        await asyncio.sleep(600)  # 10 minutes

# Start keep-alive in background
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(keep_alive())