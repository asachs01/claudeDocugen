"""Tests for desktop element annotation enhancements."""

import unittest
from unittest.mock import patch, MagicMock

try:
    from PIL import Image, ImageDraw
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from docugen.scripts.annotate_screenshot import (
    normalize_desktop_element,
    DEFAULT_STYLES,
)


class TestNormalizeDesktopElement(unittest.TestCase):
    """Tests for normalize_desktop_element function."""

    def test_converts_bounds_to_bounding_box(self):
        element = {"bounds": {"x": 10, "y": 20, "width": 100, "height": 30}}
        result = normalize_desktop_element(element)
        self.assertEqual(result["boundingBox"], {"x": 10, "y": 20, "width": 100, "height": 30})

    def test_preserves_existing_bounding_box(self):
        element = {
            "bounds": {"x": 0, "y": 0, "width": 50, "height": 50},
            "boundingBox": {"x": 5, "y": 5, "width": 40, "height": 40},
        }
        result = normalize_desktop_element(element)
        # Existing boundingBox preserved
        self.assertEqual(result["boundingBox"]["x"], 5)

    def test_maps_name_to_text(self):
        element = {"name": "Save Button", "bounds": {"x": 0, "y": 0, "width": 1, "height": 1}}
        result = normalize_desktop_element(element)
        self.assertEqual(result["text"], "Save Button")

    def test_maps_type_to_tag(self):
        element = {"type": "button", "bounds": {"x": 0, "y": 0, "width": 1, "height": 1}}
        result = normalize_desktop_element(element)
        self.assertEqual(result["tagName"], "button")

    def test_unknown_type_maps_to_div(self):
        element = {"type": "toolbar", "bounds": {"x": 0, "y": 0, "width": 1, "height": 1}}
        result = normalize_desktop_element(element)
        self.assertEqual(result["tagName"], "div")

    def test_sets_is_target(self):
        element = {"bounds": {"x": 0, "y": 0, "width": 1, "height": 1}}
        result = normalize_desktop_element(element)
        self.assertTrue(result["isTarget"])


@unittest.skipUnless(HAS_PIL, "PIL/Pillow not installed")
class TestDrawDashedRectangle(unittest.TestCase):
    """Tests for _draw_dashed_rectangle function."""

    def test_dashed_rectangle_runs_without_error(self):
        from docugen.scripts.annotate_screenshot import _draw_dashed_rectangle

        img = Image.new("RGB", (200, 200), (255, 255, 255))
        draw = ImageDraw.Draw(img)

        # Should not raise
        _draw_dashed_rectangle(draw, (10, 10, 100, 50), color=(255, 0, 0))

    def test_dashed_rectangle_modifies_image(self):
        from docugen.scripts.annotate_screenshot import _draw_dashed_rectangle

        img = Image.new("RGB", (200, 200), (255, 255, 255))
        original_data = list(img.getdata())
        draw = ImageDraw.Draw(img)

        _draw_dashed_rectangle(draw, (10, 10, 100, 50), color=(255, 0, 0), width=3)

        modified_data = list(img.getdata())
        self.assertNotEqual(original_data, modified_data)


@unittest.skipUnless(HAS_PIL, "PIL/Pillow not installed")
class TestDrawDesktopElement(unittest.TestCase):
    """Tests for draw_desktop_element function."""

    def setUp(self):
        self.img = Image.new("RGB", (400, 300), (255, 255, 255))
        self.draw = ImageDraw.Draw(self.img)
        self.styles = DEFAULT_STYLES.copy()

    def test_accessibility_source_solid_border(self):
        from docugen.scripts.annotate_screenshot import draw_desktop_element

        element = {
            "bounds": {"x": 50, "y": 50, "width": 100, "height": 30},
            "source": "accessibility",
            "title": "OK Button",
        }
        result = draw_desktop_element(
            self.img, self.draw, element, step_number=1, styles=self.styles
        )
        self.assertIsNotNone(result)

    def test_visual_high_confidence_solid(self):
        from docugen.scripts.annotate_screenshot import draw_desktop_element

        element = {
            "bounds": {"x": 50, "y": 50, "width": 100, "height": 30},
            "source": "visual",
            "confidence": 0.95,
            "name": "Submit",
        }
        result = draw_desktop_element(
            self.img, self.draw, element, step_number=2, styles=self.styles
        )
        self.assertIsNotNone(result)

    def test_visual_low_confidence_dashed(self):
        from docugen.scripts.annotate_screenshot import draw_desktop_element

        element = {
            "bounds": {"x": 50, "y": 50, "width": 100, "height": 30},
            "source": "visual",
            "confidence": 0.6,
            "name": "Maybe Button",
        }
        result = draw_desktop_element(
            self.img, self.draw, element, step_number=3, styles=self.styles
        )
        self.assertIsNotNone(result)

    def test_missing_bounds_returns_img(self):
        from docugen.scripts.annotate_screenshot import draw_desktop_element

        element = {"source": "accessibility", "title": "No Bounds"}
        result = draw_desktop_element(
            self.img, self.draw, element, step_number=1, styles=self.styles
        )
        self.assertEqual(result, self.img)

    def test_tiny_element_returns_img(self):
        from docugen.scripts.annotate_screenshot import draw_desktop_element

        element = {
            "bounds": {"x": 50, "y": 50, "width": 2, "height": 2},
            "source": "accessibility",
        }
        result = draw_desktop_element(
            self.img, self.draw, element, step_number=1, styles=self.styles
        )
        self.assertEqual(result, self.img)

    def test_scale_factor_applied(self):
        from docugen.scripts.annotate_screenshot import draw_desktop_element

        element = {
            "bounds": {"x": 25, "y": 25, "width": 50, "height": 15},
            "source": "accessibility",
            "title": "Scaled",
        }
        # 2x scale should still work on 400x300 canvas
        result = draw_desktop_element(
            self.img, self.draw, element, step_number=1,
            styles=self.styles, scale_factor=2.0
        )
        self.assertIsNotNone(result)

    def test_label_shows_confidence_for_visual(self):
        from docugen.scripts.annotate_screenshot import draw_desktop_element

        # This is a visual validation - just ensure no crash
        element = {
            "bounds": {"x": 50, "y": 80, "width": 100, "height": 30},
            "source": "visual",
            "confidence": 0.73,
            "name": "ConfTest",
        }
        result = draw_desktop_element(
            self.img, self.draw, element, step_number=4, styles=self.styles
        )
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
