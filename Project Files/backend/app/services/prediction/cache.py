import hashlib
import json
import asyncio
from typing import Any, Dict, Optional, Tuple


class PredictionCache:
    """Computes SHA-256 prediction hashes for idempotency and response caching checks."""

    def compute_request_hash(self, payload: Any) -> str:
        serialized = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode()).hexdigest()

    def compile_prediction_cache_key(self, model_checksum: str, prep_hash: str, request_hash: str) -> str:
        return f"pred:{model_checksum}:{prep_hash}:{request_hash}"


class WarmModelCache:
    """In-memory cache for loaded model estimators and preprocessors with lifecycle states."""

    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._hits = 0
        self._misses = 0

    def get_stats(self) -> Dict[str, int]:
        return {
            "hits": self._hits,
            "misses": self._misses,
            "cache_size": len(self._cache)
        }

    async def get_or_load(self, key: str, load_func) -> Any:
        if key in self._cache:
            entry = self._cache[key]
            if entry["state"] == "READY":
                self._hits += 1
                return entry["value"]
            elif entry["state"] == "LOADING":
                self._hits += 1
                await entry["event"].wait()
                if entry["state"] == "READY":
                    return entry["value"]
                raise RuntimeError("Failed to load warm model from concurrent request task.")

        self._misses += 1
        event = asyncio.Event()
        self._cache[key] = {
            "state": "LOADING",
            "value": None,
            "event": event
        }
        
        try:
            val = await load_func()
            self._cache[key]["value"] = val
            self._cache[key]["state"] = "READY"
            event.set()
            return val
        except Exception as e:
            self._cache[key]["state"] = "EVICTED"
            event.set()
            if key in self._cache:
                del self._cache[key]
            raise e

    def evict(self, key: str) -> None:
        if key in self._cache:
            self._cache[key]["state"] = "EVICTED"
            del self._cache[key]

    def clear(self) -> None:
        self._cache.clear()
