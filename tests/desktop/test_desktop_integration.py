"""Tests for desktop integration with annotation and markdown scripts."""

import unittest
from unittest.mock import patch, MagicMock

# Import annotation functions
from docugen.scripts.annotate_screenshot import (
    normalize_desktop_element,
    draw_desktop_element,
)

# Import markdown generation
from docugen.scripts.generate_markdown import generate_step_section


class TestNormalizeDesktopElement(unittest.TestCase):
    """Tests for normalize_desktop_element."""

    def test_converts_bounds_to_boundingBox(self):
        elem = {
            "name": "Save",
            "type": "button",
            "bounds": {"x": 10, "y": 20, "width": 80, "height": 30},
            "source": "accessibility",
        }
        result = normalize_desktop_element(elem)
        self.assertEqual(result["boundingBox"], {"x": 10, "y": 20, "width": 80, "height": 30})

    def test_preserves_existing_boundingBox(self):
        elem = {
            "boundingBox": {"x": 5, "y": 5, "width": 50, "height": 25},
            "bounds": {"x": 10, "y": 20, "width": 80, "height": 30},
        }
        result = normalize_desktop_element(elem)
        # Should keep the existing boundingBox, not overwrite
        self.assertEqual(result["boundingBox"], {"x": 5, "y": 5, "width": 50, "height": 25})

    def test_maps_name_to_text(self):
        elem = {"name": "OK Button", "bounds": {"x": 0, "y": 0, "width": 50, "height": 25}}
        result = normalize_desktop_element(elem)
        self.assertEqual(result["text"], "OK Button")

    def test_maps_type_to_tagName(self):
        for desktop_type, expected_tag in [
            ("button", "button"),
            ("input", "input"),
            ("link", "a"),
            ("dropdown", "select"),
        ]:
            elem = {"type": desktop_type, "bounds": {"x": 0, "y": 0, "width": 50, "height": 25}}
            result = normalize_desktop_element(elem)
            self.assertEqual(result["tagName"], expected_tag, f"Failed for type={desktop_type}")

    def test_sets_isTarget(self):
        elem = {"bounds": {"x": 0, "y": 0, "width": 50, "height": 25}}
        result = normalize_desktop_element(elem)
        self.assertTrue(result["isTarget"])


class TestDrawDesktopElement(unittest.TestCase):
    """Tests for draw_desktop_element."""

    @patch("docugen.scripts.annotate_screenshot.smart_annotate")
    def test_calls_smart_annotate_with_normalized_element(self, mock_smart):
        from PIL import Image, ImageDraw
        from docugen.scripts.annotate_screenshot import DEFAULT_STYLES

        img = Image.new("RGBA", (200, 200))
        draw = ImageDraw.Draw(img)
        mock_smart.return_value = img

        elem = {
            "name": "Submit",
            "type": "button",
            "bounds": {"x": 10, "y": 20, "width": 80, "height": 30},
            "source": "accessibility",
            "confidence": 0.95,
        }

        draw_desktop_element(img, draw, elem, 1, DEFAULT_STYLES.copy())

        mock_smart.assert_called_once()
        call_args = mock_smart.call_args
        elements = call_args[0][2]  # Third positional arg
        self.assertTrue(elements[0]["isTarget"])
        self.assertEqual(elements[0]["boundingBox"], elem["bounds"])

    @patch("docugen.scripts.annotate_screenshot.smart_annotate")
    def test_visual_source_uses_orange_color(self, mock_smart):
        from PIL import Image, ImageDraw
        from docugen.scripts.annotate_screenshot import DEFAULT_STYLES

        img = Image.new("RGBA", (200, 200))
        draw = ImageDraw.Draw(img)
        mock_smart.return_value = img

        elem = {
            "bounds": {"x": 10, "y": 20, "width": 80, "height": 30},
            "source": "visual",
            "confidence": 0.6,
        }

        draw_desktop_element(img, draw, elem, 1, DEFAULT_STYLES.copy())

        call_args = mock_smart.call_args
        styles_used = call_args[0][4]  # Fifth positional arg (styles)
        self.assertEqual(styles_used["highlight_color"], (255, 165, 0, 180))
        self.assertEqual(styles_used["highlight_width"], 2)  # Low confidence = thinner

    @patch("docugen.scripts.annotate_screenshot.smart_annotate")
    def test_high_confidence_visual_uses_normal_width(self, mock_smart):
        from PIL import Image, ImageDraw
        from docugen.scripts.annotate_screenshot import DEFAULT_STYLES

        img = Image.new("RGBA", (200, 200))
        draw = ImageDraw.Draw(img)
        mock_smart.return_value = img

        elem = {
            "bounds": {"x": 10, "y": 20, "width": 80, "height": 30},
            "source": "visual",
            "confidence": 0.9,
        }

        draw_desktop_element(img, draw, elem, 1, DEFAULT_STYLES.copy())

        call_args = mock_smart.call_args
        styles_used = call_args[0][4]
        self.assertEqual(styles_used["highlight_width"], 3)


