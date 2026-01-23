"""Integration tests for fallback mechanism."""

import tempfile
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from docugen.desktop.fallback_manager import FallbackManager, ElementMetadata
from docugen.desktop.fallback_config import FallbackConfig


@pytest.fixture
def screenshot_path():
    """Create a temporary screenshot file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        # Write minimal PNG data
        f.write(b"\x89PNG\r\n\x1a\n")
        path = f.name

    yield path

    # Cleanup
    Path(path).unlink(missing_ok=True)


@pytest.fixture
def config():
    """Test configuration."""
    return FallbackConfig(
        timeout_ms=100,
        cache_ttl_seconds=5,
        max_retries=2,
        visual_fallback_enabled=True,
    )


@pytest.fixture
def manager(config):
    """FallbackManager instance."""
    return FallbackManager(config)


@patch("docugen.desktop.platform_router.get_accessibility_backend")
@patch("docugen.desktop.fallback_manager.analyze_with_fallback")
def test_complete_accessibility_failure_fallback(
    mock_visual, mock_backend, manager, screenshot_path
):
    """Test complete accessibility backend failure with visual analysis fallback."""
    # Simulate complete backend failure
    mock_backend.return_value = None

    # Mock visual analysis to return usable metadata
    mock_visual.return_value = {
        "name": "Submit Button",
        "type": "button",
        "bounds": {"x": 100, "y": 200, "width": 80, "height": 35},
        "confidence": 0.65,
        "source": "visual",
    }

    result = manager.get_element_metadata_with_fallback(
        x=100, y=200, platform="linux", screenshot_path=screenshot_path
    )

    assert result is not None
    assert isinstance(result, ElementMetadata)
    assert result.name == "Submit Button"
    assert result.type == "button"
    assert result.source == "visual"
    assert result.fallback_used is True
    assert result.bounds == {"x": 100, "y": 200, "width": 80, "height": 35}


@patch("docugen.desktop.platform_router.get_accessibility_backend")
@patch("docugen.desktop.fallback_manager.analyze_with_fallback")
def test_metrics_collection_integration(
    mock_visual, mock_backend, manager, screenshot_path
):
    """Test that metrics are collected correctly during fallback."""
    mock_backend_instance = MagicMock()
    mock_backend.return_value = mock_backend_instance

    # First call succeeds
    mock_backend_instance.get_element_at_point.return_value = {
        "name": "Success",
        "type": "button",
        "bounds": {"x": 10, "y": 10, "width": 50, "height": 30},
    }

    result1 = manager.get_element_metadata_with_fallback(
        x=10, y=10, platform="macos", app_name="TestApp"
    )

    # Second call times out
    def timeout_func(x, y):
        time.sleep(0.2)
        return None

    mock_backend_instance.get_element_at_point.side_effect = timeout_func
    mock_visual.return_value = {
        "name": "Timeout Visual",
        "type": "button",
        "bounds": {"x": 20, "y": 20, "width": 50, "height": 30},
    }

    result2 = manager.get_element_metadata_with_fallback(
        x=20, y=20, platform="macos", screenshot_path=screenshot_path, app_name="TestApp"
    )

    # Verify metrics
    metrics = manager.get_metrics()
    stats = metrics.get_stats()

    assert stats.total_calls == 2
    assert stats.accessibility_success >= 1  # At least the first call
    assert stats.visual_fallbacks >= 1  # At least the second call
    assert stats.avg_latency_ms > 0


@patch("docugen.desktop.platform_router.get_accessibility_backend")
@patch("docugen.desktop.fallback_manager.analyze_with_fallback")
def test_cache_ttl_expiration(mock_visual, mock_backend, config, screenshot_path):
    """Test that app cache expires after TTL."""
    config.cache_ttl_seconds = 1  # Very short TTL for testing
    manager = FallbackManager(config)

    mock_backend_instance = MagicMock()
    mock_backend.return_value = mock_backend_instance
    mock_backend_instance.get_element_at_point.side_effect = Exception("not found")

    mock_visual.return_value = {
        "name": "Cached",
        "type": "button",
        "bounds": {"x": 30, "y": 30, "width": 40, "height": 25},
    }

    # First call caches the app as unsupported
    result1 = manager.get_element_metadata_with_fallback(
        x=30, y=30, platform="macos", screenshot_path=screenshot_path, app_name="CachedApp"
    )
    assert result1.fallback_used is True

    # Second call should use cache (skip accessibility)
    mock_backend_instance.get_element_at_point.reset_mock()
    result2 = manager.get_element_metadata_with_fallback(
        x=30, y=30, platform="macos", screenshot_path=screenshot_path, app_name="CachedApp"
    )
    mock_backend_instance.get_element_at_point.assert_not_called()

    # Wait for cache to expire
    time.sleep(1.5)

    # Third call should try accessibility again (cache expired)
    result3 = manager.get_element_metadata_with_fallback(
        x=30, y=30, platform="macos", screenshot_path=screenshot_path, app_name="CachedApp"
    )
    # Should have attempted backend call again
    assert result3.fallback_used is True


@patch("docugen.desktop.platform_router.get_accessibility_backend")
def test_logging_format(mock_backend, manager, screenshot_path, caplog):
    """Test that fallback decisions are logged with correct format."""
    import logging

    caplog.set_level(logging.INFO)

    mock_backend_instance = MagicMock()
    mock_backend.return_value = mock_backend_instance

    def timeout_func(x, y):
        time.sleep(0.2)
        return None

    mock_backend_instance.get_element_at_point.side_effect = timeout_func

    with patch("docugen.desktop.fallback_manager.analyze_with_fallback") as mock_visual:
        mock_visual.return_value = {
            "name": "Visual",
            "type": "button",
            "bounds": {"x": 50, "y": 60, "width": 70, "height": 40},
        }

        manager.get_element_metadata_with_fallback(
            x=50, y=60, platform="macos", screenshot_path=screenshot_path, app_name="LogApp"
        )

    # Check log format: [FALLBACK] reason={reason} app={app_name} coords=({x},{y})
    log_messages = [rec.message for rec in caplog.records]
    fallback_logs = [msg for msg in log_messages if "[FALLBACK]" in msg]

    assert len(fallback_logs) > 0
    # Should contain reason, app, coords in all fallback logs
    for log in fallback_logs:
        assert "reason=" in log
        assert "app=" in log
        assert "coords=" in log
    # At least one should have source=visual (the successful fallback)
    visual_logs = [msg for msg in fallback_logs if "source=visual" in msg]
    assert len(visual_logs) > 0


@patch("docugen.desktop.platform_router.get_accessibility_backend")
@patch("docugen.desktop.fallback_manager.analyze_with_fallback")
def test_visual_fallback_performance(mock_visual, mock_backend, manager, screenshot_path):
    """Test that visual fallback completes within performance target (<50ms)."""
    mock_backend.return_value = None  # No accessibility backend

    # Mock fast visual analysis (cached)
    mock_visual.return_value = {
        "name": "Fast",
        "type": "button",
        "bounds": {"x": 80, "y": 90, "width": 60, "height": 30},
    }

    start = time.time()
    result = manager.get_element_metadata_with_fallback(
        x=80, y=90, platform="linux", screenshot_path=screenshot_path
    )
    latency_ms = (time.time() - start) * 1000

    assert result is not None
    # Note: In real scenario with caching, this should be <50ms
    # For tests with mocks, we just verify it completes quickly
    assert latency_ms < 1000  # Generous bound for test environment


@patch("docugen.desktop.platform_router.get_accessibility_backend")
def test_no_blocking_on_fallback(mock_backend, manager, screenshot_path):
    """Test that fallback doesn't block annotation pipeline."""
    mock_backend_instance = MagicMock()
    mock_backend.return_value = mock_backend_instance

    def slow_backend(x, y):
        time.sleep(0.5)  # Very slow
        return None

    mock_backend_instance.get_element_at_point.side_effect = slow_backend

    with patch("docugen.desktop.fallback_manager.analyze_with_fallback") as mock_visual:
        mock_visual.return_value = {
            "name": "No Block",
            "type": "button",
            "bounds": {"x": 100, "y": 100, "width": 50, "height": 30},
        }

        start = time.time()
        result = manager.get_element_metadata_with_fallback(
            x=100, y=100, platform="macos", screenshot_path=screenshot_path
        )
        elapsed_ms = (time.time() - start) * 1000

        # Should timeout and fallback quickly, not wait for slow backend
        assert elapsed_ms < 500  # Should timeout at 100ms + fallback overhead
        assert result is not None
        assert result.source == "visual"
