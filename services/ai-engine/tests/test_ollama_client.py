from pathlib import Path
import sys


AI_ENGINE_PATH = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AI_ENGINE_PATH))

from ollama_client import OllamaClient


def test_default_model_can_be_overridden():
    client = OllamaClient(host="http://example.test", default_model="custom-model")
    assert client.host == "http://example.test"
    assert client.default_model == "custom-model"
