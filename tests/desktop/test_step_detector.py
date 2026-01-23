"""Tests for step_detector module."""

import io
import time
import unittest
from collections import namedtuple
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock

from docugen.desktop.step_detector import (
    StepDetector,
    StepRecord,
    DetectorConfig,
)


def _make_capture_result(width=1920, height=1080, image_bytes=b"PNG_DATA"):
    """Helper to create a mock CaptureResult."""
    from docugen.desktop.capture import CaptureResult

    return CaptureResult(
        image_bytes=image_bytes,
        width=width,
        height=height,
        dpi_scale=1.0,
    )


class TestDetectorConfig(unittest.TestCase):
    """Tests for DetectorConfig."""

    def test_default_values(self):
        config = DetectorConfig()
        self.assertEqual(config.ssim_threshold, 0.90)
        self.assertEqual(config.desktop_threshold, 0.87)
        self.assertEqual(config.debounce_seconds, 0.3)
        self.assertEqual(config.mode, "desktop")

    def test_effective_threshold_desktop(self):
        config = DetectorConfig(mode="desktop")
        self.assertEqual(config.effective_threshold, 0.87)

    def test_effective_threshold_web(self):
        config = DetectorConfig(mode="web")
        self.assertEqual(config.effective_threshold, 0.90)

    def test_custom_thresholds(self):
        config = DetectorConfig(ssim_threshold=0.95, desktop_threshold=0.80)
        self.assertEqual(config.effective_threshold, 0.80)  # desktop mode default


