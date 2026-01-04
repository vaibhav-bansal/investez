import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Any

from config import FUNDAMENTALS_CACHE_DIR, CACHE_TTL_HOURS


def get_cache_path(cache_type: str, key: str) -> Path:
    """Get the cache file path for a given type and key."""
    if cache_type == "fundamentals":
        return FUNDAMENTALS_CACHE_DIR / f"{key}.json"
    raise ValueError(f"Unknown cache type: {cache_type}")


def is_cache_valid(cache_path: Path, ttl_hours: int = CACHE_TTL_HOURS) -> bool:
    """Check if cache file exists and is within TTL."""
    if not cache_path.exists():
        return False

    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        cached_at = datetime.fromisoformat(data.get("cached_at", ""))
        expiry_time = cached_at + timedelta(hours=ttl_hours)
        return datetime.now() < expiry_time
    except (json.JSONDecodeError, ValueError, KeyError):
        return False


def get_cached(cache_type: str, key: str) -> Optional[dict]:
    """
    Get cached data if valid.
    Returns None if cache doesn't exist or is expired.
    """
    cache_path = get_cache_path(cache_type, key)

    if not is_cache_valid(cache_path):
        return None

    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("data")
    except (json.JSONDecodeError, IOError):
        return None


def set_cached(cache_type: str, key: str, data: Any) -> None:
    """Save data to cache with timestamp."""
    cache_path = get_cache_path(cache_type, key)

    cache_entry = {
        "cached_at": datetime.now().isoformat(),
        "key": key,
        "data": data
    }

    cache_path.parent.mkdir(parents=True, exist_ok=True)

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache_entry, f, indent=2, ensure_ascii=False)


def invalidate_cache(cache_type: str, key: str) -> bool:
    """Remove a specific cache entry. Returns True if removed."""
    cache_path = get_cache_path(cache_type, key)

    if cache_path.exists():
        cache_path.unlink()
        return True
    return False


def clear_expired_cache(cache_type: str) -> int:
    """Clear all expired cache entries. Returns count of removed files."""
    if cache_type == "fundamentals":
        cache_dir = FUNDAMENTALS_CACHE_DIR
    else:
        raise ValueError(f"Unknown cache type: {cache_type}")

    removed_count = 0
    for cache_file in cache_dir.glob("*.json"):
        if not is_cache_valid(cache_file):
            cache_file.unlink()
            removed_count += 1

    return removed_count
