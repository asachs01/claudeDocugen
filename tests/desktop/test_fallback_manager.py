"""Unit tests for fallback_manager.py."""

import time
from unittest.mock import patch, MagicMock

import pytest

from docugen.desktop.fallback_manager import (
    FallbackManager,
    ElementMetadata,
    get_element_metadata_with_fallback,
)
from docugen.desktop.fallback_config import FallbackConfig
from docugen.desktop.timeout_wrapper import TimeoutError


@pytest.fixture
def config():
    """Test configuration with short timeouts."""
    return FallbackConfig(
        timeout_ms=100,
        cache_ttl_seconds=5,
        max_retries=2,
        visual_fallback_enabled=True,
    )


@pytest.fixture
def manager(config):
    """FallbackManager instance for testing."""
    return FallbackManager(config)


def test_element_metadata_structure():
    """Verify ElementMetadata has all required fields."""
    metadata = ElementMetadata(
        name="Submit Button",
        type="button",
        bounds={"x": 100, "y": 200, "width": 80, "height": 30},
        confidence_score=0.9,
        source="accessibility",
        fallback_used=False,
        fallback_reason=None,
    )

    assert metadata.name == "Submit Button"
    assert metadata.type == "button"
    assert metadata.bounds == {"x": 100, "y": 200, "width": 80, "height": 30}
    assert metadata.confidence_score == 0.9
    assert metadata.source == "accessibility"
    assert metadata.fallback_used is False
    assert metadata.fallback_reason is None

    # Test to_dict conversion
    result_dict = metadata.to_dict()
    assert result_dict["name"] == "Submit Button"
    assert result_dict["confidence"] == 0.9
    assert result_dict["source"] == "accessibility"


@patch("docugen.desktop.fallback_manager.check_accessibility_permission")
@patch("docugen.desktop.platform_router.get_accessibility_backend")
def test_permission_denied_triggers_fallback(
    mock_backend, mock_permission, manager
):
    """Test that macOS permission denied triggers visual fallback."""
    # Simulate permission denied
    mock_permission.return_value = False

    # Mock visual fallback
    with patch("docugen.desktop.fallback_manager.analyze_with_fallback") as mock_visual:
        mock_visual.return_value = {
            "name": "Button",
            "type": "button",
            "bounds": {"x": 10, "y": 20, "width": 50, "height": 30},
            "confidence": 0.6,
            "source": "visual",
        }

        result = manager.get_element_metadata_with_fallback(
            x=10, y=20, platform="macos", screenshot_path="/tmp/test.png"
        )

        assert result is not None
        assert result.source == "visual"
        assert result.fallback_used is True
        assert result.fallback_reason == "error"  # Permission check fails before timeout
        mock_visual.assert_called_once()


@patch("docugen.desktop.platform_router.get_accessibility_backend")
def test_timeout_triggers_fallback(mock_backend, manager):
    """Test that accessibility API timeout triggers visual fallback."""
    # Mock slow backend that exceeds timeout
    mock_backend_instance = MagicMock()
    mock_backend.return_value = mock_backend_instance

    def slow_get_element(x, y):
        time.sleep(0.2)  # Exceed 100ms timeout
        return {"name": "Slow", "type": "button"}

    mock_backend_instance.get_element_at_point.side_effect = slow_get_element

    with patch("docugen.desktop.fallback_manager.analyze_with_fallback") as mock_visual:
        mock_visual.return_value = {
            "name": "Fast Visual",
            "type": "button",
            "bounds": {"x": 100, "y": 100, "width": 50, "height": 30},
            "confidence": 0.5,
            "source": "visual",
        }

        result = manager.get_element_metadata_with_fallback(
            x=100, y=100, platform="macos", screenshot_path="/tmp/test.png"
        )

        assert result is not None
        assert result.source == "visual"
        assert result.name == "Fast Visual"
        assert result.fallback_used is True
        mock_visual.assert_called_once()


@patch("docugen.desktop.platform_router.get_accessibility_backend")
def test_exception_handling(mock_backend, manager):
    """Test that accessibility API exceptions trigger graceful fallback."""
    mock_backend_instance = MagicMock()
    mock_backend.return_value = mock_backend_instance

    # Simulate various exceptions
    exceptions = [
        Exception("COM Error"),
        RuntimeError("RPC Failure"),
        ValueError("AX API Error"),
    ]

    for exc in exceptions:
        mock_backend_instance.get_element_at_point.side_effect = exc

        with patch("docugen.desktop.fallback_manager.analyze_with_fallback") as mock_visual:
            mock_visual.return_value = {
                "name": "Fallback",
                "type": "button",
                "bounds": {"x": 50, "y": 50, "width": 40, "height": 25},
                "confidence": 0.6,
            }

            result = manager.get_element_metadata_with_fallback(
                x=50, y=50, platform="windows", screenshot_path="/tmp/test.png"
            )

            assert result is not None
            assert result.source == "visual"
            assert result.fallback_used is True