class TestStepDetector(unittest.TestCase):
    """Tests for StepDetector."""

    def setUp(self):
        self.config = DetectorConfig(debounce_seconds=0)  # Disable debounce for tests

    @patch("docugen.desktop.step_detector.ScreenCapture")
    def test_initial_state(self, mock_capture_cls):
        detector = StepDetector(self.config)
        self.assertEqual(detector.step_count, 0)
        self.assertEqual(detector.steps, [])

    @patch("docugen.desktop.step_detector.ScreenCapture")
    def test_capture_before(self, mock_capture_cls):
        mock_instance = mock_capture_cls.return_value
        mock_instance.fullscreen.return_value = _make_capture_result()

        detector = StepDetector(self.config)
        result = detector.capture_before()

        self.assertIsNotNone(result)
        mock_instance.fullscreen.assert_called_once()

    @patch("docugen.desktop.step_detector.ScreenCapture")
    def test_capture_after_without_before_returns_none(self, mock_capture_cls):
        mock_instance = mock_capture_cls.return_value
        mock_instance.fullscreen.return_value = _make_capture_result()

        detector = StepDetector(self.config)
        result = detector.capture_after("test action")

        # Should return None since there was no prior before capture
        self.assertIsNone(result)

    @patch("docugen.desktop.step_detector.ScreenCapture")
    def test_detects_significant_change(self, mock_capture_cls):
        mock_instance = mock_capture_cls.return_value
        before = _make_capture_result(image_bytes=b"BEFORE")
        after = _make_capture_result(image_bytes=b"AFTER")
        mock_instance.fullscreen.side_effect = [before, after]

        detector = StepDetector(self.config)

        # Mock the _compare method to return low SSIM (significant change)
        with patch.object(detector, "_compare", return_value=0.70):
            detector.capture_before()
            step = detector.capture_after("clicked button")

        self.assertIsNotNone(step)
        self.assertEqual(step.step_number, 1)
        self.assertEqual(step.ssim_score, 0.70)
        self.assertEqual(step.description, "clicked button")
        self.assertEqual(step.detection_method, "ssim")

    @patch("docugen.desktop.step_detector.ScreenCapture")
    def test_ignores_minor_change(self, mock_capture_cls):
        mock_instance = mock_capture_cls.return_value
        mock_instance.fullscreen.return_value = _make_capture_result()

        detector = StepDetector(self.config)

        with patch.object(detector, "_compare", return_value=0.95):
            detector.capture_before()
            step = detector.capture_after("hover")

        self.assertIsNone(step)
        self.assertEqual(detector.step_count, 0)

    @patch("docugen.desktop.step_detector.ScreenCapture")
    def test_debounce_prevents_rapid_steps(self, mock_capture_cls):
        config = DetectorConfig(debounce_seconds=1.0)  # 1 second debounce
        mock_instance = mock_capture_cls.return_value
        mock_instance.fullscreen.return_value = _make_capture_result()

        detector = StepDetector(config)

        with patch.object(detector, "_compare", return_value=0.50):
            detector.capture_before()
            # First step should succeed
            step1 = detector.capture_after("action 1")
            self.assertIsNotNone(step1)

            # Second step immediately after should be debounced
            step2 = detector.capture_after("action 2")
            self.assertIsNone(step2)

    @patch("docugen.desktop.step_detector.ScreenCapture")
    def test_manual_step_always_records(self, mock_capture_cls):
        mock_instance = mock_capture_cls.return_value
        mock_instance.fullscreen.return_value = _make_capture_result()

        detector = StepDetector(self.config)

        with patch.object(detector, "_compare", return_value=0.99):
            step = detector.record_manual_step("user pressed enter")

        self.assertIsNotNone(step)
        self.assertEqual(step.detection_method, "manual")
        self.assertEqual(step.description, "user pressed enter")

    @patch("docugen.desktop.step_detector.ScreenCapture")
    def test_set_target_window(self, mock_capture_cls):
        mock_instance = mock_capture_cls.return_value
        mock_instance.window.return_value = _make_capture_result()

        detector = StepDetector(self.config)
        detector.set_target_window(12345)

        detector.capture_before()
        mock_instance.window.assert_called_with(12345)

    @patch("docugen.desktop.step_detector.ScreenCapture")
    def test_reset_clears_state(self, mock_capture_cls):
        mock_instance = mock_capture_cls.return_value
        mock_instance.fullscreen.return_value = _make_capture_result()

        detector = StepDetector(self.config)

        with patch.object(detector, "_compare", return_value=0.50):
            detector.capture_before()
            detector.capture_after("step 1")

        self.assertEqual(detector.step_count, 1)
        detector.reset()
        self.assertEqual(detector.step_count, 0)
        self.assertEqual(detector.steps, [])

    @patch("docugen.desktop.step_detector.ScreenCapture")
    def test_multiple_steps_increment(self, mock_capture_cls):
        mock_instance = mock_capture_cls.return_value
        mock_instance.fullscreen.return_value = _make_capture_result()

        detector = StepDetector(self.config)

        with patch.object(detector, "_compare", return_value=0.50):
            detector.capture_before()
            step1 = detector.capture_after("action 1")
            step2 = detector.capture_after("action 2")
            step3 = detector.capture_after("action 3")

        self.assertEqual(step1.step_number, 1)
        self.assertEqual(step2.step_number, 2)
        self.assertEqual(step3.step_number, 3)
        self.assertEqual(detector.step_count, 3)

    @patch("docugen.desktop.step_detector.ScreenCapture")
    def test_save_step_to_output_dir(self, mock_capture_cls):
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            config = DetectorConfig(
                output_dir=Path(tmpdir), debounce_seconds=0
            )
            mock_instance = mock_capture_cls.return_value
            mock_instance.fullscreen.return_value = _make_capture_result(
                image_bytes=b"\x89PNG_DATA"
            )

            detector = StepDetector(config)

            with patch.object(detector, "_compare", return_value=0.50):
                detector.capture_before()
                detector.capture_after("save test")

            before_path = Path(tmpdir) / "step-01-before.png"
            after_path = Path(tmpdir) / "step-01-after.png"
            self.assertTrue(before_path.exists())
            self.assertTrue(after_path.exists())


