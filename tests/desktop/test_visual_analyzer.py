"""Tests for visual_analyzer module."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from docugen.desktop.visual_analyzer import (
    analyze_screenshot,
    analyze_capture_result,
    _parse_response,
    _get_media_type,
)


def _create_temp_png():
    """Create a temporary PNG file for testing."""
    f = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    f.write(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
    f.close()
    return f.name


def _mock_api_response(text):
    """Create a mock Anthropic API response."""
    response = MagicMock()
    response.content = [MagicMock(text=text)]
    return response


class TestAnalyzeScreenshot(unittest.TestCase):
    """Tests for analyze_screenshot function."""

    def test_returns_none_for_missing_file(self):
        """Returns None when screenshot file doesn't exist."""
        result = analyze_screenshot("/nonexistent/path.png")
        self.assertIsNone(result)

    @patch("anthropic.Anthropic")
    def test_calls_api_and_parses_response(self, mock_anthropic_cls):
        """Calls Claude API with image and parses element response."""
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _mock_api_response(
            '[{"name": "Save", "type": "button", "bounds": {"x": 10, "y": 20, "width": 80, "height": 30}, "confidence": 0.9}]'
        )
        mock_anthropic_cls.return_value = mock_client

        temp_path = _create_temp_png()
        try:
            result = analyze_screenshot(temp_path)

            self.assertIsNotNone(result)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["name"], "Save")
            self.assertEqual(result[0]["type"], "button")
            self.assertEqual(result[0]["source"], "visual")
            self.assertEqual(result[0]["confidence"], 0.9)
        finally:
            Path(temp_path).unlink()

    @patch("anthropic.Anthropic")
    def test_focused_prompt_includes_coords(self, mock_anthropic_cls):
        """Uses focused prompt containing click coordinates."""
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _mock_api_response(
            '{"name": "Submit", "type": "button", "bounds": {"x": 100, "y": 200, "width": 60, "height": 25}, "confidence": 0.85}'
        )
        mock_anthropic_cls.return_value = mock_client

        temp_path = _create_temp_png()
        try:
            result = analyze_screenshot(temp_path, click_coords=(100, 200))

            self.assertIsNotNone(result)
            self.assertEqual(result[0]["name"], "Submit")

            call_args = mock_client.messages.create.call_args
            messages = call_args.kwargs["messages"]
            prompt_text = messages[0]["content"][1]["text"]
            self.assertIn("100", prompt_text)
            self.assertIn("200", prompt_text)
        finally:
            Path(temp_path).unlink()

    @patch("anthropic.Anthropic")
    def test_returns_none_on_api_error(self, mock_anthropic_cls):
        """Returns None when API call raises an exception."""
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = RuntimeError("API down")
        mock_anthropic_cls.return_value = mock_client

        temp_path = _create_temp_png()
        try:
            result = analyze_screenshot(temp_path)
            self.assertIsNone(result)
        finally:
            Path(temp_path).unlink()

    @patch("anthropic.Anthropic")
    def test_multiple_elements_returned(self, mock_anthropic_cls):
        """Parses multiple elements from response."""
        elements = [
            {"name": "Save", "type": "button", "bounds": {"x": 10, "y": 10, "width": 80, "height": 30}, "confidence": 0.9},
            {"name": "Cancel", "type": "button", "bounds": {"x": 100, "y": 10, "width": 80, "height": 30}, "confidence": 0.85},
            {"name": "Email", "type": "input", "bounds": {"x": 10, "y": 50, "width": 200, "height": 25}, "confidence": 0.8},
        ]
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _mock_api_response(json.dumps(elements))
        mock_anthropic_cls.return_value = mock_client

        temp_path = _create_temp_png()
        try:
            result = analyze_screenshot(temp_path)
            self.assertEqual(len(result), 3)
            self.assertEqual(result[2]["name"], "Email")
            self.assertEqual(result[2]["type"], "input")
        finally:
            Path(temp_path).unlink()


