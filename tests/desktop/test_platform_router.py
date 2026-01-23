"""Tests for platform_router module."""

import unittest
from unittest.mock import patch, MagicMock


class TestGetAccessibilityBackend(unittest.TestCase):
    """Tests for get_accessibility_backend function."""

    @patch("docugen.desktop.platform_router.get_os", return_value="windows")
    def test_windows_no_pywinauto(self, mock_os):
        """Returns None when windows_accessibility module unavailable."""
        from docugen.desktop.platform_router import get_accessibility_backend
        result = get_accessibility_backend()
        self.assertIsNone(result)

    @patch("docugen.desktop.platform_router.get_os", return_value="macos")
    def test_macos_no_atomacos(self, mock_os):
        """Returns None with warning when atomacos unavailable."""
        from docugen.desktop.platform_router import get_accessibility_backend
        result = get_accessibility_backend()
        self.assertIsNone(result)

    @patch("docugen.desktop.platform_router.get_os", return_value="linux")
    def test_linux_no_backend(self, mock_os):
        """Returns None for Linux (no accessibility backend)."""
        from docugen.desktop.platform_router import get_accessibility_backend
        result = get_accessibility_backend()
        self.assertIsNone(result)


class TestGetCaptureCapabilities(unittest.TestCase):
    """Tests for get_capture_capabilities function."""

    @patch("docugen.desktop.platform_router.get_platform")
    def test_returns_capabilities_dict(self, mock_platform):
        from docugen.desktop.platform_router import get_capture_capabilities
        from docugen.desktop.platform_utils import PlatformInfo

        mock_platform.return_value = PlatformInfo(
            os="macos",
            version="14.0",
            dpi_scale=2.0,
            has_accessibility=False,
            has_window_enumeration=True,
            notes=["test note"],
        )

        caps = get_capture_capabilities()

        self.assertTrue(caps["screenshots"])
        self.assertTrue(caps["window_enumeration"])
        self.assertFalse(caps["accessibility"])
        self.assertEqual(caps["os"], "macos")
        self.assertEqual(caps["dpi_scale"], 2.0)
        self.assertEqual(caps["notes"], ["test note"])

    @patch("docugen.desktop.platform_router.get_platform")
    def test_screenshots_always_true(self, mock_platform):
        from docugen.desktop.platform_router import get_capture_capabilities
        from docugen.desktop.platform_utils import PlatformInfo

        mock_platform.return_value = PlatformInfo(
            os="linux", version="5.15", has_window_enumeration=False
        )

        caps = get_capture_capabilities()
        self.assertTrue(caps["screenshots"])


class TestGetElementMetadata(unittest.TestCase):
    """Tests for get_element_metadata function."""

    @patch("docugen.desktop.platform_router.get_accessibility_backend")
    def test_returns_none_when_no_backend(self, mock_get_backend):
        from docugen.desktop.platform_router import get_element_metadata

        mock_get_backend.return_value = None
        result = get_element_metadata(100, 200)
        self.assertIsNone(result)

    @patch("docugen.desktop.platform_router.get_accessibility_backend")
    def test_returns_element_with_source_tag(self, mock_get_backend):
        from docugen.desktop.platform_router import get_element_metadata

        mock_backend = MagicMock()
        mock_backend.get_element_at_point.return_value = {
            "name": "OK Button",
            "control_type": "Button",
            "bounds": {"x": 100, "y": 200, "width": 80, "height": 30},
        }
        mock_get_backend.return_value = mock_backend

        result = get_element_metadata(100, 200)
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "OK Button")
        self.assertEqual(result["source"], "accessibility")

    @patch("docugen.desktop.platform_router.get_accessibility_backend")
    def test_returns_none_when_backend_finds_nothing(self, mock_get_backend):
        from docugen.desktop.platform_router import get_element_metadata

        mock_backend = MagicMock()
        mock_backend.get_element_at_point.return_value = None
        mock_get_backend.return_value = mock_backend

        result = get_element_metadata(100, 200)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
