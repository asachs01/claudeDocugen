"""Tests for the desktop capture infrastructure."""

import unittest
from unittest.mock import patch, MagicMock, PropertyMock
from collections import namedtuple

# Mock platform-specific modules before importing our code
import sys

sys.modules["win32gui"] = MagicMock()
sys.modules["win32process"] = MagicMock()
sys.modules["win32api"] = MagicMock()
sys.modules["Quartz"] = MagicMock()
sys.modules["Xlib"] = MagicMock()
sys.modules["Xlib.display"] = MagicMock()
sys.modules["Xlib.X"] = MagicMock()
sys.modules["Xlib.error"] = MagicMock()


class TestPlatformUtils(unittest.TestCase):
    """Tests for platform detection and capability reporting."""

    @patch("docugen.desktop.platform_utils.platform.system")
    def test_get_os_windows(self, mock_system):
        from docugen.desktop.platform_utils import get_os

        mock_system.return_value = "Windows"
        self.assertEqual(get_os(), "windows")

    @patch("docugen.desktop.platform_utils.platform.system")
    def test_get_os_macos(self, mock_system):
        from docugen.desktop.platform_utils import get_os

        mock_system.return_value = "Darwin"
        self.assertEqual(get_os(), "macos")

    @patch("docugen.desktop.platform_utils.platform.system")
    def test_get_os_linux(self, mock_system):
        from docugen.desktop.platform_utils import get_os

        mock_system.return_value = "Linux"
        self.assertEqual(get_os(), "linux")

    @patch("docugen.desktop.platform_utils.platform.system")
    def test_get_os_unsupported(self, mock_system):
        from docugen.desktop.platform_utils import get_os

        mock_system.return_value = "FreeBSD"
        with self.assertRaises(NotImplementedError):
            get_os()

    @patch("docugen.desktop.platform_utils.platform.system")
    def test_get_platform_returns_platform_info(self, mock_system):
        from docugen.desktop.platform_utils import get_platform, PlatformInfo

        mock_system.return_value = "Darwin"
        info = get_platform()
        self.assertIsInstance(info, PlatformInfo)
        self.assertEqual(info.os, "macos")

    @patch("docugen.desktop.platform_utils.platform.system")
    def test_get_dpi_scale_defaults_to_1(self, mock_system):
        from docugen.desktop.platform_utils import get_dpi_scale

        mock_system.return_value = "Linux"
        self.assertEqual(get_dpi_scale(), 1.0)


