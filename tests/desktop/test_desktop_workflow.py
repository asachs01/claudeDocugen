"""Tests for desktop_workflow module."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from docugen.desktop.desktop_workflow import (
    DesktopWorkflow,
    WorkflowConfig,
    WorkflowStep,
)


class TestWorkflowConfig(unittest.TestCase):
    """Tests for WorkflowConfig defaults."""

    def test_defaults(self):
        config = WorkflowConfig()
        self.assertEqual(config.ssim_threshold, 0.87)
        self.assertEqual(config.debounce_ms, 300)
        self.assertEqual(config.output_dir, "./docugen_output")
        self.assertIsNone(config.capture_window)
        self.assertTrue(config.include_frontmatter)

    def test_custom_values(self):
        config = WorkflowConfig(ssim_threshold=0.90, debounce_ms=500)
        self.assertEqual(config.ssim_threshold, 0.90)
        self.assertEqual(config.debounce_ms, 500)


class TestDesktopWorkflowInit(unittest.TestCase):
    """Tests for DesktopWorkflow initialization."""

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_init_sets_title(self, mock_cap, mock_det, mock_backend):
        wf = DesktopWorkflow(title="Test Workflow")
        self.assertEqual(wf.title, "Test Workflow")
        self.assertFalse(wf._started)

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_init_uses_custom_config(self, mock_cap, mock_det, mock_backend):
        config = WorkflowConfig(ssim_threshold=0.92)
        wf = DesktopWorkflow(title="Test", config=config)
        self.assertEqual(wf.config.ssim_threshold, 0.92)


class TestDesktopWorkflowStart(unittest.TestCase):
    """Tests for workflow start."""

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_start_creates_output_dir(self, mock_cap, mock_det, mock_backend):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = WorkflowConfig(output_dir=tmpdir)
            wf = DesktopWorkflow(title="Test", config=config)
            wf.start(app_name="Settings")

            self.assertTrue(wf._started)
            self.assertEqual(wf._app_name, "Settings")
            self.assertTrue(Path(tmpdir, "images").exists())

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_start_with_description(self, mock_cap, mock_det, mock_backend):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = WorkflowConfig(output_dir=tmpdir)
            wf = DesktopWorkflow(title="Test", config=config)
            wf.start(description="How to change resolution")
            self.assertEqual(wf._description, "How to change resolution")


class TestDesktopWorkflowCaptureStep(unittest.TestCase):
    """Tests for step capture."""

    @patch("docugen.desktop.desktop_workflow.get_element_metadata")
    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_capture_requires_start(self, mock_cap, mock_det, mock_backend, mock_meta):
        wf = DesktopWorkflow(title="Test")
        with self.assertRaises(RuntimeError):
            wf.capture_step(description="Click something")

    @patch("docugen.desktop.desktop_workflow.get_element_metadata")
    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_capture_step_with_click_coords(self, mock_cap, mock_det, mock_backend, mock_meta):
        mock_meta.return_value = {"title": "OK", "source": "accessibility"}
        mock_det_instance = MagicMock()
        mock_record = MagicMock()
        mock_record.ssim_score = 0.75
        mock_record.before_capture.path = "/tmp/before.png"
        mock_record.after_capture.path = "/tmp/after.png"
        mock_det_instance.record_manual_step.return_value = mock_record
        mock_det.return_value = mock_det_instance

        with tempfile.TemporaryDirectory() as tmpdir:
            config = WorkflowConfig(output_dir=tmpdir)
            wf = DesktopWorkflow(title="Test", config=config)
            wf.start()

            result = wf.capture_step(
                description="Click OK",
                click_coords=(100, 200),
                force=True,
            )

            self.assertIsNotNone(result)
            self.assertEqual(result.description, "Click OK")
            self.assertEqual(result.element["title"], "OK")

    @patch("docugen.desktop.desktop_workflow.get_element_metadata")
    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_debounce_skips_rapid_captures(self, mock_cap, mock_det, mock_backend, mock_meta):
        mock_det_instance = MagicMock()
        mock_record = MagicMock()
        mock_record.ssim_score = 0.5
        mock_record.before_capture.path = "/tmp/before.png"
        mock_record.after_capture.path = "/tmp/after.png"
        mock_det_instance.record_manual_step.return_value = mock_record
        mock_det.return_value = mock_det_instance

        with tempfile.TemporaryDirectory() as tmpdir:
            config = WorkflowConfig(output_dir=tmpdir, debounce_ms=5000)
            wf = DesktopWorkflow(title="Test", config=config)
            wf.start()

            # First capture should work (force=True to bypass initial time)
            result1 = wf.capture_step("First", force=True)
            self.assertIsNotNone(result1)

            # Second capture should be debounced
            result2 = wf.capture_step("Second")
            self.assertIsNone(result2)


class TestDesktopWorkflowManualStep(unittest.TestCase):
    """Tests for manual step addition."""

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_add_manual_step(self, mock_cap, mock_det, mock_backend):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = WorkflowConfig(output_dir=tmpdir)
            wf = DesktopWorkflow(title="Test", config=config)
            wf.start()

            result = wf.add_manual_step(
                description="Press Cmd+S",
                element={"title": "Save", "source": "manual"},
            )

            self.assertEqual(result.step_number, 1)
            self.assertEqual(result.description, "Press Cmd+S")
            self.assertEqual(result.ssim_score, 0.0)
            self.assertTrue(result.is_significant)

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_manual_step_requires_start(self, mock_cap, mock_det, mock_backend):
        wf = DesktopWorkflow(title="Test")
        with self.assertRaises(RuntimeError):
            wf.add_manual_step(description="oops")


class TestDesktopWorkflowFinish(unittest.TestCase):
    """Tests for workflow finish."""

    @patch("docugen.desktop.desktop_workflow.detector_to_workflow_data")
    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_finish_returns_workflow_data(self, mock_cap, mock_det, mock_backend, mock_adapter):
        mock_adapter.return_value = {
            "title": "Test",
            "steps": [],
            "app_name": "Settings",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config = WorkflowConfig(output_dir=tmpdir)
            wf = DesktopWorkflow(title="Test", config=config)
            wf.start(app_name="Settings")

            result = wf.finish()

            self.assertEqual(result["mode"], "desktop")
            self.assertIn("config", result)
            self.assertEqual(result["config"]["ssim_threshold"], 0.87)

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_finish_requires_start(self, mock_cap, mock_det, mock_backend):
        wf = DesktopWorkflow(title="Test")
        with self.assertRaises(RuntimeError):
            wf.finish()

    @patch("docugen.desktop.desktop_workflow.detector_to_workflow_data")
    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_finish_resets_started(self, mock_cap, mock_det, mock_backend, mock_adapter):
        mock_adapter.return_value = {"title": "T", "steps": []}

        with tempfile.TemporaryDirectory() as tmpdir:
            config = WorkflowConfig(output_dir=tmpdir)
            wf = DesktopWorkflow(title="T", config=config)
            wf.start()
            wf.finish()
            self.assertFalse(wf._started)


class TestDesktopWorkflowGetSteps(unittest.TestCase):
    """Tests for get_steps."""

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_get_steps_returns_copy(self, mock_cap, mock_det, mock_backend):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = WorkflowConfig(output_dir=tmpdir)
            wf = DesktopWorkflow(title="Test", config=config)
            wf.start()

            wf.add_manual_step("Step 1")
            wf.add_manual_step("Step 2")

            steps = wf.get_steps()
            self.assertEqual(len(steps), 2)
            # Verify it's a copy
            steps.pop()
            self.assertEqual(len(wf.get_steps()), 2)


if __name__ == "__main__":
    unittest.main()
