"""
Play Store scraper wrapper.
Calls Node.js google-play-scraper with rate limiting and caching.
"""
import json
import subprocess
import time
import random
from pathlib import Path
from datetime import datetime, timedelta

GPLAY_JS = Path(__file__).parent / "gplay_fetch.js"
NODE_BIN = "node"

# Rate limiting: min seconds between requests
MIN_DELAY = 3.0
MAX_DELAY = 6.0
_last_request_time = 0.0


def _wait():
    global _last_request_time
    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < MIN_DELAY:
        sleep_for = MIN_DELAY - elapsed + random.uniform(0, MAX_DELAY - MIN_DELAY)
        time.sleep(sleep_for)
    _last_request_time = time.time()


def _run(method: str, args: dict) -> list | dict:
    _wait()
    cmd = [NODE_BIN, str(GPLAY_JS), method, json.dumps(args)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(f"gplay error: {result.stderr.strip()}")
    data = json.loads(result.stdout.strip())
    if isinstance(data, dict) and "error" in data:
        raise RuntimeError(f"gplay API error: {data['error']}")
    return data


def fetch_list(collection: str, category: str, num: int = 100) -> list[dict]:
    """Fetch top apps for a collection+category."""
    return _run("list", {"collection": collection, "category": category, "num": num})


def fetch_app_detail(app_id: str, lang: str = "en", country: str = "us") -> dict:
    return _run("app", {"appId": app_id, "lang": lang, "country": country})


def fetch_search(term: str, num: int = 30) -> list[dict]:
    return _run("search", {"term": term, "num": num})


def fetch_reviews(app_id: str, num: int = 100, sort: str = "NEWEST") -> dict:
    return _run("reviews", {"appId": app_id, "num": num, "sort": sort})


def fetch_categories() -> list[dict]:
    return _run("categories", {})


class CacheGuard:
    """
    Simple file-based cache guard to avoid re-fetching the same data too often.
    """
    def __init__(self, cache_dir: Path = None, ttl_hours: float = 24.0):
        self.cache_dir = cache_dir or Path(__file__).parent.parent / ".cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)

    def _key(self, *parts) -> str:
        safe = "_".join(str(p).replace("/", "_") for p in parts)
        return safe

    def _path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.json"

    def get(self, *parts) -> list | dict | None:
        path = self._path(self._key(*parts))
        if not path.exists():
            return None
        mtime = datetime.fromtimestamp(path.stat().st_mtime)
        if datetime.now() - mtime > self.ttl:
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def set(self, data, *parts):
        path = self._path(self._key(*parts))
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def safe_fetch_list(collection: str, category: str, num: int = 100, cache: CacheGuard = None):
    """Fetch with caching and rate limiting."""
    cache = cache or CacheGuard()
    cached = cache.get("list", collection, category, num)
    if cached is not None:
        return cached
    data = fetch_list(collection, category, num)
    cache.set(data, "list", collection, category, num)
    return data
