import time
from typing import Any, Optional, Dict, Tuple


class AnalyticsCache:
    """In-memory key-value cache layer serving overview, comparison, and lineage chart DTOs."""

    def __init__(self):
        self._cache: Dict[str, Tuple[Any, float]] = {}

    def get(self, key: str) -> Optional[Any]:
        if key not in self._cache:
            return None
        data, expires_at = self._cache[key]
        if time.time() > expires_at:
            del self._cache[key]
            return None
        return data

    def set(self, key: str, value: Any, ttl: int = 600) -> None:
        self._cache[key] = (value, time.time() + ttl)

    def delete(self, key: str) -> None:
        if key in self._cache:
            del self._cache[key]

    def clear(self) -> None:
        self._cache.clear()

    def invalidate_project(self, project_id: Any) -> None:
        """Evicts overview, lineage, and timeseries cached logs belonging to a target project."""
        p_id = str(project_id)
        keys_to_del = [
            k for k in self._cache.keys()
            if f":{p_id}" in k or k.startswith(f"project_overview:{p_id}") or k.startswith(f"lineage:{p_id}") or k.startswith(f"timeseries:{p_id}")
        ]
        for k in keys_to_del:
            self.delete(k)