@patch("docugen.desktop.platform_router.get_accessibility_backend")
def test_app_cache_behavior(mock_backend, manager):
    """Test that apps without accessibility support are cached."""
    mock_backend_instance = MagicMock()
    mock_backend.return_value = mock_backend_instance
    mock_backend_instance.get_element_at_point.side_effect = Exception("Element not found")

    with patch("docugen.desktop.fallback_manager.analyze_with_fallback") as mock_visual:
        mock_visual.return_value = {
            "name": "Cached",
            "type": "button",
            "bounds": {"x": 30, "y": 40, "width": 60, "height": 35},
            "confidence": 0.7,
        }

        # First call should try accessibility
        result1 = manager.get_element_metadata_with_fallback(
            x=30, y=40, platform="macos", screenshot_path="/tmp/test.png", app_name="TestApp"
        )
        assert result1.fallback_used is True

        # Reset mock to verify second call behavior
        mock_backend_instance.get_element_at_point.reset_mock()

        # Second call should skip accessibility (cached as unsupported)
        result2 = manager.get_element_metadata_with_fallback(
            x=30, y=40, platform="macos", screenshot_path="/tmp/test.png", app_name="TestApp"
        )

        # Should use cached result and skip accessibility backend
        assert result2.fallback_used is True
        assert result2.source == "visual"


@patch("docugen.desktop.platform_router.get_accessibility_backend")
def test_exponential_backoff(mock_backend, config):
    """Test exponential backoff after repeated timeouts."""
    config.max_retries = 2
    manager = FallbackManager(config)

    mock_backend_instance = MagicMock()
    mock_backend.return_value = mock_backend_instance

    def timeout_func(x, y):
        time.sleep(0.2)  # Exceed timeout
        return None

    mock_backend_instance.get_element_at_point.side_effect = timeout_func

    with patch("docugen.desktop.fallback_manager.analyze_with_fallback") as mock_visual:
        mock_visual.return_value = {
            "name": "Visual",
            "type": "button",
            "bounds": {"x": 10, "y": 10, "width": 50, "height": 30},
        }

        # First timeout
        manager.get_element_metadata_with_fallback(
            x=10, y=10, platform="macos", screenshot_path="/tmp/test.png", app_name="SlowApp"
        )

        # Second timeout
        manager.get_element_metadata_with_fallback(
            x=10, y=10, platform="macos", screenshot_path="/tmp/test.png", app_name="SlowApp"
        )

        # Third call should skip accessibility entirely due to exponential backoff
        mock_backend_instance.get_element_at_point.reset_mock()
        result = manager.get_element_metadata_with_fallback(
            x=10, y=10, platform="macos", screenshot_path="/tmp/test.png", app_name="SlowApp"
        )

        # Should have skipped accessibility backend
        mock_backend_instance.get_element_at_point.assert_not_called()
        assert result.source == "visual"


def test_config_loading():
    """Test that configuration options are correctly applied."""
    config = FallbackConfig(
        timeout_ms=200,
        cache_ttl_seconds=600,
        max_retries=5,
        visual_fallback_enabled=False,
    )

    manager = FallbackManager(config)
    assert manager._config.timeout_ms == 200
    assert manager._config.cache_ttl_seconds == 600
    assert manager._config.max_retries == 5
    assert manager._config.visual_fallback_enabled is False


@patch("docugen.desktop.platform_router.get_accessibility_backend")
def test_successful_accessibility_api(mock_backend, manager):
    """Test successful accessibility API call returns correct metadata."""
    mock_backend_instance = MagicMock()
    mock_backend.return_value = mock_backend_instance
    mock_backend_instance.get_element_at_point.return_value = {
        "name": "Login Button",
        "type": "button",
        "bounds": {"x": 150, "y": 250, "width": 100, "height": 40},
        "confidence": 0.95,
    }

    result = manager.get_element_metadata_with_fallback(
        x=150, y=250, platform="windows"
    )

    assert result is not None
    assert result.name == "Login Button"
    assert result.type == "button"
    assert result.source == "accessibility"
    assert result.fallback_used is False
    assert result.confidence_score == 0.95


def test_convenience_function():
    """Test module-level convenience function."""
    with patch("docugen.desktop.fallback_manager.FallbackManager") as mock_manager_class:
        mock_instance = MagicMock()
        mock_manager_class.return_value = mock_instance
        mock_instance.get_element_metadata_with_fallback.return_value = ElementMetadata(
            name="Test",
            type="button",
            bounds={"x": 0, "y": 0, "width": 10, "height": 10},
            confidence_score=0.8,
            source="accessibility",
            fallback_used=False,
        )

        result = get_element_metadata_with_fallback(x=100, y=200, platform="macos")

        assert result is not None
        mock_instance.get_element_metadata_with_fallback.assert_called_once()
