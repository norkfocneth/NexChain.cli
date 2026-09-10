"""
ChainSentinel Local LLM Connector
Provides local offline AI inference through Ollama (or local endpoint) using lightweight models
like Qwen2.5 (0.5B / 1.5B / 7B). Fails gracefully to offline deterministic logic if LLM is unavailable.
"""

import json
from typing import Optional, Dict, Any
import httpx

OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "qwen2.5:0.5b"
FALLBACK_MODEL = "qwen2.5vl:7b"


def is_ollama_running() -> bool:
    try:
        r = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=1.5)
        return r.status_code == 200
    except Exception:
        return False


def get_available_model() -> Optional[str]:
    try:
        r = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=1.5)
        if r.status_code == 200:
            data = r.json()
            names = [m["name"] for m in data.get("models", [])]
            for pref in [DEFAULT_MODEL, "qwen2.5:0.5b", "qwen2.5:latest", FALLBACK_MODEL]:
                for name in names:
                    if pref in name:
                        return name
            if names:
                return names[0]
    except Exception:
        pass
    return None


def query_local_llm(prompt: str, system_prompt: str = "", temperature: float = 0.2) -> Optional[str]:
    """Queries local Ollama instance for intent classification or conversational synthesis."""
    model = get_available_model()
    if not model:
        return None

    payload = {
        "model": model,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": 256
        }
    }

    try:
        r = httpx.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=6.0)
        if r.status_code == 200:
            return r.json().get("response", "").strip()
    except Exception:
        pass
    return None
