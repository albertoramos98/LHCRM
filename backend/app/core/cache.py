import time
from typing import Any, Dict, Optional, Tuple

class SimpleMemoryCache:
    def __init__(self, default_ttl: int = 60):
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self.default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            value, expires_at = self._cache[key]
            if time.time() < expires_at:
                return value
            else:
                del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        duration = ttl if ttl is not None else self.default_ttl
        expires_at = time.time() + duration
        self._cache[key] = (value, expires_at)

    def clear(self) -> None:
        self._cache.clear()

memory_cache = SimpleMemoryCache(default_ttl=60)
