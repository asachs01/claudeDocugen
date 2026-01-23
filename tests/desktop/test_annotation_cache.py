"""Tests for element metadata caching."""

import pytest

from docugen.desktop.annotation_cache import ElementCache, make_cache_key
from docugen.desktop.element_metadata import ElementMetadata


def test_cache_basic_operations():
    """Test basic cache get/put operations."""
    cache = ElementCache(max_size=3)

    key1 = ("windows", "Chrome", 10, 20)
    element1: ElementMetadata = {
        "bounds": {"x": 100, "y": 200, "width": 50, "height": 30},
        "name": "Submit",
        "type": "button",
        "confidence": 1.0,
        "source": "accessibility",
        "app_name": "Chrome",
        "platform": "windows",
    }

    # Put and get
    cache.put(key1, element1)
    result = cache.get(key1)
    assert result == element1
    assert cache.size() == 1


def test_cache_lru_eviction():
    """Test LRU eviction when cache exceeds max_size."""
    cache = ElementCache(max_size=2)

    key1 = ("windows", "Chrome", 10, 20)
    key2 = ("windows", "Chrome", 20, 30)
    key3 = ("windows", "Chrome", 30, 40)

    element1: ElementMetadata = {
        "bounds": {"x": 100, "y": 200, "width": 50, "height": 30},
        "name": "Button1",
        "type": "button",
        "confidence": 1.0,
        "source": "accessibility",
        "app_name": "Chrome",
        "platform": "windows",
    }
    element2 = {**element1, "name": "Button2"}
    element3 = {**element1, "name": "Button3"}

    cache.put(key1, element1)
    cache.put(key2, element2)
    assert cache.size() == 2

    # Adding third should evict key1 (LRU)
    cache.put(key3, element3)
    assert cache.size() == 2
    assert cache.get(key1) is None  # Evicted
    assert cache.get(key2) == element2
    assert cache.get(key3) == element3


def test_cache_hit_rate():
    """Test cache hit rate calculation."""
    cache = ElementCache(max_size=10)

    key1 = ("windows", "Chrome", 10, 20)
    element: ElementMetadata = {
        "bounds": {"x": 100, "y": 200, "width": 50, "height": 30},
        "name": "Submit",
        "type": "button",
        "confidence": 1.0,
        "source": "accessibility",
        "app_name": "Chrome",
        "platform": "windows",
    }

    cache.put(key1, element)

    # 1 hit
    cache.get(key1)
    # 1 miss
    cache.get(("windows", "Chrome", 99, 99))

    assert cache.hit_rate() == 0.5

    # 3 more hits
    cache.get(key1)
    cache.get(key1)
    cache.get(key1)

    # 4 hits, 1 miss = 4/5 = 0.8
    assert cache.hit_rate() == 0.8


def test_cache_efficiency_80_percent():
    """Test that cache achieves >80% hit rate with repeated elements.

    Acceptance criterion AC4: Cache hit rate >80% for 50 identical elements.
    """
    cache = ElementCache(max_size=100)

    element: ElementMetadata = {
        "bounds": {"x": 100, "y": 200, "width": 50, "height": 30},
        "name": "Submit",
        "type": "button",
        "confidence": 1.0,
        "source": "accessibility",
        "app_name": "Chrome",
        "platform": "windows",
    }

    # Simulate 50 identical element queries (same coordinates)
    key = make_cache_key("windows", "Chrome", 100, 200)

    # First query = miss
    cache.put(key, element)

    # Next 49 queries = hits
    for _ in range(49):
        result = cache.get(key)
        assert result == element

    # Hit rate should be 49/50 = 98%
    assert cache.hit_rate() > 0.8
    assert cache.size() == 1  # Only 1 entry


def test_make_cache_key_coordinate_bucketing():
    """Test that make_cache_key buckets coordinates to 10px grid."""
    # Coordinates 100-109 should map to same bucket (10)
    key1 = make_cache_key("windows", "Chrome", 100, 200)
    key2 = make_cache_key("windows", "Chrome", 109, 209)
    assert key1 == key2

    # Coordinate 110 should map to different bucket (11)
    key3 = make_cache_key("windows", "Chrome", 110, 200)
    assert key1 != key3


def test_cache_clear():
    """Test cache clearing."""
    cache = ElementCache(max_size=10)

    element: ElementMetadata = {
        "bounds": {"x": 100, "y": 200, "width": 50, "height": 30},
        "name": "Submit",
        "type": "button",
        "confidence": 1.0,
        "source": "accessibility",
        "app_name": "Chrome",
        "platform": "windows",
    }

    cache.put(("windows", "Chrome", 10, 20), element)
    assert cache.size() == 1

    cache.clear()
    assert cache.size() == 0
    assert cache.hit_rate() == 0.0


def test_cache_stats():
    """Test cache statistics reporting."""
    cache = ElementCache(max_size=10)

    key1 = ("windows", "Chrome", 10, 20)
    element: ElementMetadata = {
        "bounds": {"x": 100, "y": 200, "width": 50, "height": 30},
        "name": "Submit",
        "type": "button",
        "confidence": 1.0,
        "source": "accessibility",
        "app_name": "Chrome",
        "platform": "windows",
    }

    cache.put(key1, element)
    cache.get(key1)  # Hit
    cache.get(("windows", "Chrome", 99, 99))  # Miss

    stats = cache.stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["hit_rate"] == 0.5
    assert stats["size"] == 1