class TestGenerateStepSectionDesktop(unittest.TestCase):
    """Tests for desktop mode in generate_step_section."""

    def test_web_mode_unchanged(self):
        step = {
            "number": 1,
            "title": "Click Submit",
            "description": "Submit the form",
            "screenshot": "./images/step-01.png",
            "expected_result": "Form submitted",
        }
        result = generate_step_section(step)
        self.assertIn("### Step 1: Click Submit", result)
        self.assertIn("Submit the form", result)
        self.assertNotIn("Application:", result)

    def test_desktop_mode_includes_app_name(self):
        step = {
            "number": 2,
            "title": "Open Settings",
            "description": "Navigate to system settings",
            "mode": "desktop",
            "app_name": "System Preferences",
            "screenshot": "./images/step-02.png",
        }
        result = generate_step_section(step)
        self.assertIn("**Application:** System Preferences", result)

    def test_desktop_mode_includes_window_title(self):
        step = {
            "number": 3,
            "title": "Select Network",
            "description": "Go to network panel",
            "mode": "desktop",
            "app_name": "System Preferences",
            "window_title": "Network Settings",
            "screenshot": "./images/step-03.png",
        }
        result = generate_step_section(step)
        self.assertIn("System Preferences - Network Settings", result)

    def test_desktop_element_accessibility_source(self):
        step = {
            "number": 4,
            "title": "Click Apply",
            "description": "Apply changes",
            "mode": "desktop",
            "element": {
                "name": "Apply",
                "type": "button",
                "source": "accessibility",
            },
            "screenshot": "./images/step-04.png",
        }
        result = generate_step_section(step)
        self.assertIn("Click **Apply** (button)", result)
        self.assertNotIn("visual analysis", result)

    def test_desktop_element_visual_source_with_confidence(self):
        step = {
            "number": 5,
            "title": "Click Save",
            "description": "Save the file",
            "mode": "desktop",
            "element": {
                "name": "Save",
                "type": "button",
                "source": "visual",
                "confidence": 0.85,
            },
            "screenshot": "./images/step-05.png",
        }
        result = generate_step_section(step)
        self.assertIn("Click **Save** (button", result)
        self.assertIn("visual analysis", result)
        self.assertIn("85% confidence", result)

    def test_desktop_skips_duplicate_window_title(self):
        """Don't repeat app name if window title matches."""
        step = {
            "number": 1,
            "title": "Open Finder",
            "description": "Open file manager",
            "mode": "desktop",
            "app_name": "Finder",
            "window_title": "Finder",
            "screenshot": "./images/step-01.png",
        }
        result = generate_step_section(step)
        # Should show just app name, not "Finder - Finder"
        self.assertIn("**Application:** Finder", result)
        self.assertNotIn("Finder - Finder", result)


if __name__ == "__main__":
    unittest.main()
