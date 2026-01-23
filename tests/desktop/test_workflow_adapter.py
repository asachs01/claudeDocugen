"""Tests for workflow_adapter module."""

import json
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from docugen.desktop.workflow_adapter import (
    steps_to_workflow_data,
    detector_to_workflow_data,
    save_workflow_json,
)
from docugen.desktop.step_detector import StepRecord, StepDetector, DetectorConfig
from docugen.desktop.capture import CaptureResult


def _make_capture_result(width=1920, height=1080, image_bytes=b"PNG_DATA"):
    return CaptureResult(
        image_bytes=image_bytes,
        width=width,
        height=height,
        dpi_scale=1.0,
    )


def _make_step(number, description="", ssim=0.70, element_metadata=None):
    return StepRecord(
        step_number=number,
        before_capture=_make_capture_result(),
        after_capture=_make_capture_result(),
        ssim_score=ssim,
        timestamp=time.time(),
        description=description,
        element_metadata=element_metadata,
    )


class TestStepsToWorkflowData(unittest.TestCase):
    """Tests for steps_to_workflow_data conversion."""

    @patch("docugen.desktop.workflow_adapter.get_platform")
    def test_basic_conversion(self, mock_platform):
        mock_platform.return_value = MagicMock(os_type="macos", dpi_scale=2.0)

        steps = [
            _make_step(1, "Click Save button"),
            _make_step(2, "Confirm dialog"),
        ]

        result = steps_to_workflow_data(
            steps,
            title="Save Document",
            description="How to save a document",
            app_name="TextEdit",
        )

        self.assertEqual(result["title"], "Save Document")
        self.assertEqual(result["description"], "How to save a document")
        self.assertEqual(result["mode"], "desktop")
        self.assertEqual(result["app_name"], "TextEdit")
        self.assertEqual(result["platform"]["os"], "macos")
        self.assertEqual(len(result["steps"]), 2)

    @patch("docugen.desktop.workflow_adapter.get_platform")
    def test_step_fields(self, mock_platform):
        mock_platform.return_value = MagicMock(os_type="windows", dpi_scale=1.0)

        steps = [_make_step(1, "Click button", ssim=0.65)]
        result = steps_to_workflow_data(steps, title="Test")

        step = result["steps"][0]
        self.assertEqual(step["number"], 1)
        self.assertEqual(step["title"], "Click button")
        self.assertEqual(step["mode"], "desktop")
        self.assertEqual(step["ssim_score"], 0.65)
        self.assertIn("timestamp", step)

    @patch("docugen.desktop.workflow_adapter.get_platform")
    def test_element_metadata_included(self, mock_platform):
        mock_platform.return_value = MagicMock(os_type="macos", dpi_scale=1.0)

        elem = {"name": "Save", "type": "button", "source": "accessibility"}
        steps = [_make_step(1, "Click Save", element_metadata=elem)]
        result = steps_to_workflow_data(steps, title="Test")

        self.assertEqual(result["steps"][0]["element"], elem)

    @patch("docugen.desktop.workflow_adapter.get_platform")
    def test_image_dir_paths(self, mock_platform):
        mock_platform.return_value = MagicMock(os_type="macos", dpi_scale=1.0)

        steps = [_make_step(1, "action")]
        result = steps_to_workflow_data(
            steps, title="Test", image_dir=Path("/output/images")
        )

        self.assertEqual(result["steps"][0]["screenshot"], "/output/images/step-01-after.png")

    @patch("docugen.desktop.workflow_adapter.get_platform")
    def test_default_image_paths(self, mock_platform):
        mock_platform.return_value = MagicMock(os_type="macos", dpi_scale=1.0)

        steps = [_make_step(3, "action")]
        result = steps_to_workflow_data(steps, title="Test")

        self.assertEqual(result["steps"][0]["screenshot"], "./images/step-03-after.png")

    @patch("docugen.desktop.workflow_adapter.get_platform")
    def test_empty_description_uses_step_number(self, mock_platform):
        mock_platform.return_value = MagicMock(os_type="macos", dpi_scale=1.0)

        steps = [_make_step(1, "")]
        result = steps_to_workflow_data(steps, title="Test")

        self.assertEqual(result["steps"][0]["title"], "Step 1")


class TestDetectorToWorkflowData(unittest.TestCase):
    """Tests for detector_to_workflow_data convenience wrapper."""

    @patch("docugen.desktop.workflow_adapter.get_platform")
    @patch("docugen.desktop.step_detector.ScreenCapture")
    def test_extracts_from_detector(self, mock_capture_cls, mock_platform):
        mock_platform.return_value = MagicMock(os_type="macos", dpi_scale=1.0)
        mock_instance = mock_capture_cls.return_value
        mock_instance.fullscreen.return_value = _make_capture_result()

        config = DetectorConfig(debounce_seconds=0, output_dir=Path("/tmp/out"))
        detector = StepDetector(config)

        with patch.object(detector, "_compare", return_value=0.50):
            detector.capture_before()
            detector.capture_after("clicked button")

        result = detector_to_workflow_data(
            detector, title="My Workflow", app_name="Finder"
        )

        self.assertEqual(result["title"], "My Workflow")
        self.assertEqual(result["app_name"], "Finder")
        self.assertEqual(len(result["steps"]), 1)


class TestSaveWorkflowJson(unittest.TestCase):
    """Tests for save_workflow_json."""

    def test_writes_valid_json(self):
        data = {"title": "Test", "steps": []}

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "workflow.json"
            save_workflow_json(data, path)

            loaded = json.loads(path.read_text())
            self.assertEqual(loaded["title"], "Test")

    def test_creates_parent_dirs(self):
        data = {"title": "Test"}

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sub" / "dir" / "workflow.json"
            save_workflow_json(data, path)
            self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()
