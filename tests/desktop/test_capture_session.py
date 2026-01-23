"""Tests for capture_session module."""

import tempfile
import time
import unittest
from unittest.mock import MagicMock, patch

from docugen.desktop.capture_session import (
    CaptureSession,
    EventType,
    HotkeyConfig,
    SessionEvent,
    SessionState,
)
from docugen.desktop.desktop_workflow import WorkflowConfig


class TestCaptureSessionInit(unittest.TestCase):
    """Tests for CaptureSession initialization."""

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_init_defaults(self, mock_cap, mock_det, mock_backend):
        session = CaptureSession(title="Test Session")
        self.assertEqual(session.state, SessionState.IDLE)
        self.assertEqual(session.step_count, 0)

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_init_with_app_name(self, mock_cap, mock_det, mock_backend):
        session = CaptureSession(
            title="Test",
            app_name="System Settings",
            description="Change resolution",
        )
        self.assertEqual(session._app_name, "System Settings")
        self.assertEqual(session._description, "Change resolution")

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_init_with_custom_config(self, mock_cap, mock_det, mock_backend):
        config = WorkflowConfig(ssim_threshold=0.90)
        session = CaptureSession(title="Test", config=config)
        self.assertEqual(session._workflow.config.ssim_threshold, 0.90)


class TestCaptureSessionStart(unittest.TestCase):
    """Tests for starting a capture session."""

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_start_changes_state(self, mock_cap, mock_det, mock_backend):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = WorkflowConfig(output_dir=tmpdir)
            session = CaptureSession(title="Test", config=config)
            result = session.start()

            self.assertEqual(session.state, SessionState.RECORDING)
            self.assertEqual(result["status"], "recording")

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_start_without_hotkeys(self, mock_cap, mock_det, mock_backend):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = WorkflowConfig(output_dir=tmpdir)
            session = CaptureSession(title="Test", config=config)
            result = session.start(use_hotkeys=False)

            self.assertFalse(result["hotkeys_active"])
            self.assertIsNone(result["hotkey_config"])

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_start_twice_raises(self, mock_cap, mock_det, mock_backend):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = WorkflowConfig(output_dir=tmpdir)
            session = CaptureSession(title="Test", config=config)
            session.start()
            with self.assertRaises(RuntimeError):
                session.start()


class TestCaptureSessionRecord(unittest.TestCase):
    """Tests for recording steps."""

    @patch("docugen.desktop.desktop_workflow.get_element_metadata")
    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_record_step(self, mock_cap, mock_det, mock_backend, mock_meta):
        mock_det_instance = MagicMock()
        mock_record = MagicMock()
        mock_record.ssim_score = 0.65
        mock_record.before_capture.path = "/tmp/before.png"
        mock_record.after_capture.path = "/tmp/after.png"
        mock_det_instance.record_manual_step.return_value = mock_record
        mock_det.return_value = mock_det_instance

        with tempfile.TemporaryDirectory() as tmpdir:
            config = WorkflowConfig(output_dir=tmpdir)
            session = CaptureSession(title="Test", config=config)
            session.start()

            step = session.record_step("Click Save button")
            self.assertIsNotNone(step)
            self.assertEqual(step.description, "Click Save button")
            self.assertEqual(session.step_count, 1)

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_record_step_not_recording(self, mock_cap, mock_det, mock_backend):
        session = CaptureSession(title="Test")
        result = session.record_step("Click something")
        self.assertIsNone(result)

    @patch("docugen.desktop.desktop_workflow.get_element_metadata")
    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_record_step_with_coords(self, mock_cap, mock_det, mock_backend, mock_meta):
        mock_meta.return_value = {"title": "OK", "source": "accessibility"}
        mock_det_instance = MagicMock()
        mock_record = MagicMock()
        mock_record.ssim_score = 0.70
        mock_record.before_capture.path = "/tmp/before.png"
        mock_record.after_capture.path = "/tmp/after.png"
        mock_det_instance.record_manual_step.return_value = mock_record
        mock_det.return_value = mock_det_instance

        with tempfile.TemporaryDirectory() as tmpdir:
            config = WorkflowConfig(output_dir=tmpdir)
            session = CaptureSession(title="Test", config=config)
            session.start()

            step = session.record_step("Click OK", coords=(150, 200))
            self.assertIsNotNone(step)
            self.assertEqual(step.element["title"], "OK")


class TestCaptureSessionKeyboard(unittest.TestCase):
    """Tests for keyboard shortcut steps."""

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_add_keyboard_step(self, mock_cap, mock_det, mock_backend):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = WorkflowConfig(output_dir=tmpdir)
            session = CaptureSession(title="Test", config=config)
            session.start()

            step = session.add_keyboard_step("Cmd+S")
            self.assertEqual(step.description, "Press Cmd+S")
            self.assertEqual(step.element["type"], "keyboard_shortcut")

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_add_keyboard_step_custom_description(self, mock_cap, mock_det, mock_backend):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = WorkflowConfig(output_dir=tmpdir)
            session = CaptureSession(title="Test", config=config)
            session.start()

            step = session.add_keyboard_step("Ctrl+Z", description="Undo last change")
            self.assertEqual(step.description, "Undo last change")

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_keyboard_step_requires_recording(self, mock_cap, mock_det, mock_backend):
        session = CaptureSession(title="Test")
        with self.assertRaises(RuntimeError):
            session.add_keyboard_step("Cmd+C")


