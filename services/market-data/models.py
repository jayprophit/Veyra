from datetime import datetime, timezone

from pydantic import BaseModel, Field, field_validator


class MarketEvent(BaseModel):
    """Canonical market tick used before data reaches charts, AI, or portfolio code."""

    symbol: str = Field(..., min_length=1)
    exchange: str = "UNKNOWN"
    timestamp: datetime
    price: float = Field(..., ge=0)
    volume: float = Field(0, ge=0)
    source: str = Field(..., min_length=1)
    currency: str = "USD"

    @field_validator("symbol", "exchange", "source", "currency")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("value cannot be blank")
        return cleaned.upper()

    @field_validator("timestamp")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