class TestAnalyzeCaptureResult(unittest.TestCase):
    """Tests for analyze_capture_result function."""

    @patch("anthropic.Anthropic")
    def test_analyzes_bytes_directly(self, mock_anthropic_cls):
        """Sends CaptureResult bytes to API without disk I/O."""
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _mock_api_response(
            '[{"name": "OK", "type": "button", "bounds": {"x": 50, "y": 60, "width": 40, "height": 20}, "confidence": 0.95}]'
        )
        mock_anthropic_cls.return_value = mock_client

        mock_capture = MagicMock()
        mock_capture.image_bytes = b"\x89PNG\r\n" + b"\x00" * 50

        result = analyze_capture_result(mock_capture)

        self.assertIsNotNone(result)
        self.assertEqual(result[0]["name"], "OK")
        self.assertEqual(result[0]["source"], "visual")

    @patch("anthropic.Anthropic")
    def test_uses_png_media_type(self, mock_anthropic_cls):
        """Sends image as PNG media type."""
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _mock_api_response(
            '[{"name": "X", "type": "icon", "bounds": {"x": 0, "y": 0, "width": 20, "height": 20}, "confidence": 0.7}]'
        )
        mock_anthropic_cls.return_value = mock_client

        mock_capture = MagicMock()
        mock_capture.image_bytes = b"DATA"

        analyze_capture_result(mock_capture)

        call_args = mock_client.messages.create.call_args
        messages = call_args.kwargs["messages"]
        image_content = messages[0]["content"][0]
        self.assertEqual(image_content["source"]["media_type"], "image/png")


class TestParseResponse(unittest.TestCase):
    """Tests for _parse_response."""

    def _mock_response(self, text):
        response = MagicMock()
        response.content = [MagicMock(text=text)]
        return response

    def test_parses_json_array(self):
        text = json.dumps([
            {"name": "Save", "type": "button", "bounds": {"x": 10, "y": 20, "width": 80, "height": 30}, "confidence": 0.9},
            {"name": "Cancel", "type": "button", "bounds": {"x": 100, "y": 20, "width": 80, "height": 30}, "confidence": 0.85},
        ])
        result = _parse_response(self._mock_response(text))
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "Save")
        self.assertEqual(result[1]["name"], "Cancel")

    def test_parses_single_object(self):
        text = json.dumps(
            {"name": "OK", "type": "button", "bounds": {"x": 50, "y": 60, "width": 40, "height": 20}, "confidence": 0.95}
        )
        result = _parse_response(self._mock_response(text), focused=True)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "OK")

    def test_strips_markdown_code_fence(self):
        text = "```json\n" + json.dumps([
            {"name": "Button", "type": "button", "bounds": {"x": 0, "y": 0, "width": 50, "height": 25}, "confidence": 0.8}
        ]) + "\n```"
        result = _parse_response(self._mock_response(text))
        self.assertIsNotNone(result)
        self.assertEqual(result[0]["name"], "Button")

    def test_returns_none_for_invalid_json(self):
        result = _parse_response(self._mock_response("not valid json at all"))
        self.assertIsNone(result)

    def test_returns_none_for_missing_bounds(self):
        text = json.dumps([{"name": "No bounds", "type": "button"}])
        result = _parse_response(self._mock_response(text))
        self.assertIsNone(result)

    def test_tags_elements_with_visual_source(self):
        text = json.dumps([
            {"name": "X", "type": "icon", "bounds": {"x": 0, "y": 0, "width": 20, "height": 20}, "confidence": 0.7}
        ])
        result = _parse_response(self._mock_response(text))
        self.assertEqual(result[0]["source"], "visual")

    def test_defaults_confidence_to_0_5(self):
        text = json.dumps([
            {"name": "Link", "type": "link", "bounds": {"x": 0, "y": 0, "width": 100, "height": 15}}
        ])
        result = _parse_response(self._mock_response(text))
        self.assertEqual(result[0]["confidence"], 0.5)

    def test_defaults_name_to_unknown(self):
        text = json.dumps([
            {"type": "button", "bounds": {"x": 0, "y": 0, "width": 50, "height": 25}}
        ])
        result = _parse_response(self._mock_response(text))
        self.assertEqual(result[0]["name"], "Unknown")


class TestGetMediaType(unittest.TestCase):
    """Tests for _get_media_type."""

    def test_png(self):
        self.assertEqual(_get_media_type(Path("test.png")), "image/png")

    def test_jpg(self):
        self.assertEqual(_get_media_type(Path("test.jpg")), "image/jpeg")

    def test_jpeg(self):
        self.assertEqual(_get_media_type(Path("test.jpeg")), "image/jpeg")

    def test_webp(self):
        self.assertEqual(_get_media_type(Path("test.webp")), "image/webp")

    def test_unknown_defaults_to_png(self):
        self.assertEqual(_get_media_type(Path("test.bmp")), "image/png")


if __name__ == "__main__":
    unittest.main()
