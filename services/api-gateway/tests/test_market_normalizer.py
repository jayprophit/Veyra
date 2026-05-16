from datetime import datetime, timezone
from pathlib import Path
import sys


MARKET_DATA_PATH = Path(__file__).resolve().parents[2] / "market-data"
sys.path.insert(0, str(MARKET_DATA_PATH))

from normalizer import MarketNormalizationError, MarketNormalizer  # noqa: E402


def test_normalizes_valid_yfinance_payload():
    event = MarketNormalizer().normalize_yfinance(
        {
            "symbol": "aapl",
            "Close": "175.25",
            "Volume": "1200",
            "timestamp": "2026-05-15T10:00:00Z",
        }
    )

    assert event.symbol == "AAPL"
    assert event.price == 175.25
    assert event.volume == 1200
    assert event.source == "YFINANCE"
    assert event.currency == "USD"
    assert event.timestamp.tzinfo is not None


def test_defaults_missing_optional_fields():
    event = MarketNormalizer().normalize_yfinance(
        {"Close": 10, "timestamp": datetime(2026, 5, 15, tzinfo=timezone.utc)},
        symbol="msft",
    )

    assert event.symbol == "MSFT"
    assert event.exchange == "UNKNOWN"
    assert event.volume == 0


def test_rejects_missing_symbol():
    try:
        MarketNormalizer().normalize_yfinance({"Close": 10})
    except MarketNormalizationError as exc:
        assert "symbol" in str(exc)
    else:
        raise AssertionError("missing symbol should fail")


def test_rejects_bad_numeric_value():
    try:
        MarketNormalizer().normalize_yfinance({"symbol": "AAPL", "Close": "bad"})
    except MarketNormalizationError as exc:
        assert "invalid numeric value" in str(exc)
    else:
        raise AssertionError("bad numeric value should fail")