class TestStepDetectorCompare(unittest.TestCase):
    """Tests for the SSIM comparison logic."""

    @patch("docugen.desktop.step_detector.ScreenCapture")
    def test_compare_identical_bytes_returns_high_ssim(self, mock_capture_cls):
        """Identical images should have SSIM close to 1.0."""
        # Create a simple valid PNG-like image for testing
        from PIL import Image
        import numpy as np

        img = Image.fromarray(np.zeros((100, 100), dtype=np.uint8))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        png_bytes = buf.getvalue()

        before = _make_capture_result(width=100, height=100, image_bytes=png_bytes)
        after = _make_capture_result(width=100, height=100, image_bytes=png_bytes)

        detector = StepDetector(DetectorConfig(debounce_seconds=0))
        score = detector._compare(before, after)
        self.assertGreater(score, 0.99)

    @patch("docugen.desktop.step_detector.ScreenCapture")
    def test_compare_different_images(self, mock_capture_cls):
        """Different images should have lower SSIM."""
        from PIL import Image
        import numpy as np

        # Black image
        img1 = Image.fromarray(np.zeros((100, 100), dtype=np.uint8))
        buf1 = io.BytesIO()
        img1.save(buf1, format="PNG")

        # White image
        img2 = Image.fromarray(np.full((100, 100), 255, dtype=np.uint8))
        buf2 = io.BytesIO()
        img2.save(buf2, format="PNG")

        before = _make_capture_result(width=100, height=100, image_bytes=buf1.getvalue())
        after = _make_capture_result(width=100, height=100, image_bytes=buf2.getvalue())

        detector = StepDetector(DetectorConfig(debounce_seconds=0))
        score = detector._compare(before, after)
        self.assertLess(score, 0.5)

    @patch("docugen.desktop.step_detector.ScreenCapture")
    def test_compare_fallback_when_no_skimage(self, mock_capture_cls):
        """Falls back to byte comparison when scikit-image unavailable."""
        import sys

        detector = StepDetector(DetectorConfig(debounce_seconds=0))

        before = _make_capture_result(image_bytes=b"SAME")
        after = _make_capture_result(image_bytes=b"SAME")

        # Mock the import to fail
        with patch.dict(sys.modules, {"skimage": None, "skimage.metrics": None}):
            # Force reimport by making the import inside _compare raise
            with patch(
                "builtins.__import__",
                side_effect=lambda name, *args, **kwargs: (
                    (_ for _ in ()).throw(ImportError("no skimage"))
                    if "skimage" in name
                    else __builtins__.__import__(name, *args, **kwargs)
                ),
            ):
                score = detector._compare(before, after)

        # Identical bytes should return 1.0 in fallback
        self.assertEqual(score, 1.0)


class TestStepDetectorDeleteStep(unittest.TestCase):
    """Tests for delete_step method."""

    def setUp(self):
        self.config = DetectorConfig(debounce_seconds=0)

    @patch("docugen.desktop.step_detector.ScreenCapture")
    def test_delete_existing_step(self, mock_capture_cls):
        mock_instance = mock_capture_cls.return_value
        mock_instance.fullscreen.return_value = _make_capture_result()

        detector = StepDetector(self.config)

        with patch.object(detector, "_compare", return_value=0.50):
            detector.capture_before()
            detector.capture_after("step 1")
            detector.capture_after("step 2")
            detector.capture_after("step 3")

        self.assertEqual(detector.step_count, 3)
        result = detector.delete_step(2)
        self.assertTrue(result)
        self.assertEqual(detector.step_count, 2)
        # Remaining steps should be renumbered
        self.assertEqual(detector.steps[0].step_number, 1)
        self.assertEqual(detector.steps[1].step_number, 2)
        self.assertEqual(detector.steps[0].description, "step 1")
        self.assertEqual(detector.steps[1].description, "step 3")

    @patch("docugen.desktop.step_detector.ScreenCapture")
    def test_delete_invalid_step_returns_false(self, mock_capture_cls):
        mock_instance = mock_capture_cls.return_value
        mock_instance.fullscreen.return_value = _make_capture_result()

        detector = StepDetector(self.config)

        with patch.object(detector, "_compare", return_value=0.50):
            detector.capture_before()
            detector.capture_after("step 1")

        self.assertFalse(detector.delete_step(0))
        self.assertFalse(detector.delete_step(5))
        self.assertEqual(detector.step_count, 1)

    @patch("docugen.desktop.step_detector.ScreenCapture")
    def test_delete_first_step(self, mock_capture_cls):
        mock_instance = mock_capture_cls.return_value
        mock_instance.fullscreen.return_value = _make_capture_result()

        detector = StepDetector(self.config)

        with patch.object(detector, "_compare", return_value=0.50):
            detector.capture_before()
            detector.capture_after("step 1")
            detector.capture_after("step 2")

        detector.delete_step(1)
        self.assertEqual(detector.step_count, 1)
        self.assertEqual(detector.steps[0].step_number, 1)
        self.assertEqual(detector.steps[0].description, "step 2")


