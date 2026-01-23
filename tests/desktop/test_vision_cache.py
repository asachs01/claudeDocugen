"""Tests for vision_cache module."""

import time
import unittest

from docugen.desktop.vision_cache import VisionCache, CacheEntry


class TestVisionCache(unittest.TestCase):
    """Tests for VisionCache."""

    def setUp(self):
        self.cache = VisionCache(ttl_seconds=10.0, max_entries=5)

    def test_empty_cache_returns_none(self):
        result = self.cache.get(b"image_data")
        self.assertIsNone(result)
        self.assertEqual(self.cache.misses, 1)

    def test_put_and_get(self):
        elements = [{"name": "Save", "type": "button", "bounds": {"x": 10, "y": 20}}]
        self.cache.put(b"image_data", elements)

        result = self.cache.get(b"image_data")
        self.assertEqual(result, elements)
        self.assertEqual(self.cache.hits, 1)

    def test_different_images_different_entries(self):
        elem1 = [{"name": "Save"}]
        elem2 = [{"name": "Cancel"}]

        self.cache.put(b"image_1", elem1)
        self.cache.put(b"image_2", elem2)

        self.assertEqual(self.cache.get(b"image_1"), elem1)
        self.assertEqual(self.cache.get(b"image_2"), elem2)
        self.assertEqual(self.cache.size, 2)

    def test_ttl_expiry(self):
        cache = VisionCache(ttl_seconds=0.01)  # 10ms TTL
        cache.put(b"image", [{"name": "Button"}])

        # Should be available immediately
        self.assertIsNotNone(cache.get(b"image"))

        # Wait for expiry
        time.sleep(0.02)
        result = cache.get(b"image")
        self.assertIsNone(result)

    def test_max_entries_eviction(self):
        cache = VisionCache(max_entries=3)

        cache.put(b"img1", [{"name": "A"}])
        time.sleep(0.001)
        cache.put(b"img2", [{"name": "B"}])
        time.sleep(0.001)
        cache.put(b"img3", [{"name": "C"}])

        # Adding 4th should evict the oldest
        cache.put(b"img4", [{"name": "D"}])

        self.assertEqual(cache.size, 3)
        self.assertIsNone(cache.get(b"img1"))  # Evicted
        self.assertIsNotNone(cache.get(b"img2"))

    def test_clear(self):
        self.cache.put(b"img1", [{"name": "A"}])
        self.cache.put(b"img2", [{"name": "B"}])

        self.cache.clear()
        self.assertEqual(self.cache.size, 0)
        self.assertIsNone(self.cache.get(b"img1"))

    def test_stats_tracking(self):
        self.cache.put(b"img", [{"name": "A"}])

        self.cache.get(b"img")      # hit
        self.cache.get(b"img")      # hit
        self.cache.get(b"other")    # miss

        self.assertEqual(self.cache.hits, 2)
        self.assertEqual(self.cache.misses, 1)

    def test_overwrite_existing_key(self):
        self.cache.put(b"img", [{"name": "Old"}])
        self.cache.put(b"img", [{"name": "New"}])

        result = self.cache.get(b"img")
        self.assertEqual(result, [{"name": "New"}])


class TestCacheEntry(unittest.TestCase):
    """Tests for CacheEntry dataclass."""

    def test_creation(self):
        entry = CacheEntry(
            elements=[{"name": "Button"}],
            timestamp=time.time(),
            image_hash="abc123",
        )
        self.assertEqual(entry.elements, [{"name": "Button"}])
        self.assertEqual(entry.image_hash, "abc123")


if __name__ == "__main__":
    unittest.main()