class TestMonitorManager(unittest.TestCase):
    """Tests for MonitorManager with lazy loading."""

    def setUp(self):
        self.mock_monitors = [
            {"left": 0, "top": 0, "width": 3840, "height": 2160},  # virtual
            {"left": 0, "top": 0, "width": 1920, "height": 1080},  # monitor 1
            {"left": 1920, "top": 0, "width": 1280, "height": 720},  # monitor 2
        ]

    @patch("docugen.desktop.monitor_manager.get_dpi_scale", return_value=1.0)
    @patch("mss.mss")
    def test_lazy_loading(self, mock_mss, mock_dpi):
        from docugen.desktop.monitor_manager import MonitorManager

        mock_sct = mock_mss.return_value.__enter__.return_value
        mock_sct.monitors = self.mock_monitors

        manager = MonitorManager()
        # No mss call until we access monitors
        mock_mss.assert_not_called()

        # Access triggers load
        monitors = manager.monitors
        self.assertEqual(len(monitors), 2)  # Only individual monitors, not virtual

    @patch("docugen.desktop.monitor_manager.get_dpi_scale", return_value=1.0)
    @patch("mss.mss")
    def test_primary_monitor(self, mock_mss, mock_dpi):
        from docugen.desktop.monitor_manager import MonitorManager

        mock_sct = mock_mss.return_value.__enter__.return_value
        mock_sct.monitors = self.mock_monitors

        manager = MonitorManager()
        primary = manager.primary
        self.assertIsNotNone(primary)
        self.assertTrue(primary.is_primary)
        self.assertEqual(primary.width, 1920)

    @patch("docugen.desktop.monitor_manager.get_dpi_scale", return_value=2.0)
    @patch("mss.mss")
    def test_dpi_scale_logical_dimensions(self, mock_mss, mock_dpi):
        from docugen.desktop.monitor_manager import MonitorManager

        mock_sct = mock_mss.return_value.__enter__.return_value
        mock_sct.monitors = self.mock_monitors

        manager = MonitorManager()
        primary = manager.primary
        # Physical: 1920x1080, DPI scale 2.0 → Logical: 960x540
        self.assertEqual(primary.logical_width, 960)
        self.assertEqual(primary.logical_height, 540)

    @patch("docugen.desktop.monitor_manager.get_dpi_scale", return_value=1.0)
    @patch("mss.mss")
    def test_get_by_index(self, mock_mss, mock_dpi):
        from docugen.desktop.monitor_manager import MonitorManager

        mock_sct = mock_mss.return_value.__enter__.return_value
        mock_sct.monitors = self.mock_monitors

        manager = MonitorManager()
        mon2 = manager.get_by_index(2)
        self.assertIsNotNone(mon2)
        self.assertEqual(mon2.width, 1280)

        # Out of range
        self.assertIsNone(manager.get_by_index(99))

    @patch("docugen.desktop.monitor_manager.get_dpi_scale", return_value=1.0)
    @patch("mss.mss")
    def test_to_mss_region(self, mock_mss, mock_dpi):
        from docugen.desktop.monitor_manager import MonitorManager

        mock_sct = mock_mss.return_value.__enter__.return_value
        mock_sct.monitors = self.mock_monitors

        manager = MonitorManager()
        region = manager.primary.to_mss_region()
        self.assertEqual(region, {"left": 0, "top": 0, "width": 1920, "height": 1080})

    @patch("docugen.desktop.monitor_manager.get_dpi_scale", return_value=1.0)
    @patch("mss.mss")
    def test_refresh_clears_cache(self, mock_mss, mock_dpi):
        from docugen.desktop.monitor_manager import MonitorManager

        mock_sct = mock_mss.return_value.__enter__.return_value
        mock_sct.monitors = self.mock_monitors

        manager = MonitorManager()
        _ = manager.monitors  # trigger load
        manager.refresh()
        self.assertIsNone(manager._monitors)


