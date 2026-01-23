"""Tests for mode_detection module."""

import unittest

from docugen.desktop.mode_detection import detect_mode


class TestDetectMode(unittest.TestCase):
    """Tests for detect_mode function."""

    # --- URL always means web ---

    def test_url_always_web(self):
        self.assertEqual(detect_mode("Document https://github.com/new"), "web")

    def test_url_with_desktop_keywords_still_web(self):
        """URL takes priority even with desktop keywords present."""
        self.assertEqual(
            detect_mode("Document this desktop app at https://app.example.com"),
            "web",
        )

    def test_www_url_is_web(self):
        self.assertEqual(detect_mode("Go to www.example.com"), "web")

    # --- Desktop keywords ---

    def test_desktop_keyword(self):
        self.assertEqual(detect_mode("Document this desktop application"), "desktop")

    def test_system_settings(self):
        self.assertEqual(
            detect_mode("Change resolution in System Settings"), "desktop"
        )

    def test_system_preferences(self):
        self.assertEqual(
            detect_mode("Open System Preferences and go to Displays"), "desktop"
        )

    def test_finder(self):
        self.assertEqual(detect_mode("Create a folder in Finder"), "desktop")

    def test_native_app(self):
        self.assertEqual(detect_mode("Record this native app workflow"), "desktop")

    def test_vs_code(self):
        self.assertEqual(detect_mode("Document how to use VS Code extensions"), "desktop")

    def test_photoshop(self):
        self.assertEqual(detect_mode("Create a layer in Photoshop"), "desktop")

    def test_capture_desktop(self):
        self.assertEqual(detect_mode("Capture desktop workflow"), "desktop")

    def test_windows_application(self):
        self.assertEqual(
            detect_mode("Document this Windows application"), "desktop"
        )

    def test_macos_application(self):
        self.assertEqual(
            detect_mode("Document this macOS application"), "desktop"
        )

    # --- Web keywords ---

    def test_website(self):
        self.assertEqual(detect_mode("Document this website"), "web")

    def test_web_app(self):
        self.assertEqual(detect_mode("Create a walkthrough for this web app"), "web")

    def test_browser(self):
        self.assertEqual(detect_mode("Record browser workflow"), "web")

    def test_login_page(self):
        self.assertEqual(detect_mode("Document the login page"), "web")

    def test_dashboard(self):
        self.assertEqual(detect_mode("Create a guide for the dashboard"), "web")

    # --- Ambiguous ---

    def test_ambiguous_no_keywords(self):
        self.assertEqual(detect_mode("Document this workflow"), "ambiguous")

    def test_ambiguous_generic(self):
        self.assertEqual(detect_mode("Create a walkthrough"), "ambiguous")

    def test_ambiguous_no_context(self):
        self.assertEqual(detect_mode("Help me record the process"), "ambiguous")

    # --- Mixed keywords (desktop wins when equal) ---

    def test_mixed_desktop_bias(self):
        """When both present with equal score, desktop wins."""
        result = detect_mode("Document the desktop browser app")
        # "desktop" keyword + "browser" keyword → desktop wins (bias)
        self.assertEqual(result, "desktop")

    # --- Case insensitivity ---

    def test_case_insensitive(self):
        self.assertEqual(detect_mode("DOCUMENT THIS DESKTOP APPLICATION"), "desktop")
        self.assertEqual(detect_mode("WEBSITE documentation"), "web")


if __name__ == "__main__":
    unittest.main()
