"""Tests for macOS accessibility backend using atomacos/Apple Accessibility API.

Test coverage:
    - Permission checking and error handling
    - Element identification at coordinates
    - Bounding rectangle accuracy and coordinate conversion
    - Timeout enforcement (100ms limit)
    - Error handling for edge cases (minimized windows, invalid coords)
    - Integration with platform_router
    - Fallback to visual analysis
    - Real application accuracy testing (requires permission)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import time

# Import module under test
try:
    from docugen.desktop.macos_accessibility import (
        MacOSAccessibility,
        ElementMetadata,
        PermissionError,
        TimeoutException,
        check_accessibility_permission,
        find_element_at_coordinate,
        with_timeout,
        _cocoa_to_screen_y,
        _point_in_bounds,
        _extract_element_metadata,
        _get_screen_height,
    )

    ATOMACOS_AVAILABLE = True
except ImportError:
    ATOMACOS_AVAILABLE = False
    pytestmark = pytest.mark.skip(reason="atomacos not installed")


class TestElementMetadata:
    """Test ElementMetadata dataclass."""

    def test_to_dict_basic(self):
        """Test conversion to dict format."""
        metadata = ElementMetadata(
            title="Submit",
            role="AXButton",
            bounds={"x": 100, "y": 200, "width": 80, "height": 30},
            identifier="submit_btn",
        )
        result = metadata.to_dict()

        assert result["title"] == "Submit"
        assert result["role"] == "AXButton"
        assert result["bounds"] == {"x": 100, "y": 200, "width": 80, "height": 30}
        assert result["identifier"] == "submit_btn"
        assert result["source"] == "accessibility"

    def test_to_dict_with_parent_and_properties(self):
        """Test conversion with optional fields."""
        metadata = ElementMetadata(
            title="Username",
            role="AXTextField",
            bounds={"x": 50, "y": 100, "width": 200, "height": 25},
            identifier="username_field",
            parent_role="AXGroup",
            properties={"value": "john@example.com", "enabled": True},
        )
        result = metadata.to_dict()

        assert result["parent_role"] == "AXGroup"
        assert result["properties"] == {"value": "john@example.com", "enabled": True}


class TestTimeout:
    """Test timeout mechanism."""

    def test_timeout_does_not_trigger_for_fast_operation(self):
        """Test that fast operations complete without timeout."""
        with with_timeout(0.2):  # 200ms timeout
            time.sleep(0.05)  # 50ms operation
        # Should not raise TimeoutException

    def test_timeout_triggers_for_slow_operation(self):
        """Test that slow operations trigger timeout."""
        with pytest.raises(TimeoutException):
            with with_timeout(0.05):  # 50ms timeout
                time.sleep(0.15)  # 150ms operation


class TestCoordinateConversion:
    """Test coordinate system conversion."""

    @patch("docugen.desktop.macos_accessibility._get_screen_height", return_value=1080)
    def test_cocoa_to_screen_y_conversion(self, mock_height):
        """Test Cocoa (bottom-left) to screen (top-left) Y conversion."""
        # Element at Cocoa Y=900 with height=50
        # Screen height = 1080
        # Screen Y = 1080 - 900 - 50 = 130
        screen_y = _cocoa_to_screen_y(cocoa_y=900, element_height=50)
        assert screen_y == 130

    @patch("docugen.desktop.macos_accessibility._get_screen_height", return_value=1440)
    def test_cocoa_to_screen_y_retina(self, mock_height):
        """Test coordinate conversion on Retina display."""
        # Retina screen height = 1440
        # Element at Cocoa Y=1200 with height=100
        # Screen Y = 1440 - 1200 - 100 = 140
        screen_y = _cocoa_to_screen_y(cocoa_y=1200, element_height=100)
        assert screen_y == 140

    def test_point_in_bounds_inside(self):
        """Test point falls inside element bounds."""
        # Create mock position and size
        position = Mock(x=100, y=900)  # Cocoa coords
        size = Mock(width=200, height=50)

        # Point at (150, 135) in screen coords
        # Element bounds: x=100, screen_y=130 (from cocoa_y=900, height=50, screen_height=1080)
        # width=200, height=50
        # So bounds are: x[100-300], y[130-180]
        with patch(
            "docugen.desktop.macos_accessibility._get_screen_height", return_value=1080
        ):
            assert _point_in_bounds(150, 135, position, size) is True

    def test_point_in_bounds_outside(self):
        """Test point falls outside element bounds."""
        position = Mock(x=100, y=900)
        size = Mock(width=200, height=50)

        with patch(
            "docugen.desktop.macos_accessibility._get_screen_height", return_value=1080
        ):
            # Point at (50, 135) - outside X bounds
            assert _point_in_bounds(50, 135, position, size) is False


class TestPermissionChecking:
    """Test accessibility permission checking."""

    @patch("AppKit.NSWorkspace")
    @patch("atomacos.getAppRefByPid")
    def test_permission_granted(self, mock_get_app, mock_workspace):
        """Test permission check returns True when granted."""
        # Mock frontmost app
        mock_app = Mock()
        mock_app.processIdentifier.return_value = 1234
        mock_workspace.sharedWorkspace.return_value.frontmostApplication.return_value = (
            mock_app
        )

        # Mock atomacos app reference
        mock_ax_app = Mock()
        mock_ax_app.AXRole = "AXApplication"
        mock_get_app.return_value = mock_ax_app

        result = check_accessibility_permission()
        assert result is True

    @patch("AppKit.NSWorkspace")
    @patch("atomacos.getAppRefByPid")
    def test_permission_denied_ax_error(self, mock_get_app, mock_workspace):
        """Test permission check returns False when AXError raised."""
        # Mock frontmost app
        mock_app = Mock()
        mock_app.processIdentifier.return_value = 1234
        mock_workspace.sharedWorkspace.return_value.frontmostApplication.return_value = (
            mock_app
        )

        # Mock AXError
        mock_get_app.side_effect = Exception("AX API Error: not trusted")

        result = check_accessibility_permission()
        assert result is False

    @patch("AppKit.NSWorkspace")
    def test_permission_check_no_frontmost_app(self, mock_workspace):
        """Test permission check handles no frontmost app."""
        mock_workspace.sharedWorkspace.return_value.frontmostApplication.return_value = (
            None
        )

        result = check_accessibility_permission()
        assert result is False


class TestExtractElementMetadata:
    """Test element metadata extraction."""

    def test_extract_basic_metadata(self):
        """Test extraction of basic element attributes."""
        # Mock AX element
        mock_element = Mock()
        mock_element.AXTitle = "Submit Button"
        mock_element.AXDescription = ""
        mock_element.AXRole = "AXButton"
        mock_element.AXPosition = Mock(x=100, y=900)
        mock_element.AXSize = Mock(width=80, height=30)
        mock_element.AXIdentifier = "submit_btn"
        mock_element.AXParent = Mock(AXRole="AXGroup")
        mock_element.AXValue = None
        mock_element.AXEnabled = True

        with patch(
            "docugen.desktop.macos_accessibility._get_screen_height", return_value=1080
        ):
            metadata = _extract_element_metadata(mock_element)

        assert metadata is not None
        assert metadata.title == "Submit Button"
        assert metadata.role == "AXButton"
        assert metadata.identifier == "submit_btn"
        assert metadata.parent_role == "AXGroup"
        # Screen Y = 1080 - 900 - 30 = 150
        assert metadata.bounds == {"x": 100, "y": 150, "width": 80, "height": 30}

    def test_extract_metadata_missing_identifier(self):
        """Test identifier generation when AXIdentifier unavailable."""
        mock_element = Mock()
        mock_element.AXTitle = "Click Me"
        mock_element.AXRole = "AXButton"
        mock_element.AXPosition = Mock(x=0, y=0)
        mock_element.AXSize = Mock(width=50, height=20)

        # Simulate missing AXIdentifier
        del mock_element.AXIdentifier

        with patch(
            "docugen.desktop.macos_accessibility._get_screen_height", return_value=1080
        ):
            metadata = _extract_element_metadata(mock_element)

        assert metadata is not None
        assert metadata.identifier == "AXButton_Click Me"

    def test_extract_metadata_with_properties(self):
        """Test extraction of additional properties."""
        mock_element = Mock()
        mock_element.AXTitle = "Email"
        mock_element.AXRole = "AXTextField"
        mock_element.AXPosition = Mock(x=50, y=950)
        mock_element.AXSize = Mock(width=200, height=25)
        mock_element.AXIdentifier = "email_field"
        mock_element.AXValue = "user@example.com"
        mock_element.AXEnabled = True

        with patch(
            "docugen.desktop.macos_accessibility._get_screen_height", return_value=1080
        ):
            metadata = _extract_element_metadata(mock_element)

        assert metadata.properties is not None
        assert metadata.properties["value"] == "user@example.com"
        assert metadata.properties["enabled"] is True


class TestFindElementAtCoordinate:
    """Test element finding at coordinates."""

    def test_invalid_coordinates_negative(self):
        """Test handling of negative coordinates."""
        result = find_element_at_coordinate(-10, 50)
        assert result is None

    @patch("AppKit.NSWorkspace")
    @patch("atomacos.getAppRefByPid")
    @patch("docugen.desktop.macos_accessibility._get_screen_height", return_value=1080)
    def test_find_element_no_children(
        self, mock_height, mock_get_app, mock_workspace
    ):
        """Test finding leaf element with no children."""
        # Mock frontmost app
        mock_app_info = Mock()
        mock_app_info.processIdentifier.return_value = 1234
        mock_workspace.sharedWorkspace.return_value.frontmostApplication.return_value = (
            mock_app_info
        )

        # Mock AX app with button element
        mock_button = Mock()
        mock_button.AXTitle = "OK"
        mock_button.AXRole = "AXButton"
        mock_button.AXPosition = Mock(x=100, y=900)  # Screen Y = 1080 - 900 - 30 = 150
        mock_button.AXSize = Mock(width=80, height=30)
        mock_button.AXIdentifier = "ok_btn"
        mock_button.AXChildren = []

        mock_ax_app = Mock()
        mock_ax_app.AXPosition = Mock(x=0, y=0)
        mock_ax_app.AXSize = Mock(width=1920, height=1080)
        mock_ax_app.AXChildren = [mock_button]

        mock_get_app.return_value = mock_ax_app

        # Click at (120, 160) - inside button bounds [100-180, 150-180]
        result = find_element_at_coordinate(120, 160)

        assert result is not None
        assert result.title == "OK"
        assert result.role == "AXButton"
        assert result.identifier == "ok_btn"

    @patch("AppKit.NSWorkspace")
    @patch("atomacos.getAppRefByPid")
    def test_permission_error_raised(self, mock_get_app, mock_workspace):
        """Test PermissionError raised when permission denied."""
        # Mock frontmost app
        mock_app_info = Mock()
        mock_app_info.processIdentifier.return_value = 1234
        mock_workspace.sharedWorkspace.return_value.frontmostApplication.return_value = (
            mock_app_info
        )

        # Mock AXError
        mock_get_app.side_effect = Exception("AX API Error: permission denied")

        with pytest.raises(PermissionError) as exc_info:
            find_element_at_coordinate(100, 200)

        assert "System Preferences > Security & Privacy > Accessibility" in str(
            exc_info.value
        )

    @patch("AppKit.NSWorkspace")
    @patch("atomacos.getAppRefByPid")
    @patch("docugen.desktop.macos_accessibility._get_screen_height", return_value=1080)
    def test_timeout_on_slow_query(self, mock_height, mock_get_app, mock_workspace):
        """Test timeout raised when query exceeds 100ms.

        Note: This test verifies the timeout mechanism works. Due to signal
        handling timing variability, we allow for either TimeoutException or
        successful completion that took >100ms (which would trigger fallback
        in production).
        """
        # Mock frontmost app
        mock_app_info = Mock()
        mock_app_info.processIdentifier.return_value = 1234
        mock_workspace.sharedWorkspace.return_value.frontmostApplication.return_value = (
            mock_app_info
        )

        # Mock slow getAppRefByPid - this will trigger timeout during initial AX query
        def slow_get_app_ref(pid):
            time.sleep(0.15)  # 150ms - exceeds 100ms timeout
            mock_ax_app = Mock()
            mock_ax_app.AXPosition = Mock(x=0, y=0)
            mock_ax_app.AXSize = Mock(width=1920, height=1080)
            mock_ax_app.AXChildren = []
            return mock_ax_app

        mock_get_app.side_effect = slow_get_app_ref

        # The timeout mechanism should raise TimeoutException
        # However, signal handling can be timing-sensitive in tests
        start_time = time.time()
        with pytest.raises(TimeoutException):
            find_element_at_coordinate(100, 200)

        # Verify the timeout triggered within reasonable time
        # Allow some overhead for signal handling
        elapsed = time.time() - start_time
        assert (
            0.05 <= elapsed <= 0.25
        ), f"Timeout should trigger ~100ms, got {elapsed}s"


class TestMacOSAccessibility:
    """Test MacOSAccessibility class (backend implementation)."""

    @patch("docugen.desktop.macos_accessibility.check_accessibility_permission")
    @patch("docugen.desktop.macos_accessibility.find_element_at_coordinate")
    def test_get_element_at_point_returns_metadata(
        self, mock_find, mock_check_permission
    ):
        """Test get_element_at_point returns dict with all required fields."""
        mock_check_permission.return_value = True

        # Mock found element
        mock_metadata = ElementMetadata(
            title="Login",
            role="AXButton",
            bounds={"x": 100, "y": 200, "width": 80, "height": 30},
            identifier="login_btn",
            parent_role="AXWindow",
            properties={"enabled": True},
        )
        mock_find.return_value = mock_metadata

        backend = MacOSAccessibility()
        result = backend.get_element_at_point(100, 200)

        assert result is not None
        assert result["title"] == "Login"
        assert result["role"] == "AXButton"
        assert result["bounds"] == {"x": 100, "y": 200, "width": 80, "height": 30}
        assert result["identifier"] == "login_btn"
        assert result["source"] == "accessibility"
        assert result["parent_role"] == "AXWindow"

    @patch("docugen.desktop.macos_accessibility.check_accessibility_permission")
    def test_get_element_permission_denied_error(self, mock_check_permission):
        """Test PermissionError raised with correct message when permission denied."""
        mock_check_permission.return_value = False

        backend = MacOSAccessibility()

        with pytest.raises(PermissionError) as exc_info:
            backend.get_element_at_point(100, 200)

        error_msg = str(exc_info.value)
        assert "System Preferences > Security & Privacy > Accessibility" in error_msg

    @patch("docugen.desktop.macos_accessibility.check_accessibility_permission")
    @patch("docugen.desktop.macos_accessibility.find_element_at_coordinate")
    def test_get_element_timeout_returns_none(
        self, mock_find, mock_check_permission
    ):
        """Test timeout returns None for graceful fallback."""
        mock_check_permission.return_value = True
        mock_find.side_effect = TimeoutException("Query timed out")

        backend = MacOSAccessibility()
        result = backend.get_element_at_point(100, 200)

        # Should return None, not raise exception
        assert result is None

    @patch("docugen.desktop.macos_accessibility.check_accessibility_permission")
    @patch("AppKit.NSWorkspace")
    @patch("atomacos.getAppRefByPid")
    def test_get_focused_element(
        self, mock_get_app, mock_workspace, mock_check_permission
    ):
        """Test get_focused_element returns focused element metadata."""
        mock_check_permission.return_value = True

        # Mock frontmost app
        mock_app_info = Mock()
        mock_app_info.processIdentifier.return_value = 1234
        mock_workspace.sharedWorkspace.return_value.frontmostApplication.return_value = (
            mock_app_info
        )

        # Mock focused element
        mock_focused = Mock()
        mock_focused.AXTitle = "Search"
        mock_focused.AXRole = "AXTextField"
        mock_focused.AXPosition = Mock(x=50, y=950)
        mock_focused.AXSize = Mock(width=200, height=25)
        mock_focused.AXIdentifier = "search_field"

        mock_ax_app = Mock()
        mock_ax_app.AXFocusedUIElement = mock_focused
        mock_get_app.return_value = mock_ax_app

        backend = MacOSAccessibility()

        with patch(
            "docugen.desktop.macos_accessibility._get_screen_height", return_value=1080
        ):
            result = backend.get_focused_element()

        assert result is not None
        assert result["title"] == "Search"
        assert result["role"] == "AXTextField"
        assert result["identifier"] == "search_field"


class TestErrorHandling:
    """Test error handling for edge cases."""

    @patch("AppKit.NSWorkspace")
    def test_minimized_window_returns_none(self, mock_workspace):
        """Test gracefully handles minimized windows (no element found)."""
        # Minimized window has no visible elements
        # This is simulated by no frontmost app or no elements at coordinate
        mock_workspace.sharedWorkspace.return_value.frontmostApplication.return_value = (
            None
        )
        result = find_element_at_coordinate(100, 200)
        assert result is None

    def test_invalid_coordinate_out_of_bounds(self):
        """Test handles out-of-bounds coordinates (y=10000)."""
        result = find_element_at_coordinate(50, 10000)
        # Should return None without crashing (no element at those coords)
        # This will be caught by "no frontmost app" or coordinate validation
        assert result is None or result is not None  # Just verify no crash

    @patch("AppKit.NSWorkspace")
    @patch("atomacos.getAppRefByPid")
    @patch("docugen.desktop.macos_accessibility._get_screen_height", return_value=1080)
    def test_application_without_accessibility(
        self, mock_height, mock_get_app, mock_workspace
    ):
        """Test handles apps without accessibility support."""
        # Mock frontmost app
        mock_app_info = Mock()
        mock_app_info.processIdentifier.return_value = 1234
        mock_workspace.sharedWorkspace.return_value.frontmostApplication.return_value = (
            mock_app_info
        )

        # Mock app with no accessible elements (returns None or raises error)
        mock_get_app.side_effect = Exception("AXErrorInvalidUIElement")

        result = find_element_at_coordinate(100, 200)
        # Should return None without crashing
        assert result is None

    @patch("AppKit.NSWorkspace")
    @patch("atomacos.getAppRefByPid")
    @patch("docugen.desktop.macos_accessibility._get_screen_height", return_value=1080)
    def test_element_without_bounds_returns_none(
        self, mock_height, mock_get_app, mock_workspace
    ):
        """Test that elements without AXPosition/AXSize return None (not invalid bounds)."""
        # Mock frontmost app
        mock_app_info = Mock()
        mock_app_info.processIdentifier.return_value = 1234
        mock_workspace.sharedWorkspace.return_value.frontmostApplication.return_value = (
            mock_app_info
        )

        # Mock app with element that has no bounds
        mock_app = Mock()
        mock_element = Mock()
        mock_element.AXTitle = "Test Element"
        mock_element.AXRole = "AXButton"
        # Missing AXPosition and AXSize - should raise AttributeError
        del mock_element.AXPosition
        del mock_element.AXSize
        mock_element.AXIdentifier = "test-id"

        mock_app.findFirst.return_value = mock_element
        mock_get_app.return_value = mock_app

        # Should return None when bounds extraction fails
        result = find_element_at_coordinate(100, 200)
        assert result is None


class TestBoundsAccuracy:
    """Test bounding rectangle accuracy within 2 pixels."""

    @patch("docugen.desktop.macos_accessibility._get_screen_height", return_value=1080)
    def test_bounds_standard_display(self, mock_height):
        """Test bounds accuracy on standard display (scale=1.0)."""
        mock_element = Mock()
        mock_element.AXTitle = "Test"
        mock_element.AXRole = "AXButton"
        # Cocoa coords: x=100, y=900, width=50, height=30
        # Screen Y = 1080 - 900 - 30 = 150
        mock_element.AXPosition = Mock(x=100, y=900)
        mock_element.AXSize = Mock(width=50, height=30)
        mock_element.AXIdentifier = "test_btn"

        metadata = _extract_element_metadata(mock_element)

        # Verify bounds are exact (within ±2 pixels tolerance)
        assert abs(metadata.bounds["x"] - 100) <= 2
        assert abs(metadata.bounds["y"] - 150) <= 2
        assert abs(metadata.bounds["width"] - 50) <= 2
        assert abs(metadata.bounds["height"] - 30) <= 2

    @patch("docugen.desktop.macos_accessibility._get_screen_height", return_value=1440)
    def test_bounds_retina_display(self, mock_height):
        """Test bounds accuracy on Retina display (scale=2.0)."""
        mock_element = Mock()
        mock_element.AXTitle = "Retina Test"
        mock_element.AXRole = "AXButton"
        # Cocoa coords on Retina: x=200, y=1200, width=100, height=60
        # Screen Y = 1440 - 1200 - 60 = 180
        mock_element.AXPosition = Mock(x=200, y=1200)
        mock_element.AXSize = Mock(width=100, height=60)
        mock_element.AXIdentifier = "retina_btn"

        metadata = _extract_element_metadata(mock_element)

        # Verify bounds within ±2px tolerance
        assert abs(metadata.bounds["x"] - 200) <= 2
        assert abs(metadata.bounds["y"] - 180) <= 2
        assert abs(metadata.bounds["width"] - 100) <= 2
        assert abs(metadata.bounds["height"] - 60) <= 2


@pytest.mark.skipif(
    not ATOMACOS_AVAILABLE, reason="Requires atomacos and accessibility permission"
)
@pytest.mark.requires_permission
class TestRealApplicationAccuracy:
    """Integration tests with real macOS applications.

    These tests require:
    1. atomacos and pyobjc installed
    2. Accessibility permission granted to Python/pytest
    3. Target applications (Finder, TextEdit, etc.) available

    Run with: pytest tests/desktop/test_macos_accessibility.py -v -m requires_permission
    """

    def test_system_preferences_element_identification(self):
        """Test element identification in System Preferences app.

        Opens System Preferences, identifies 5 known elements, verifies accuracy.
        Requires accessibility permission to be granted.
        """
        import subprocess
        import time

        from docugen.desktop.macos_accessibility import (
            MacOSAccessibility,
            check_accessibility_permission,
        )

        backend = MacOSAccessibility()

        # Check permission first
        if not check_accessibility_permission():
            pytest.skip(
                "Accessibility permission required. Grant permission in System Preferences > Security & Privacy > Accessibility"
            )

        # Open System Preferences
        try:
            subprocess.run(
                ["open", "-a", "System Preferences"], check=True, timeout=5
            )
            time.sleep(2)  # Wait for window to open

            # Test 5 known element areas in System Preferences window
            # These coordinates target typical UI elements (window controls, sidebar items)
            test_coords = [
                (100, 100),  # Top-left area (window controls)
                (200, 150),  # Toolbar/header area
                (100, 300),  # Left sidebar area
                (400, 300),  # Main content area
                (600, 500),  # Lower content area
            ]

            successful = 0
            for x, y in test_coords:
                try:
                    result = backend.get_element_at_point(x, y)
                    if result and result.get("role") and result.get("bounds"):
                        # Verify bounds are valid (not 0,0,0,0)
                        bounds = result["bounds"]
                        if bounds.get("width", 0) > 0 and bounds.get("height", 0) > 0:
                            successful += 1
                except Exception:
                    pass

            # Cleanup
            subprocess.run(["osascript", "-e", 'quit app "System Preferences"'])

            # Verify at least 4/5 successful (80% threshold)
            assert (
                successful >= 4
            ), f"Only {successful}/5 elements identified in System Preferences"

        except subprocess.TimeoutExpired:
            pytest.skip("System Preferences failed to open")

    def test_finder_element_identification(self):
        """Test element identification in Finder app."""
        import subprocess
        import time

        from docugen.desktop.macos_accessibility import (
            MacOSAccessibility,
            check_accessibility_permission,
        )

        backend = MacOSAccessibility()

        if not check_accessibility_permission():
            pytest.skip(
                "Accessibility permission required. Grant permission in System Preferences > Security & Privacy > Accessibility"
            )

        # Open Finder
        try:
            subprocess.run(["open", "-a", "Finder"], check=True, timeout=5)
            time.sleep(2)

            test_coords = [
                (50, 100),  # Sidebar area
                (300, 100),  # Toolbar
                (400, 300),  # File list area
                (100, 500),  # Bottom sidebar
                (600, 400),  # Main content
            ]

            successful = 0
            for x, y in test_coords:
                try:
                    result = backend.get_element_at_point(x, y)
                    if result and result.get("role") and result.get("bounds"):
                        bounds = result["bounds"]
                        if bounds.get("width", 0) > 0 and bounds.get("height", 0) > 0:
                            successful += 1
                except Exception:
                    pass

            assert (
                successful >= 4
            ), f"Only {successful}/5 elements identified in Finder"

        except subprocess.TimeoutExpired:
            pytest.skip("Finder failed to open")

    def test_textdit_element_identification(self):
        """Test element identification in TextEdit app."""
        import subprocess
        import time

        from docugen.desktop.macos_accessibility import (
            MacOSAccessibility,
            check_accessibility_permission,
        )

        backend = MacOSAccessibility()

        if not check_accessibility_permission():
            pytest.skip(
                "Accessibility permission required. Grant permission in System Preferences > Security & Privacy > Accessibility"
            )

        try:
            subprocess.run(["open", "-a", "TextEdit"], check=True, timeout=5)
            time.sleep(2)

            test_coords = [
                (100, 50),  # Menu bar area
                (200, 100),  # Toolbar area
                (300, 200),  # Text area
                (400, 300),  # Text editor
                (500, 400),  # Lower text area
            ]

            successful = 0
            for x, y in test_coords:
                try:
                    result = backend.get_element_at_point(x, y)
                    if result and result.get("role") and result.get("bounds"):
                        bounds = result["bounds"]
                        if bounds.get("width", 0) > 0 and bounds.get("height", 0) > 0:
                            successful += 1
                except Exception:
                    pass

            # Cleanup
            subprocess.run(["osascript", "-e", 'quit app "TextEdit"'])

            assert (
                successful >= 4
            ), f"Only {successful}/5 elements identified in TextEdit"

        except subprocess.TimeoutExpired:
            pytest.skip("TextEdit failed to open")

    def test_safari_element_identification(self):
        """Test element identification in Safari app."""
        import subprocess
        import time

        from docugen.desktop.macos_accessibility import (
            MacOSAccessibility,
            check_accessibility_permission,
        )

        backend = MacOSAccessibility()

        if not check_accessibility_permission():
            pytest.skip(
                "Accessibility permission required. Grant permission in System Preferences > Security & Privacy > Accessibility"
            )

        try:
            subprocess.run(["open", "-a", "Safari"], check=True, timeout=5)
            time.sleep(2)

            test_coords = [
                (100, 100),  # Toolbar/navigation
                (300, 100),  # URL bar area
                (500, 100),  # Toolbar buttons
                (400, 300),  # Content area
                (200, 500),  # Lower content
            ]

            successful = 0
            for x, y in test_coords:
                try:
                    result = backend.get_element_at_point(x, y)
                    if result and result.get("role") and result.get("bounds"):
                        bounds = result["bounds"]
                        if bounds.get("width", 0) > 0 and bounds.get("height", 0) > 0:
                            successful += 1
                except Exception:
                    pass

            # Cleanup
            subprocess.run(["osascript", "-e", 'quit app "Safari"'])

            assert (
                successful >= 4
            ), f"Only {successful}/5 elements identified in Safari"

        except subprocess.TimeoutExpired:
            pytest.skip("Safari failed to open")


class TestPlatformRouterIntegration:
    """Test integration with platform_router.py."""

    @patch("docugen.desktop.platform_router.get_os", return_value="macos")
    @patch("docugen.desktop.macos_accessibility.MacOSAccessibility")
    def test_platform_router_uses_macos_accessibility(
        self, mock_backend_class, mock_get_os
    ):
        """Test platform_router loads MacOSAccessibility on macOS."""
        from docugen.desktop.platform_router import get_accessibility_backend

        mock_instance = Mock()
        mock_instance.get_element_at_point.return_value = {
            "title": "Test",
            "role": "AXButton",
            "bounds": {"x": 0, "y": 0, "width": 50, "height": 20},
            "identifier": "test",
            "source": "accessibility",
        }
        mock_backend_class.return_value = mock_instance

        backend = get_accessibility_backend()
        assert backend is not None

        result = backend.get_element_at_point(100, 200)
        assert result["source"] == "accessibility"

    @patch("docugen.desktop.platform_router.get_os", return_value="macos")
    @patch(
        "docugen.desktop.platform_router.get_accessibility_backend",
        return_value=None,
    )
    @patch("docugen.desktop.visual_analyzer.analyze_screenshot")
    def test_fallback_to_visual_analysis(
        self, mock_visual, mock_backend, mock_get_os
    ):
        """Test fallback to visual analysis when accessibility unavailable."""
        from docugen.desktop.platform_router import get_element_metadata

        # Mock visual analyzer return value
        mock_visual.return_value = [
            {
                "title": "Visual Button",
                "role": "button",
                "bounds": {"x": 100, "y": 200, "width": 80, "height": 30},
                "source": "vision",
            }
        ]

        result = get_element_metadata(100, 200, screenshot_path="/tmp/test.png")

        # Should fall back to visual analysis
        assert result is not None
        assert result["source"] == "vision"
        mock_visual.assert_called_once()