class TestScreenCapture(unittest.TestCase):
    """Tests for the ScreenCapture class."""

    def setUp(self):
        self.mock_monitors = [
            {"left": 0, "top": 0, "width": 3840, "height": 2160},
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1920, "top": 0, "width": 1280, "height": 720},
        ]

        # Create a fake mss image result
        Size = namedtuple("Size", ["width", "height"])
        self.mock_sct_img = MagicMock()
        self.mock_sct_img.rgb = b"\x00" * (1920 * 1080 * 3)
        self.mock_sct_img.size = Size(width=1920, height=1080)

    @patch("docugen.desktop.capture.get_dpi_scale", return_value=1.0)
    @patch("docugen.desktop.monitor_manager.get_dpi_scale", return_value=1.0)
    @patch("mss.mss")
    @patch("mss.tools.to_png", return_value=b"PNG_BYTES")
    def test_fullscreen_primary(self, mock_to_png, mock_mss, mock_dpi_mm, mock_dpi_cap):
        from docugen.desktop.capture import ScreenCapture, CaptureResult

        mock_sct = mock_mss.return_value.__enter__.return_value
        mock_sct.monitors = self.mock_monitors
        mock_sct.grab.return_value = self.mock_sct_img

        capture = ScreenCapture()
        result = capture.fullscreen()

        self.assertIsInstance(result, CaptureResult)
        self.assertEqual(result.image_bytes, b"PNG_BYTES")
        self.assertEqual(result.width, 1920)
        self.assertEqual(result.height, 1080)
        self.assertEqual(result.monitor_index, 1)

    @patch("docugen.desktop.capture.get_dpi_scale", return_value=1.0)
    @patch("docugen.desktop.monitor_manager.get_dpi_scale", return_value=1.0)
    @patch("mss.mss")
    @patch("mss.tools.to_png", return_value=b"PNG_BYTES")
    def test_fullscreen_specific_monitor(self, mock_to_png, mock_mss, mock_dpi_mm, mock_dpi_cap):
        from docugen.desktop.capture import ScreenCapture

        mock_sct = mock_mss.return_value.__enter__.return_value
        mock_sct.monitors = self.mock_monitors

        Size = namedtuple("Size", ["width", "height"])
        mock_img = MagicMock()
        mock_img.rgb = b"\x00" * 100
        mock_img.size = Size(width=1280, height=720)
        mock_sct.grab.return_value = mock_img

        capture = ScreenCapture()
        result = capture.monitor(2)

        self.assertEqual(result.width, 1280)
        self.assertEqual(result.monitor_index, 2)

    @patch("docugen.desktop.capture.get_dpi_scale", return_value=1.0)
    @patch("docugen.desktop.monitor_manager.get_dpi_scale", return_value=1.0)
    @patch("mss.mss")
    def test_fullscreen_invalid_monitor(self, mock_mss, mock_dpi_mm, mock_dpi_cap):
        from docugen.desktop.capture import ScreenCapture

        mock_sct = mock_mss.return_value.__enter__.return_value
        mock_sct.monitors = self.mock_monitors

        capture = ScreenCapture()
        with self.assertRaises(ValueError) as ctx:
            capture.monitor(99)
        self.assertIn("99", str(ctx.exception))

    @patch("docugen.desktop.capture.get_dpi_scale", return_value=1.0)
    @patch("docugen.desktop.monitor_manager.get_dpi_scale", return_value=1.0)
    @patch("mss.mss")
    @patch("mss.tools.to_png", return_value=b"REGION_PNG")
    def test_region_capture(self, mock_to_png, mock_mss, mock_dpi_mm, mock_dpi_cap):
        from docugen.desktop.capture import ScreenCapture

        mock_sct = mock_mss.return_value.__enter__.return_value
        mock_sct.monitors = self.mock_monitors

        Size = namedtuple("Size", ["width", "height"])
        mock_img = MagicMock()
        mock_img.rgb = b"\x00" * 100
        mock_img.size = Size(width=800, height=600)
        mock_sct.grab.return_value = mock_img

        capture = ScreenCapture()
        result = capture.region(left=100, top=100, width=800, height=600)

        self.assertEqual(result.image_bytes, b"REGION_PNG")
        expected_region = {"left": 100, "top": 100, "width": 800, "height": 600}
        mock_sct.grab.assert_called_with(expected_region)

    @patch("docugen.desktop.capture.get_dpi_scale", return_value=1.0)
    @patch("docugen.desktop.monitor_manager.get_dpi_scale", return_value=1.0)
    @patch("mss.mss")
    def test_region_invalid_size(self, mock_mss, mock_dpi_mm, mock_dpi_cap):
        from docugen.desktop.capture import ScreenCapture

        mock_sct = mock_mss.return_value.__enter__.return_value
        mock_sct.monitors = self.mock_monitors

        capture = ScreenCapture()
        with self.assertRaises(ValueError):
            capture.region(left=0, top=0, width=0, height=100)
        with self.assertRaises(ValueError):
            capture.region(left=0, top=0, width=100, height=-1)

    @patch("docugen.desktop.capture.get_dpi_scale", return_value=2.0)
    @patch("docugen.desktop.monitor_manager.get_dpi_scale", return_value=2.0)
    @patch("mss.mss")
    @patch("mss.tools.to_png", return_value=b"RETINA_PNG")
    def test_dpi_scale_in_result(self, mock_to_png, mock_mss, mock_dpi_mm, mock_dpi_cap):
        from docugen.desktop.capture import ScreenCapture

        mock_sct = mock_mss.return_value.__enter__.return_value
        mock_sct.monitors = self.mock_monitors

        Size = namedtuple("Size", ["width", "height"])
        mock_img = MagicMock()
        mock_img.rgb = b"\x00" * 100
        mock_img.size = Size(width=3840, height=2160)
        mock_sct.grab.return_value = mock_img

        capture = ScreenCapture()
        result = capture.fullscreen()

        self.assertEqual(result.dpi_scale, 2.0)
        self.assertEqual(result.logical_width, 1920)
        self.assertEqual(result.logical_height, 1080)


