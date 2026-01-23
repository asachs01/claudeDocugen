"""Unit tests for fallback_config.py."""

import os
from unittest.mock import patch

import pytest

from docugen.desktop.fallback_config import FallbackConfig


def test_config_defaults():
    """Test default configuration values."""
    config = FallbackConfig()

    assert config.timeout_ms == 100
    assert config.retry_strategy == "exponential_backoff"
    assert config.permission_handling == "auto_fallback"
    assert config.cache_ttl_seconds == 300
    assert config.max_retries == 2
    assert config.visual_fallback_enabled is True
    assert config.app_specific_rules == {}


def test_config_custom_values():
    """Test configuration with custom values."""
    config = FallbackConfig(
        timeout_ms=200,
        retry_strategy="immediate",
        permission_handling="prompt_user",
        cache_ttl_seconds=600,
        max_retries=5,
        visual_fallback_enabled=False,
        app_specific_rules={"app1": {"timeout_ms": 150}},
    )

    assert config.timeout_ms == 200
    assert config.retry_strategy == "immediate"
    assert config.permission_handling == "prompt_user"
    assert config.cache_ttl_seconds == 600
    assert config.max_retries == 5
    assert config.visual_fallback_enabled is False
    assert config.app_specific_rules == {"app1": {"timeout_ms": 150}}


def test_from_env_defaults():
    """Test loading from environment with no env vars set."""
    with patch.dict(os.environ, {}, clear=True):
        config = FallbackConfig.from_env()

        assert config.timeout_ms == 100
        assert config.retry_strategy == "exponential_backoff"
        assert config.permission_handling == "auto_fallback"
        assert config.cache_ttl_seconds == 300
        assert config.max_retries == 2
        assert config.visual_fallback_enabled is True


def test_from_env_custom():
    """Test loading from environment with custom values."""
    env_vars = {
        "FALLBACK_TIMEOUT_MS": "250",
        "FALLBACK_RETRY_STRATEGY": "none",
        "FALLBACK_PERMISSION_HANDLING": "fail",
        "FALLBACK_CACHE_TTL": "1200",
        "FALLBACK_MAX_RETRIES": "10",
        "FALLBACK_VISUAL_ENABLED": "false",
    }

    with patch.dict(os.environ, env_vars, clear=True):
        config = FallbackConfig.from_env()

        assert config.timeout_ms == 250
        assert config.retry_strategy == "none"
        assert config.permission_handling == "fail"
        assert config.cache_ttl_seconds == 1200
        assert config.max_retries == 10
        assert config.visual_fallback_enabled is False


def test_from_env_partial():
    """Test loading from environment with only some values set."""
    env_vars = {
        "FALLBACK_TIMEOUT_MS": "150",
        "FALLBACK_CACHE_TTL": "500",
    }

    with patch.dict(os.environ, env_vars, clear=True):
        config = FallbackConfig.from_env()

        assert config.timeout_ms == 150
        assert config.cache_ttl_seconds == 500
        # Others should use defaults
        assert config.retry_strategy == "exponential_backoff"
        assert config.max_retries == 2