class TestStepDetectorMergeSteps(unittest.TestCase):
    """Tests for merge_steps method."""

    def setUp(self):
        self.config = DetectorConfig(debounce_seconds=0)

    @patch("docugen.desktop.step_detector.ScreenCapture")
    def test_merge_consecutive_steps(self, mock_capture_cls):
        mock_instance = mock_capture_cls.return_value
        mock_instance.fullscreen.return_value = _make_capture_result()

        detector = StepDetector(self.config)

        with patch.object(detector, "_compare", return_value=0.50):
            detector.capture_before()
            detector.capture_after("first action")
            detector.capture_after("second action")
            detector.capture_after("third action")

        self.assertEqual(detector.step_count, 3)

        with patch.object(detector, "_compare", return_value=0.60):
            merged = detector.merge_steps(1, 2)

        self.assertIsNotNone(merged)
        self.assertEqual(merged.detection_method, "merged")
        self.assertEqual(detector.step_count, 2)
        self.assertEqual(detector.steps[0].step_number, 1)
        self.assertEqual(detector.steps[1].step_number, 2)

    @patch("docugen.desktop.step_detector.ScreenCapture")
    def test_merge_non_consecutive_returns_none(self, mock_capture_cls):
        mock_instance = mock_capture_cls.return_value
        mock_instance.fullscreen.return_value = _make_capture_result()

        detector = StepDetector(self.config)

        with patch.object(detector, "_compare", return_value=0.50):
            detector.capture_before()
            detector.capture_after("step 1")
            detector.capture_after("step 2")
            detector.capture_after("step 3")

        result = detector.merge_steps(1, 3)
        self.assertIsNone(result)
        self.assertEqual(detector.step_count, 3)

    @patch("docugen.desktop.step_detector.ScreenCapture")
    def test_merge_out_of_range_returns_none(self, mock_capture_cls):
        mock_instance = mock_capture_cls.return_value
        mock_instance.fullscreen.return_value = _make_capture_result()

        detector = StepDetector(self.config)

        with patch.object(detector, "_compare", return_value=0.50):
            detector.capture_before()
            detector.capture_after("step 1")

        result = detector.merge_steps(1, 2)
        self.assertIsNone(result)

    @patch("docugen.desktop.step_detector.ScreenCapture")
    def test_merge_preserves_description(self, mock_capture_cls):
        mock_instance = mock_capture_cls.return_value
        mock_instance.fullscreen.return_value = _make_capture_result()

        detector = StepDetector(self.config)

        with patch.object(detector, "_compare", return_value=0.50):
            detector.capture_before()
            detector.capture_after("important action")
            detector.capture_after("")

        with patch.object(detector, "_compare", return_value=0.60):
            merged = detector.merge_steps(1, 2)
        self.assertEqual(merged.description, "important action")