class TestCaptureSessionPauseResume(unittest.TestCase):
    """Tests for pause/resume functionality."""

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_pause(self, mock_cap, mock_det, mock_backend):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = WorkflowConfig(output_dir=tmpdir)
            session = CaptureSession(title="Test", config=config)
            session.start()
            session.pause()
            self.assertEqual(session.state, SessionState.PAUSED)

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_resume(self, mock_cap, mock_det, mock_backend):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = WorkflowConfig(output_dir=tmpdir)
            session = CaptureSession(title="Test", config=config)
            session.start()
            session.pause()
            session.resume()
            self.assertEqual(session.state, SessionState.RECORDING)

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_pause_when_not_recording_noop(self, mock_cap, mock_det, mock_backend):
        session = CaptureSession(title="Test")
        session.pause()  # Should not raise
        self.assertEqual(session.state, SessionState.IDLE)

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_record_while_paused_returns_none(self, mock_cap, mock_det, mock_backend):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = WorkflowConfig(output_dir=tmpdir)
            session = CaptureSession(title="Test", config=config)
            session.start()
            session.pause()
            result = session.record_step("Click something")
            self.assertIsNone(result)


class TestCaptureSessionUndo(unittest.TestCase):
    """Tests for undo functionality."""

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_undo_last_step(self, mock_cap, mock_det, mock_backend):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = WorkflowConfig(output_dir=tmpdir)
            session = CaptureSession(title="Test", config=config)
            session.start()

            session._workflow.add_manual_step("Step 1")
            session._workflow.add_manual_step("Step 2")
            self.assertEqual(session.step_count, 2)

            removed = session.undo_last_step()
            self.assertIsNotNone(removed)
            self.assertEqual(removed.description, "Step 2")
            self.assertEqual(session.step_count, 1)

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_undo_empty_returns_none(self, mock_cap, mock_det, mock_backend):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = WorkflowConfig(output_dir=tmpdir)
            session = CaptureSession(title="Test", config=config)
            session.start()

            result = session.undo_last_step()
            self.assertIsNone(result)


class TestCaptureSessionFinish(unittest.TestCase):
    """Tests for finishing a session."""

    @patch("docugen.desktop.desktop_workflow.detector_to_workflow_data")
    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_finish_returns_workflow_data(self, mock_cap, mock_det, mock_backend, mock_adapter):
        mock_adapter.return_value = {"title": "Test", "steps": []}

        with tempfile.TemporaryDirectory() as tmpdir:
            config = WorkflowConfig(output_dir=tmpdir)
            session = CaptureSession(title="Test", config=config)
            session.start()
            result = session.finish()

            self.assertEqual(session.state, SessionState.FINISHED)
            self.assertIn("mode", result)
            self.assertEqual(result["mode"], "desktop")

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_finish_idle_raises(self, mock_cap, mock_det, mock_backend):
        session = CaptureSession(title="Test")
        with self.assertRaises(RuntimeError):
            session.finish()

    @patch("docugen.desktop.desktop_workflow.detector_to_workflow_data")
    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_finish_twice_raises(self, mock_cap, mock_det, mock_backend, mock_adapter):
        mock_adapter.return_value = {"title": "T", "steps": []}

        with tempfile.TemporaryDirectory() as tmpdir:
            config = WorkflowConfig(output_dir=tmpdir)
            session = CaptureSession(title="T", config=config)
            session.start()
            session.finish()
            with self.assertRaises(RuntimeError):
                session.finish()


class TestCaptureSessionEvents(unittest.TestCase):
    """Tests for event queue functionality."""

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_poll_events_empty(self, mock_cap, mock_det, mock_backend):
        session = CaptureSession(title="Test")
        events = session.poll_events()
        self.assertEqual(events, [])

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_poll_events_returns_queued(self, mock_cap, mock_det, mock_backend):
        session = CaptureSession(title="Test")
        # Manually enqueue an event
        session._events.put(SessionEvent(type=EventType.CAPTURE, coords=(100, 200)))
        session._events.put(SessionEvent(type=EventType.FINISH))

        events = session.poll_events()
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].type, EventType.CAPTURE)
        self.assertEqual(events[0].coords, (100, 200))
        self.assertEqual(events[1].type, EventType.FINISH)

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_wait_for_event_timeout(self, mock_cap, mock_det, mock_backend):
        session = CaptureSession(title="Test")
        result = session.wait_for_event(timeout=0.01)
        self.assertIsNone(result)

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_wait_for_event_returns_event(self, mock_cap, mock_det, mock_backend):
        session = CaptureSession(title="Test")
        event = SessionEvent(type=EventType.CAPTURE, coords=(50, 75))
        session._events.put(event)

        result = session.wait_for_event(timeout=1.0)
        self.assertIsNotNone(result)
        self.assertEqual(result.type, EventType.CAPTURE)


