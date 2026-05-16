from pathlib import Path
import os
import sys

from fastapi.testclient import TestClient


API_PATH = Path(__file__).resolve().parents[1]
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
sys.path.insert(0, str(API_PATH))

from main import app  # noqa: E402


client = TestClient(app)

health = client.get("/health")
assert health.status_code == 200, health.text
assert health.json()["status"] == "ok"

openapi = client.get("/openapi.json")
assert openapi.status_code == 200, openapi.text

quote = client.get("/api/markets/quotes/AAPL")
assert quote.status_code == 200, quote.text
assert quote.json()["symbol"] == "AAPL"

print("api smoke ok")
