from .capture import ScreenCapture
from .platform_utils import get_platform, PlatformInfo
from .monitor_manager import MonitorManager
from .window_enumerator import WindowEnumerator
from .platform_router import get_accessibility_backend, get_capture_capabilities
from .step_detector import StepDetector, StepRecord, DetectorConfig

__all__ = [
    "ScreenCapture",
    "get_platform",
    "PlatformInfo",
    "MonitorManager",
    "WindowEnumerator",
    "get_accessibility_backend",
    "get_capture_capabilities",
    "StepDetector",
    "StepRecord",
    "DetectorConfig",
]