class TestCaptureSessionStatus(unittest.TestCase):
    """Tests for status and prompts."""

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_get_status(self, mock_cap, mock_det, mock_backend):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = WorkflowConfig(output_dir=tmpdir)
            session = CaptureSession(
                title="Test", app_name="Finder", config=config
            )
            session.start()

            status = session.get_status()
            self.assertEqual(status["state"], "recording")
            self.assertEqual(status["title"], "Test")
            self.assertEqual(status["app_name"], "Finder")
            self.assertEqual(status["steps_captured"], 0)

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_get_action_prompt(self, mock_cap, mock_det, mock_backend):
        session = CaptureSession(title="Test")
        prompt = session.get_action_prompt()

        self.assertIn("questions", prompt)
        self.assertEqual(len(prompt["questions"]), 1)
        q = prompt["questions"][0]
        self.assertIn("Step 1:", q["question"])
        self.assertEqual(len(q["options"]), 4)
        self.assertFalse(q["multiSelect"])

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_get_element_prompt(self, mock_cap, mock_det, mock_backend):
        session = CaptureSession(title="Test")
        prompt = session.get_element_prompt()

        self.assertIn("questions", prompt)
        q = prompt["questions"][0]
        self.assertEqual(len(q["options"]), 2)
        self.assertIn("describe", q["options"][0]["label"].lower())


class TestCaptureSessionHotkeys(unittest.TestCase):
    """Tests for hotkey listener integration."""

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_custom_hotkey_config(self, mock_cap, mock_det, mock_backend):
        hotkey_config = HotkeyConfig(
            capture_hotkey="<ctrl>+<alt>+c",
            finish_hotkey="<ctrl>+<alt>+f",
        )
        session = CaptureSession(title="Test", hotkey_config=hotkey_config)
        self.assertEqual(session._hotkey_config.capture_hotkey, "<ctrl>+<alt>+c")

    @patch("docugen.desktop.capture_session.HAS_PYNPUT", False)
    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_hotkeys_disabled_without_pynput(self, mock_cap, mock_det, mock_backend):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = WorkflowConfig(output_dir=tmpdir)
            session = CaptureSession(title="Test", config=config)
            result = session.start(use_hotkeys=True)

            self.assertFalse(result["hotkeys_active"])

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_on_capture_hotkey_queues_event(self, mock_cap, mock_det, mock_backend):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = WorkflowConfig(output_dir=tmpdir)
            session = CaptureSession(title="Test", config=config)
            session.start()

            # Simulate hotkey press directly
            session._on_capture_hotkey()

            events = session.poll_events()
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0].type, EventType.CAPTURE)

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_on_finish_hotkey_queues_event(self, mock_cap, mock_det, mock_backend):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = WorkflowConfig(output_dir=tmpdir)
            session = CaptureSession(title="Test", config=config)
            session.start()

            session._on_finish_hotkey()

            events = session.poll_events()
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0].type, EventType.FINISH)

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_on_pause_hotkey_toggles(self, mock_cap, mock_det, mock_backend):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = WorkflowConfig(output_dir=tmpdir)
            session = CaptureSession(title="Test", config=config)
            session.start()

            # First press pauses
            session._on_pause_hotkey()
            self.assertEqual(session.state, SessionState.PAUSED)

            # Second press resumes
            session._on_pause_hotkey()
            self.assertEqual(session.state, SessionState.RECORDING)

    @patch("docugen.desktop.desktop_workflow.get_accessibility_backend")
    @patch("docugen.desktop.desktop_workflow.StepDetector")
    @patch("docugen.desktop.desktop_workflow.ScreenCapture")
    def test_capture_hotkey_ignored_when_not_recording(self, mock_cap, mock_det, mock_backend):
        session = CaptureSession(title="Test")
        # Not started, hotkey should be ignored
        session._on_capture_hotkey()
        events = session.poll_events()
        self.assertEqual(len(events), 0)


class TestHotkeyConfig(unittest.TestCase):
    """Tests for HotkeyConfig defaults."""

    def test_defaults(self):
        config = HotkeyConfig()
        self.assertEqual(config.capture_hotkey, "<ctrl>+<shift>+d")
        self.assertEqual(config.finish_hotkey, "<ctrl>+<shift>+f")
        self.assertEqual(config.pause_hotkey, "<ctrl>+<shift>+p")

    def test_custom_values(self):
        config = HotkeyConfig(capture_hotkey="<cmd>+<shift>+r")
        self.assertEqual(config.capture_hotkey, "<cmd>+<shift>+r")


class TestSessionEvent(unittest.TestCase):
    """Tests for SessionEvent dataclass."""

    def test_capture_event(self):
        event = SessionEvent(type=EventType.CAPTURE, coords=(100, 200))
        self.assertEqual(event.type, EventType.CAPTURE)
        self.assertEqual(event.coords, (100, 200))
        self.assertIsNotNone(event.timestamp)

    def test_finish_event(self):
        event = SessionEvent(type=EventType.FINISH)
        self.assertIsNone(event.coords)


if __name__ == "__main__":
    unittest.main()
