from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

try:
    from models import MarketEvent
except ImportError:  # pragma: no cover - supports package-style imports later.
    from .models import MarketEvent


class MarketNormalizationError(ValueError):
    """Raised when provider data cannot be converted to the canonical model."""


class MarketNormalizer:
    """Provider mappers that emit canonical MarketEvent objects."""

    def normalize_yfinance(
        self,
        raw: Mapping[str, Any],
        *,
        symbol: str | None = None,
        exchange: str = "UNKNOWN",
        currency: str = "USD",
    ) -> MarketEvent:
        resolved_symbol = symbol or self._first(raw, ("symbol", "Symbol", "ticker"))
        if not resolved_symbol:
            raise MarketNormalizationError("symbol is required")

        price = self._number(raw, ("Close", "close", "regularMarketPrice", "price"))
        volume = self._number(raw, ("Volume", "volume"), default=0)
        timestamp = self._timestamp(raw)
        source = str(raw.get("source") or "yfinance")
        resolved_exchange = str(raw.get("exchange") or exchange)
        resolved_currency = str(raw.get("currency") or currency)

        return MarketEvent(
            symbol=str(resolved_symbol),
            exchange=resolved_exchange,
            timestamp=timestamp,
            price=price,
            volume=volume,
            source=source,
            currency=resolved_currency,
        )

    @staticmethod
    def _first(raw: Mapping[str, Any], keys: Iterable[str]) -> Any:
        for key in keys:
            value = raw.get(key)
            if value not in (None, ""):
                return value
        return None

    def _number(
        self,
        raw: Mapping[str, Any],
        keys: Iterable[str],
        *,
        default: float | None = None,
    ) -> float:
        value = self._first(raw, keys)
        if value in (None, ""):
            if default is not None:
                return default
            raise MarketNormalizationError(f"missing numeric field: {', '.join(keys)}")

        try:
            return float(value)
        except (TypeError, ValueError) as exc:
            raise MarketNormalizationError(f"invalid numeric value: {value}") from exc

    @staticmethod
    def _timestamp(raw: Mapping[str, Any]) -> datetime:
        value = raw.get("timestamp") or raw.get("Datetime") or raw.get("Date")
        if value is None:
            return datetime.now(timezone.utc)

        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc)

        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value, tz=timezone.utc)

        if isinstance(value, str):
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError as exc:
                raise MarketNormalizationError(f"invalid timestamp: {value}") from exc
            if parsed.tzinfo is None:
                return parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc)

        raise MarketNormalizationError(f"unsupported timestamp value: {value!r}")
