from dataclasses import dataclass
import os
from typing import Any

import httpx


class OllamaError(RuntimeError):
    pass


@dataclass(frozen=True)
class OllamaStatus:
    available: bool
    host: str
    version: str | None = None
    error: str | None = None


class OllamaClient:
    def __init__(self, host: str | None = None, default_model: str | None = None) -> None:
        self.host = (host or os.getenv("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")
        self.default_model = default_model or os.getenv("AI_MODEL", "llama3.2:3b")
        self.status_timeout = float(os.getenv("OLLAMA_STATUS_TIMEOUT_SECONDS", "20"))
        self.model_timeout = float(os.getenv("OLLAMA_MODEL_TIMEOUT_SECONDS", "30"))
        self.chat_timeout = float(os.getenv("OLLAMA_CHAT_TIMEOUT_SECONDS", "420"))

    async def status(self) -> OllamaStatus:
        try:
            async with httpx.AsyncClient(timeout=self.status_timeout) as client:
                response = await client.get(f"{self.host}/api/version")
                response.raise_for_status()
            return OllamaStatus(
                available=True,
                host=self.host,
                version=response.json().get("version"),
            )
        except Exception as exc:
            return OllamaStatus(
                available=False,
                host=self.host,
                error=str(exc),
            )

    async def list_models(self) -> list[str]:
        async with httpx.AsyncClient(timeout=self.model_timeout) as client:
            response = await client.get(f"{self.host}/api/tags")
            response.raise_for_status()
        models = response.json().get("models", [])
        return [model["name"] for model in models if model.get("name")]

    async def chat(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        model: str | None = None,
        temperature: float = 0.2,
    ) -> dict[str, Any]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }

        try:
            async with httpx.AsyncClient(timeout=self.chat_timeout) as client:
                response = await client.post(f"{self.host}/api/chat", json=payload)
                response.raise_for_status()
        except Exception as exc:
            raise OllamaError(str(exc)) from exc

        body = response.json()
        return {
            "model": body.get("model", payload["model"]),
            "content": body.get("message", {}).get("content", ""),
            "done": body.get("done", False),
            "provider": "ollama",
        }
