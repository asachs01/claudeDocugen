"""Tests for windows_accessibility module."""

import sys
import unittest
from unittest.mock import MagicMock, patch, PropertyMock

# Create fake pywinauto module for testing on non-Windows systems
_mock_pywinauto = MagicMock()
_mock_pywinauto.Desktop = MagicMock()
sys.modules.setdefault("pywinauto", _mock_pywinauto)


class TestExtractElementDict(unittest.TestCase):
    """Tests for _extract_element_dict helper."""

    def _make_element(self, name="OK", control_type="Button",
                      automation_id="btn_ok", rect=None, enabled=True,
                      visible=True):
        """Create a mock pywinauto element."""
        element = MagicMock()
        element.window_text.return_value = name

        info = MagicMock()
        info.name = name
        info.control_type = control_type
        info.automation_id = automation_id
        info.enabled = enabled
        info.visible = visible

        if rect is None:
            rect = MagicMock()
            rect.left = 100
            rect.top = 200
            rect.right = 250
            rect.bottom = 240
        info.rectangle = rect

        element.element_info = info
        return element

    def test_basic_extraction(self):
        from docugen.desktop.windows_accessibility import _extract_element_dict

        element = self._make_element()
        result = _extract_element_dict(element)

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "OK")
        self.assertEqual(result["role"], "Button")
        self.assertEqual(result["identifier"], "btn_ok")
        self.assertEqual(result["source"], "accessibility")
        self.assertEqual(result["bounds"], {
            "x": 100, "y": 200, "width": 150, "height": 40,
        })

    def test_no_automation_id_generates_from_role_title(self):
        from docugen.desktop.windows_accessibility import _extract_element_dict

        element = self._make_element(automation_id="")
        result = _extract_element_dict(element)

        self.assertEqual(result["identifier"], "Button_OK")

    def test_missing_rect_returns_none(self):
        from docugen.desktop.windows_accessibility import _extract_element_dict

        element = self._make_element()
        type(element.element_info).rectangle = PropertyMock(
            side_effect=Exception("no rect")
        )
        result = _extract_element_dict(element)
        self.assertIsNone(result)

    def test_properties_included(self):
        from docugen.desktop.windows_accessibility import _extract_element_dict

        element = self._make_element(enabled=True, visible=True)
        result = _extract_element_dict(element)

        self.assertIn("properties", result)
        self.assertTrue(result["properties"]["enabled"])
        self.assertTrue(result["properties"]["visible"])

    def test_window_text_fallback_to_name(self):
        from docugen.desktop.windows_accessibility import _extract_element_dict

        element = self._make_element(name="Fallback Name")
        element.window_text.side_effect = Exception("no text")
        result = _extract_element_dict(element)

        self.assertEqual(result["title"], "Fallback Name")


class TestQueryWithTimeout(unittest.TestCase):
    """Tests for _query_with_timeout helper."""

    def test_fast_query_returns_result(self):
        from docugen.desktop.windows_accessibility import _query_with_timeout

        result = _query_with_timeout(lambda: 42, timeout_sec=1.0)
        self.assertEqual(result, 42)

    def test_exception_propagated(self):
        from docugen.desktop.windows_accessibility import _query_with_timeout

        def raise_error():
            raise ValueError("test error")

        with self.assertRaises(ValueError):
            _query_with_timeout(raise_error, timeout_sec=1.0)

    def test_slow_query_returns_none(self):
        import time
        from docugen.desktop.windows_accessibility import _query_with_timeout

        def slow():
            time.sleep(2)
            return "too late"

        result = _query_with_timeout(slow, timeout_sec=0.05)
        self.assertIsNone(result)


class TestWindowsAccessibility(unittest.TestCase):
    """Tests for WindowsAccessibility class."""

    @patch("pywinauto.Desktop")
    def test_init_creates_desktop(self, mock_desktop_cls):
        from docugen.desktop.windows_accessibility import WindowsAccessibility

        wa = WindowsAccessibility()
        mock_desktop_cls.assert_called_once_with(backend="uia")

    @patch("pywinauto.Desktop")
    def test_get_element_at_point_negative_coords(self, mock_desktop_cls):
        from docugen.desktop.windows_accessibility import WindowsAccessibility

        wa = WindowsAccessibility()
        result = wa.get_element_at_point(-1, -1)
        self.assertIsNone(result)

    @patch("pywinauto.Desktop")
    def test_get_element_at_point_success(self, mock_desktop_cls):
        from docugen.desktop.windows_accessibility import WindowsAccessibility

        # Set up mock element
        mock_element = MagicMock()
        mock_element.window_text.return_value = "Save"
        info = MagicMock()
        info.name = "Save"
        info.control_type = "Button"
        info.automation_id = "btn_save"
        info.enabled = True
        info.visible = True
        rect = MagicMock()
        rect.left, rect.top, rect.right, rect.bottom = 50, 60, 120, 90
        info.rectangle = rect
        mock_element.element_info = info

        mock_desktop = MagicMock()
        mock_desktop.from_point.return_value = mock_element
        mock_desktop_cls.return_value = mock_desktop

        wa = WindowsAccessibility()
        result = wa.get_element_at_point(80, 75)

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "Save")
        self.assertEqual(result["role"], "Button")
        self.assertEqual(result["bounds"]["x"], 50)
        self.assertEqual(result["source"], "accessibility")

    @patch("pywinauto.Desktop")
    def test_get_focused_element(self, mock_desktop_cls):
        from docugen.desktop.windows_accessibility import WindowsAccessibility

        mock_focused = MagicMock()
        mock_focused.window_text.return_value = "SearchBox"
        info = MagicMock()
        info.name = "SearchBox"
        info.control_type = "Edit"
        info.automation_id = "search"
        info.enabled = True
        info.visible = True
        rect = MagicMock()
        rect.left, rect.top, rect.right, rect.bottom = 10, 20, 200, 50
        info.rectangle = rect
        mock_focused.element_info = info

        mock_window = MagicMock()
        mock_window.get_focus.return_value = mock_focused
        mock_desktop = MagicMock()
        mock_desktop.top_window.return_value = mock_window
        mock_desktop_cls.return_value = mock_desktop

        wa = WindowsAccessibility()
        result = wa.get_focused_element()

        self.assertIsNotNone(result)
        self.assertEqual(result["role"], "Edit")
        self.assertEqual(result["title"], "SearchBox")

    @patch("pywinauto.Desktop")
    def test_get_focused_element_no_focus(self, mock_desktop_cls):
        from docugen.desktop.windows_accessibility import WindowsAccessibility

        mock_window = MagicMock()
        mock_window.get_focus.return_value = None
        mock_desktop = MagicMock()
        mock_desktop.top_window.return_value = mock_window
        mock_desktop_cls.return_value = mock_desktop

        wa = WindowsAccessibility()
        result = wa.get_focused_element()
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