class TestCaptureResult(unittest.TestCase):
    """Tests for CaptureResult dataclass."""

    def test_save_creates_file(self):
        from docugen.desktop.capture import CaptureResult
        import tempfile
        import os

        result = CaptureResult(
            image_bytes=b"FAKE_PNG_DATA",
            width=100,
            height=100,
            dpi_scale=1.0,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "subdir", "test.png")
            saved = result.save(path)
            self.assertTrue(saved.exists())
            self.assertEqual(saved.read_bytes(), b"FAKE_PNG_DATA")

    def test_logical_dimensions(self):
        from docugen.desktop.capture import CaptureResult

        result = CaptureResult(
            image_bytes=b"",
            width=2880,
            height=1800,
            dpi_scale=2.0,
        )
        self.assertEqual(result.logical_width, 1440)
        self.assertEqual(result.logical_height, 900)


class TestWindowEnumerator(unittest.TestCase):
    """Tests for WindowEnumerator."""

    @patch("docugen.desktop.window_enumerator.get_os", return_value="macos")
    @patch("docugen.desktop.window_enumerator._list_windows_macos")
    def test_list_windows_delegates_to_platform(self, mock_list, mock_os):
        from docugen.desktop.window_enumerator import WindowEnumerator

        mock_list.return_value = [
            {"id": 1, "title": "Finder", "pid": 100, "bbox": {"left": 0, "top": 0, "width": 800, "height": 600}},
            {"id": 2, "title": "Terminal", "pid": 200, "bbox": {"left": 100, "top": 100, "width": 600, "height": 400}},
        ]

        enumerator = WindowEnumerator()
        windows = enumerator.list_windows()

        self.assertEqual(len(windows), 2)
        self.assertEqual(windows[0]["title"], "Finder")

    @patch("docugen.desktop.window_enumerator.get_os", return_value="macos")
    @patch("docugen.desktop.window_enumerator._list_windows_macos")
    def test_find_by_title_substring(self, mock_list, mock_os):
        from docugen.desktop.window_enumerator import WindowEnumerator

        mock_list.return_value = [
            {"id": 1, "title": "Visual Studio Code", "pid": 100, "bbox": {"left": 0, "top": 0, "width": 800, "height": 600}},
        ]

        enumerator = WindowEnumerator()
        result = enumerator.find_by_title("studio code")
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], 1)

    @patch("docugen.desktop.window_enumerator.get_os", return_value="macos")
    @patch("docugen.desktop.window_enumerator._list_windows_macos")
    def test_find_by_title_not_found(self, mock_list, mock_os):
        from docugen.desktop.window_enumerator import WindowEnumerator

        mock_list.return_value = []

        enumerator = WindowEnumerator()
        result = enumerator.find_by_title("nonexistent")
        self.assertIsNone(result)

    @patch("docugen.desktop.window_enumerator.get_os", return_value="macos")
    @patch("docugen.desktop.window_enumerator._list_windows_macos")
    def test_find_by_pid(self, mock_list, mock_os):
        from docugen.desktop.window_enumerator import WindowEnumerator

        mock_list.return_value = [
            {"id": 1, "title": "Win1", "pid": 100, "bbox": {"left": 0, "top": 0, "width": 100, "height": 100}},
            {"id": 2, "title": "Win2", "pid": 100, "bbox": {"left": 0, "top": 0, "width": 100, "height": 100}},
            {"id": 3, "title": "Other", "pid": 200, "bbox": {"left": 0, "top": 0, "width": 100, "height": 100}},
        ]

        enumerator = WindowEnumerator()
        results = enumerator.find_by_pid(100)
        self.assertEqual(len(results), 2)

    @patch("docugen.desktop.window_enumerator.get_os", return_value="linux")
    def test_graceful_import_error(self, mock_os):
        from docugen.desktop.window_enumerator import WindowEnumerator

        # _list_windows_linux will try to import Xlib which is mocked
        # but if we simulate an ImportError, it should return []
        with patch(
            "docugen.desktop.window_enumerator._list_windows_linux",
            side_effect=ImportError("no xlib"),
        ):
            enumerator = WindowEnumerator()
            windows = enumerator.list_windows()
            self.assertEqual(windows, [])


if __name__ == "__main__":
    unittest.main()