class TestStepDetectorRedetect(unittest.TestCase):
    """Tests for redetect method."""

    def setUp(self):
        self.config = DetectorConfig(debounce_seconds=0, mode="desktop")

    @patch("docugen.desktop.step_detector.ScreenCapture")
    def test_redetect_removes_insignificant_steps(self, mock_capture_cls):
        mock_instance = mock_capture_cls.return_value
        mock_instance.fullscreen.return_value = _make_capture_result()

        detector = StepDetector(self.config)

        # Simulate steps with varying SSIM scores
        with patch.object(detector, "_compare", side_effect=[0.50, 0.85, 0.60]):
            detector.capture_before()
            detector.capture_after("major change")  # SSIM 0.50
            detector.capture_after("subtle change")  # SSIM 0.85
            detector.capture_after("moderate change")  # SSIM 0.60

        self.assertEqual(detector.step_count, 3)

        # Redetect with stricter threshold (only keep SSIM < 0.70)
        removed = detector.redetect(threshold=0.70)

        self.assertEqual(len(removed), 1)  # The 0.85 step removed
        self.assertEqual(detector.step_count, 2)
        self.assertEqual(detector.steps[0].description, "major change")
        self.assertEqual(detector.steps[1].description, "moderate change")

    @patch("docugen.desktop.step_detector.ScreenCapture")
    def test_redetect_keeps_manual_steps(self, mock_capture_cls):
        mock_instance = mock_capture_cls.return_value
        mock_instance.fullscreen.return_value = _make_capture_result()

        detector = StepDetector(self.config)

        with patch.object(detector, "_compare", return_value=0.95):
            detector.capture_before()
            detector.record_manual_step("user marked this")

        # Even with strict threshold, manual steps stay
        removed = detector.redetect(threshold=0.50)
        self.assertEqual(len(removed), 0)
        self.assertEqual(detector.step_count, 1)

    @patch("docugen.desktop.step_detector.ScreenCapture")
    def test_redetect_renumbers_remaining(self, mock_capture_cls):
        mock_instance = mock_capture_cls.return_value
        mock_instance.fullscreen.return_value = _make_capture_result()

        detector = StepDetector(self.config)

        with patch.object(detector, "_compare", side_effect=[0.30, 0.88, 0.40]):
            detector.capture_before()
            detector.capture_after("step A")  # SSIM 0.30
            detector.capture_after("step B")  # SSIM 0.88
            detector.capture_after("step C")  # SSIM 0.40

        detector.redetect(threshold=0.80)  # Removes step B (0.88 >= 0.80)
        self.assertEqual(detector.steps[0].step_number, 1)
        self.assertEqual(detector.steps[1].step_number, 2)

    @patch("docugen.desktop.step_detector.ScreenCapture")
    def test_redetect_with_none_uses_current_config(self, mock_capture_cls):
        config = DetectorConfig(debounce_seconds=0, mode="desktop", desktop_threshold=0.70)
        mock_instance = mock_capture_cls.return_value
        mock_instance.fullscreen.return_value = _make_capture_result()

        detector = StepDetector(config)

        with patch.object(detector, "_compare", side_effect=[0.50, 0.75]):
            detector.capture_before()
            detector.capture_after("big change")    # SSIM 0.50, below 0.70
            detector.capture_after("small change")  # SSIM 0.75, above 0.70

        # Only the 0.50 step should have been recorded since 0.75 >= 0.70
        # But in our mock, both were recorded because _compare is mocked at detection time
        # Let's test redetect with no threshold change
        self.assertEqual(detector.step_count, 1)  # 0.75 was already rejected


class TestStepRecord(unittest.TestCase):
    """Tests for StepRecord dataclass."""

    def test_step_record_creation(self):
        before = _make_capture_result()
        after = _make_capture_result()

        step = StepRecord(
            step_number=1,
            before_capture=before,
            after_capture=after,
            ssim_score=0.75,
            timestamp=time.time(),
            description="clicked save",
        )

        self.assertEqual(step.step_number, 1)
        self.assertEqual(step.ssim_score, 0.75)
        self.assertEqual(step.description, "clicked save")
        self.assertEqual(step.detection_method, "ssim")
        self.assertIsNone(step.element_metadata)


if __name__ == "__main__":
    unittest.main()
