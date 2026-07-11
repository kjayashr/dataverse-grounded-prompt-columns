"""Thin Azure OpenAI chat client (httpx, already a dependency).

Used by the functional prompt-column Test. Keeps to the chat/completions REST
shape so it works with any deployment (gpt-4.1 here). Synchronous; FastAPI runs
sync routes in a threadpool.
"""
import httpx

from .config import Settings


def chat(s: Settings, messages, max_tokens: int = 220, temperature: float = 0.2) -> str:
    url = (f"{s.aoai_endpoint.rstrip('/')}/openai/deployments/{s.aoai_deployment}"
           f"/chat/completions?api-version={s.aoai_api_version}")
    r = httpx.post(
        url,
        headers={"api-key": s.aoai_key, "Content-Type": "application/json"},
        json={"messages": messages, "max_tokens": max_tokens, "temperature": temperature},
        timeout=45,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()
