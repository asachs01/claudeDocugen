"""Unit tests for fallback_metrics.py."""

import time

import pytest

from docugen.desktop.fallback_metrics import MetricsCollector, AggregateStats


@pytest.fixture
def collector():
    """MetricsCollector instance for testing."""
    return MetricsCollector()


def test_metrics_collection(collector):
    """Test basic metrics collection."""
    # Record some events
    collector.record_event("App1", "macos", "accessibility", True, 50.0)
    collector.record_event("App1", "macos", "accessibility", True, 60.0)
    collector.record_event("App2", "windows", "visual", True, 40.0, "timeout")
    collector.record_event("App2", "windows", "accessibility", False, 100.0)

    stats = collector.get_stats()

    assert stats.total_calls == 4
    assert stats.accessibility_success == 2
    assert stats.accessibility_failures == 1
    assert stats.visual_fallbacks == 1
    assert stats.avg_latency_ms == 62.5  # (50+60+40+100)/4
    assert stats.success_rate == 0.75  # 3 successes out of 4
    assert stats.fallback_rate == 0.25  # 1 visual out of 4


def test_fallback_reasons(collector):
    """Test tracking of fallback reasons."""
    collector.record_event("App1", "macos", "visual", True, 45.0, "permission_denied")
    collector.record_event("App2", "macos", "visual", True, 35.0, "timeout")
    collector.record_event("App3", "macos", "visual", True, 30.0, "timeout")
    collector.record_event("App4", "linux", "visual", True, 25.0, "unsupported")

    stats = collector.get_stats()

    assert stats.fallback_reasons["permission_denied"] == 1
    assert stats.fallback_reasons["timeout"] == 2
    assert stats.fallback_reasons["unsupported"] == 1


def test_app_specific_stats(collector):
    """Test app-specific statistics."""
    # Record events for different apps
    collector.record_event("AppA", "macos", "accessibility", True, 50.0)
    collector.record_event("AppA", "macos", "accessibility", True, 55.0)
    collector.record_event("AppA", "macos", "visual", True, 40.0, "timeout")

    collector.record_event("AppB", "windows", "visual", True, 30.0, "error")
    collector.record_event("AppB", "windows", "visual", True, 35.0, "error")

    # Get stats for AppA
    stats_a = collector.get_app_stats("AppA")
    assert stats_a.total_calls == 3
    assert stats_a.accessibility_success == 2
    assert stats_a.visual_fallbacks == 1
    assert stats_a.fallback_rate == 1 / 3

    # Get stats for AppB
    stats_b = collector.get_app_stats("AppB")
    assert stats_b.total_calls == 2
    assert stats_b.visual_fallbacks == 2
    assert stats_b.fallback_rate == 1.0


def test_cache_stats(collector):
    """Test cache hit/miss tracking."""
    collector.record_cache_hit()
    collector.record_cache_hit()
    collector.record_cache_miss()

    cache_stats = collector.get_cache_stats()

    assert cache_stats["hits"] == 2
    assert cache_stats["misses"] == 1
    assert cache_stats["hit_rate"] == 2 / 3


def test_reset(collector):
    """Test metrics reset."""
    collector.record_event("App1", "macos", "accessibility", True, 50.0)
    collector.record_cache_hit()

    # Verify data exists
    assert collector.get_stats().total_calls == 1
    assert collector.get_cache_stats()["hits"] == 1

    # Reset
    collector.reset()

    # Verify all cleared
    assert collector.get_stats().total_calls == 0
    assert collector.get_cache_stats()["hits"] == 0
    assert collector.get_cache_stats()["misses"] == 0


def test_empty_stats(collector):
    """Test stats with no data."""
    stats = collector.get_stats()

    assert stats.total_calls == 0
    assert stats.success_rate == 0.0
    assert stats.fallback_rate == 0.0
    assert stats.avg_latency_ms == 0.0


def test_app_stats_no_data(collector):
    """Test app-specific stats when app has no data."""
    stats = collector.get_app_stats("NonExistentApp")

    assert stats.total_calls == 0
    assert stats.success_rate == 0.0
    assert stats.fallback_rate == 0.0
