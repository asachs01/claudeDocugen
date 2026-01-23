from .capture import ScreenCapture
from .platform_utils import get_platform, PlatformInfo
from .monitor_manager import MonitorManager
from .window_enumerator import WindowEnumerator
from .platform_router import get_accessibility_backend, get_capture_capabilities
from .step_detector import StepDetector, StepRecord, DetectorConfig
from .vision_cache import VisionCache
from .mode_detection import detect_mode
from .workflow_adapter import steps_to_workflow_data, detector_to_workflow_data
from .element_metadata import Rect, ElementMetadata
from .coordinate_transforms import (
    scale_bounds,
    clip_bounds_to_image,
    validate_screen_coordinates,
    transform_to_image_coordinates,
    get_dpi_scale_factor,
)
from .metadata_normalization import (
    normalize_windows_metadata,
    normalize_macos_metadata,
    get_confidence_score,
    dict_to_element_metadata,
)
from .fallback_manager import (
    FallbackManager,
    get_element_metadata_with_fallback,
)
from .fallback_config import FallbackConfig
from .fallback_metrics import MetricsCollector

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
    "VisionCache",
    "detect_mode",
    "steps_to_workflow_data",
    "detector_to_workflow_data",
    "Rect",
    "ElementMetadata",
    "scale_bounds",
    "clip_bounds_to_image",
    "validate_screen_coordinates",
    "transform_to_image_coordinates",
    "get_dpi_scale_factor",
    "normalize_windows_metadata",
    "normalize_macos_metadata",
    "get_confidence_score",
    "dict_to_element_metadata",
    "FallbackManager",
    "get_element_metadata_with_fallback",
    "FallbackConfig",
    "MetricsCollector",
]
