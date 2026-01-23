"""Platform routing for accessibility backend selection.

Extends platform_utils with capability-based routing to connect
the capture infrastructure with platform-specific accessibility APIs.
"""

import logging
from typing import Optional, Protocol

from .platform_utils import get_os, get_platform, PlatformInfo

logger = logging.getLogger(__name__)


class AccessibilityBackend(Protocol):
    """Protocol for platform accessibility backends."""

    def get_element_at_point(self, x: int, y: int) -> Optional[dict]:
        """Get UI element metadata at screen coordinates."""
        ...

    def get_focused_element(self) -> Optional[dict]:
        """Get the currently focused UI element."""
        ...


def get_accessibility_backend() -> Optional[AccessibilityBackend]:
    """Attempt to load the platform-specific accessibility backend.

    Returns the backend instance if the platform library is available,
    or None with a logged warning if unavailable.

    Returns:
        AccessibilityBackend instance or None.
    """
    os_type = get_os()

    if os_type == "windows":
        try:
            from .windows_accessibility import WindowsAccessibility
            return WindowsAccessibility()
        except ImportError:
            logger.warning(
                "pywinauto not installed. Windows accessibility unavailable. "
                "Install with: pip install pywinauto"
            )
            return None

    elif os_type == "macos":
        try:
            from .macos_accessibility import MacOSAccessibility
            return MacOSAccessibility()
        except ImportError:
            logger.warning(
                "atomacos not installed. macOS accessibility unavailable. "
                "Install with: pip install atomacos pyobjc-framework-Cocoa"
            )
            return None

    # Linux has no accessibility backend currently
    logger.info("No accessibility backend available for %s.", os_type)
    return None


def get_capture_capabilities() -> dict:
    """Report available capture capabilities for the current platform.

    Returns:
        Dict with boolean flags for each capability:
        - screenshots: Always True (mss is required).
        - window_enumeration: True if platform window listing works.
        - accessibility: True if a backend loaded successfully.
    """
    info = get_platform()
    return {
        "screenshots": True,
        "window_enumeration": info.has_window_enumeration,
        "accessibility": info.has_accessibility,
        "os": info.os,
        "dpi_scale": info.dpi_scale,
        "notes": info.notes,
    }


def get_element_metadata(
    x: int, y: int, screenshot_path: Optional[str] = None
) -> Optional[dict]:
    """Get UI element metadata at coordinates, using best available method.

    Tries accessibility backend first. Falls back to None (caller can
    use visual analysis if needed).

    Args:
        x: Screen X coordinate.
        y: Screen Y coordinate.
        screenshot_path: Path to screenshot (for potential visual fallback).

    Returns:
        Element metadata dict or None.
    """
    backend = get_accessibility_backend()
    if backend is not None:
        element = backend.get_element_at_point(x, y)
        if element:
            element["source"] = "accessibility"
            return element

    return None
