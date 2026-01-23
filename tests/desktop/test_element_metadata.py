"""Comprehensive test suite for element_metadata, coordinate_transforms, and metadata_normalization."""

import pytest
from docugen.desktop.element_metadata import Rect, ElementMetadata
from docugen.desktop.coordinate_transforms import (
    scale_bounds,
    clip_bounds_to_image,
    validate_screen_coordinates,
    transform_to_image_coordinates,
    get_dpi_scale_factor,
)
from docugen.desktop.metadata_normalization import (
    normalize_windows_metadata,
    normalize_macos_metadata,
    get_confidence_score,
    dict_to_element_metadata,
    WINDOWS_CONTROL_TYPE_MAP,
    MACOS_AX_ROLE_MAP,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def sample_rect():
    """Sample Rect for testing."""
    return Rect(x=100, y=200, width=150, height=50)


@pytest.fixture
def sample_windows_metadata():
    """Sample Windows UI Automation output."""
    return {
        "control_type": "Button",
        "name": "Submit",
        "automation_id": "submitBtn",
        "class_name": "Button",
        "bounding_rectangle": {"x": 100, "y": 200, "width": 150, "height": 50},
        "query_latency_ms": 45.2,
        "fallback_used": False,
        "properties": {"IsEnabled": True},
    }


@pytest.fixture
def sample_macos_metadata():
    """Sample macOS Accessibility API output."""
    return {
        "AXRole": "AXButton",
        "AXTitle": "Submit",
        "AXIdentifier": "submitBtn",
        "AXPosition": {"x": 100, "y": 200},
        "AXSize": {"width": 150, "height": 50},
        "query_latency_ms": 45.2,
        "permission_status": "granted",
        "fallback_used": False,
        "properties": {"AXFocused": False},
    }


# ============================================================================
# Rect Dataclass Tests
# ============================================================================


def test_rect_creation(sample_rect):
    """Test Rect creation and field access."""
    assert sample_rect.x == 100
    assert sample_rect.y == 200
    assert sample_rect.width == 150
    assert sample_rect.height == 50


def test_rect_equality():
    """Test Rect equality comparison."""
    rect1 = Rect(100, 200, 150, 50)
    rect2 = Rect(100, 200, 150, 50)
    rect3 = Rect(101, 200, 150, 50)

    assert rect1 == rect2
    assert rect1 != rect3


def test_rect_validation_negative_width():
    """Test Rect validation raises ValueError for negative width."""
    rect = Rect(100, 200, -10, 50)
    with pytest.raises(ValueError, match="width must be > 0"):
        rect.validate()


def test_rect_validation_negative_height():
    """Test Rect validation raises ValueError for negative height."""
    rect = Rect(100, 200, 150, -5)
    with pytest.raises(ValueError, match="height must be > 0"):
        rect.validate()


def test_rect_validation_zero_width():
    """Test Rect validation raises ValueError for zero width."""
    rect = Rect(100, 200, 0, 50)
    with pytest.raises(ValueError, match="width must be > 0"):
        rect.validate()


def test_rect_to_dict(sample_rect):
    """Test Rect.to_dict() serialization."""
    data = sample_rect.to_dict()
    assert data == {"x": 100, "y": 200, "width": 150, "height": 50}


def test_rect_from_dict():
    """Test Rect.from_dict() deserialization."""
    data = {"x": 100, "y": 200, "width": 150, "height": 50}
    rect = Rect.from_dict(data)
    assert rect.x == 100
    assert rect.y == 200
    assert rect.width == 150
    assert rect.height == 50


# ============================================================================
# ElementMetadata Dataclass Tests
# ============================================================================


def test_element_metadata_creation_windows():
    """Test ElementMetadata creation for Windows."""
    metadata = ElementMetadata(
        element_id="win_btn_1",
        name="Submit",
        role="button",
        bounds=Rect(100, 200, 150, 50),
        confidence_score=1.0,
        platform="windows",
        windows_automation_id="submitBtn",
        windows_class_name="Button",
        properties={"IsEnabled": True},
        query_latency_ms=45.2,
        fallback_used=False,
    )

    assert metadata.element_id == "win_btn_1"
    assert metadata.name == "Submit"
    assert metadata.role == "button"
    assert metadata.platform == "windows"
    assert metadata.windows_automation_id == "submitBtn"
    assert metadata.macos_ax_identifier is None


def test_element_metadata_creation_macos():
    """Test ElementMetadata creation for macOS."""
    metadata = ElementMetadata(
        element_id="mac_btn_1",
        name="Submit",
        role="button",
        bounds=Rect(100, 200, 150, 50),
        confidence_score=0.9,
        platform="macos",
        macos_ax_identifier="submitBtn",
        macos_ax_role="AXButton",
        properties={"AXFocused": False},
        query_latency_ms=120.5,
        permission_status="granted",
        fallback_used=False,
    )

    assert metadata.element_id == "mac_btn_1"
    assert metadata.platform == "macos"
    assert metadata.macos_ax_identifier == "submitBtn"
    assert metadata.windows_automation_id is None


def test_element_metadata_validation_invalid_platform():
    """Test ElementMetadata validation raises ValueError for invalid platform."""
    metadata = ElementMetadata(
        element_id="test",
        name="Test",
        role="button",
        bounds=Rect(100, 200, 150, 50),
        confidence_score=1.0,
        platform="linux",  # type: ignore
    )

    with pytest.raises(ValueError, match="Platform must be 'windows' or 'macos'"):
        metadata.validate()


def test_element_metadata_validation_negative_confidence():
    """Test ElementMetadata validation raises ValueError for negative confidence."""
    metadata = ElementMetadata(
        element_id="test",
        name="Test",
        role="button",
        bounds=Rect(100, 200, 150, 50),
        confidence_score=-0.5,
        platform="windows",
    )

    with pytest.raises(ValueError, match="Confidence score must be in"):
        metadata.validate()


def test_element_metadata_validation_confidence_gt_one():
    """Test ElementMetadata validation raises ValueError for confidence > 1.0."""
    metadata = ElementMetadata(
        element_id="test",
        name="Test",
        role="button",
        bounds=Rect(100, 200, 150, 50),
        confidence_score=1.5,
        platform="windows",
    )

    with pytest.raises(ValueError, match="Confidence score must be in"):
        metadata.validate()


def test_element_metadata_validation_invalid_bounds():
    """Test ElementMetadata validation raises TypeError for non-Rect bounds."""
    metadata = ElementMetadata(
        element_id="test",
        name="Test",
        role="button",
        bounds=None,  # type: ignore
        confidence_score=1.0,
        platform="windows",
    )

    with pytest.raises(TypeError, match="Bounds must be a Rect instance"):
        metadata.validate()


def test_element_metadata_serialization():
    """Test ElementMetadata to_dict() → from_dict() round-trip."""
    original = ElementMetadata(
        element_id="test_1",
        name="Submit",
        role="button",
        bounds=Rect(100, 200, 150, 50),
        confidence_score=0.95,
        platform="windows",
        windows_automation_id="submitBtn",
        windows_class_name="Button",
        properties={"IsEnabled": True, "IsKeyboardFocusable": True},
        query_latency_ms=45.2,
        fallback_used=False,
    )

    # Serialize
    data = original.to_dict()
    assert isinstance(data, dict)
    assert data["element_id"] == "test_1"
    assert data["bounds"] == {"x": 100, "y": 200, "width": 150, "height": 50}

    # Deserialize
    reconstructed = ElementMetadata.from_dict(data)
    assert reconstructed == original


# ============================================================================
# Coordinate Transform Tests
# ============================================================================


@pytest.mark.parametrize(
    "dpi_scale,expected_x,expected_y,expected_width,expected_height",
    [
        (1.0, 100, 200, 150, 50),  # No scaling
        (1.25, 125, 250, 188, 62),  # 125% scaling
        (1.5, 150, 300, 225, 75),  # 150% scaling
        (2.0, 200, 400, 300, 100),  # 200% scaling (Retina)
    ],
)
def test_scale_bounds(
    sample_rect, dpi_scale, expected_x, expected_y, expected_width, expected_height
):
    """Test scale_bounds with various DPI scales."""
    scaled = scale_bounds(sample_rect, dpi_scale)
    assert scaled.x == expected_x
    assert scaled.y == expected_y
    assert scaled.width == expected_width
    assert scaled.height == expected_height


def test_clip_bounds_to_image_within_bounds():
    """Test clip_bounds_to_image with bounds fully inside image."""
    bounds = Rect(100, 200, 150, 50)
    clipped = clip_bounds_to_image(bounds, image_width=1920, image_height=1080)

    assert clipped.x == 100
    assert clipped.y == 200
    assert clipped.width == 150
    assert clipped.height == 50


def test_clip_bounds_to_image_exceeds_right_edge():
    """Test clip_bounds_to_image with bounds exceeding right edge."""
    bounds = Rect(1800, 900, 300, 100)  # Extends past x=1920
    clipped = clip_bounds_to_image(bounds, image_width=1920, image_height=1080)

    assert clipped.x == 1800
    assert clipped.y == 900
    assert clipped.width == 120  # Clipped to 1920 - 1800
    assert clipped.height == 100


def test_clip_bounds_to_image_exceeds_bottom_edge():
    """Test clip_bounds_to_image with bounds exceeding bottom edge."""
    bounds = Rect(100, 1000, 150, 200)  # Extends past y=1080
    clipped = clip_bounds_to_image(bounds, image_width=1920, image_height=1080)

    assert clipped.x == 100
    assert clipped.y == 1000
    assert clipped.width == 150
    assert clipped.height == 80  # Clipped to 1080 - 1000


def test_clip_bounds_to_image_exceeds_both_edges():
    """Test clip_bounds_to_image with bounds exceeding both right and bottom."""
    bounds = Rect(1850, 1050, 200, 100)
    clipped = clip_bounds_to_image(bounds, image_width=1920, image_height=1080)

    assert clipped.x == 1850
    assert clipped.y == 1050
    assert clipped.width == 70  # 1920 - 1850
    assert clipped.height == 30  # 1080 - 1050


def test_clip_bounds_to_image_negative_x():
    """Test clip_bounds_to_image with negative x (off-screen left)."""
    bounds = Rect(-50, 100, 200, 100)
    clipped = clip_bounds_to_image(bounds, image_width=1920, image_height=1080)

    assert clipped.x == 0
    assert clipped.y == 100
    assert clipped.width == 150  # 200 - 50 (clipped from left)
    assert clipped.height == 100


def test_clip_bounds_to_image_negative_y():
    """Test clip_bounds_to_image with negative y (off-screen top)."""
    bounds = Rect(100, -100, 150, 200)
    clipped = clip_bounds_to_image(bounds, image_width=1920, image_height=1080)

    assert clipped.x == 100
    assert clipped.y == 0
    assert clipped.width == 150
    assert clipped.height == 100  # 200 - 100 (clipped from top)


def test_clip_bounds_to_image_completely_offscreen():
    """Test clip_bounds_to_image with bounds completely off-screen."""
    bounds = Rect(2000, 1200, 100, 100)  # Completely outside 1920x1080
    clipped = clip_bounds_to_image(bounds, image_width=1920, image_height=1080)

    # Should return minimal valid Rect (clamped to image edges)
    assert clipped.x == 1920
    assert clipped.y == 1080
    assert clipped.width == 1  # Minimum width
    assert clipped.height == 1  # Minimum height


def test_validate_screen_coordinates_primary_monitor():
    """Test validate_screen_coordinates for coordinates on primary monitor."""
    assert validate_screen_coordinates(100, 200, 1920, 1080) is True
    assert validate_screen_coordinates(0, 0, 1920, 1080) is True
    assert validate_screen_coordinates(1919, 1079, 1920, 1080) is True


def test_validate_screen_coordinates_secondary_monitor_negative_x():
    """Test validate_screen_coordinates for secondary monitor with negative x."""
    # Secondary monitor positioned to the left (-1920 to 0)
    assert validate_screen_coordinates(-1920, 100, 1920, 1080) is True
    assert validate_screen_coordinates(-100, 500, 1920, 1080) is True


def test_validate_screen_coordinates_secondary_monitor_negative_y():
    """Test validate_screen_coordinates for secondary monitor with negative y."""
    # Secondary monitor positioned above (y can be negative)
    assert validate_screen_coordinates(100, -1080, 1920, 1080) is True
    assert validate_screen_coordinates(500, -100, 1920, 1080) is True


def test_validate_screen_coordinates_far_outside():
    """Test validate_screen_coordinates rejects coordinates far outside reasonable bounds."""
    assert validate_screen_coordinates(50000, 100, 1920, 1080) is False
    assert validate_screen_coordinates(100, 50000, 1920, 1080) is False
    assert validate_screen_coordinates(-50000, 100, 1920, 1080) is False


def test_transform_to_image_coordinates_no_scaling():
    """Test transform_to_image_coordinates with DPI 1.0 and no offset."""
    image_x, image_y = transform_to_image_coordinates(
        screen_x=100,
        screen_y=200,
        dpi_scale=1.0,
        image_width=1920,
        image_height=1080,
        screen_offset_x=0,
        screen_offset_y=0,
    )

    assert image_x == 100
    assert image_y == 200


def test_transform_to_image_coordinates_with_scaling():
    """Test transform_to_image_coordinates with DPI 1.5."""
    image_x, image_y = transform_to_image_coordinates(
        screen_x=100,
        screen_y=200,
        dpi_scale=1.5,
        image_width=1920,
        image_height=1080,
        screen_offset_x=0,
        screen_offset_y=0,
    )

    assert image_x == 150  # 100 * 1.5
    assert image_y == 300  # 200 * 1.5


def test_transform_to_image_coordinates_with_offset():
    """Test transform_to_image_coordinates with screen offset (region capture)."""
    # Secondary monitor at x=1920, capture from x=1920
    image_x, image_y = transform_to_image_coordinates(
        screen_x=1920,
        screen_y=100,
        dpi_scale=1.0,
        image_width=1920,
        image_height=1080,
        screen_offset_x=1920,
        screen_offset_y=0,
    )

    assert image_x == 0  # 1920 - 1920
    assert image_y == 100


def test_transform_to_image_coordinates_clamping():
    """Test transform_to_image_coordinates clamps to image dimensions."""
    # Coordinates that would exceed image bounds
    image_x, image_y = transform_to_image_coordinates(
        screen_x=5000,
        screen_y=5000,
        dpi_scale=1.0,
        image_width=1920,
        image_height=1080,
        screen_offset_x=0,
        screen_offset_y=0,
    )

    assert image_x == 1920  # Clamped to image_width
    assert image_y == 1080  # Clamped to image_height


def test_get_dpi_scale_factor():
    """Test get_dpi_scale_factor returns valid scale."""
    scale = get_dpi_scale_factor()

    # Should return a positive number (1.0, 1.25, 1.5, 2.0, etc.)
    assert scale > 0
    assert isinstance(scale, float)


# ============================================================================
# Metadata Normalization Tests
# ============================================================================


def test_normalize_windows_metadata(sample_windows_metadata):
    """Test normalize_windows_metadata converts Windows output correctly."""
    metadata = normalize_windows_metadata(sample_windows_metadata)

    assert metadata.platform == "windows"
    assert metadata.role == "button"
    assert metadata.name == "Submit"
    assert metadata.windows_automation_id == "submitBtn"
    assert metadata.windows_class_name == "Button"
    assert metadata.bounds.x == 100
    assert metadata.bounds.y == 200
    assert metadata.bounds.width == 150
    assert metadata.bounds.height == 50
    assert metadata.confidence_score == 1.0
    assert metadata.fallback_used is False


def test_normalize_macos_metadata(sample_macos_metadata):
    """Test normalize_macos_metadata converts macOS output correctly."""
    metadata = normalize_macos_metadata(sample_macos_metadata)

    assert metadata.platform == "macos"
    assert metadata.role == "button"
    assert metadata.name == "Submit"
    assert metadata.macos_ax_identifier == "submitBtn"
    assert metadata.macos_ax_role == "AXButton"
    assert metadata.bounds.x == 100
    assert metadata.bounds.y == 200
    assert metadata.bounds.width == 150
    assert metadata.bounds.height == 50
    assert metadata.confidence_score == 1.0
    assert metadata.permission_status == "granted"


def test_normalize_windows_metadata_unknown_control_type():
    """Test normalize_windows_metadata handles unknown control types."""
    ui_output = {
        "control_type": "CustomWidget",  # Not in mapping
        "name": "Custom",
        "bounding_rectangle": {"x": 0, "y": 0, "width": 100, "height": 100},
    }

    metadata = normalize_windows_metadata(ui_output)
    assert metadata.role == "unknown"


def test_normalize_macos_metadata_unknown_ax_role():
    """Test normalize_macos_metadata handles unknown AX roles."""
    ax_output = {
        "AXRole": "AXCustomElement",  # Not in mapping
        "AXTitle": "Custom",
        "AXPosition": {"x": 0, "y": 0},
        "AXSize": {"width": 100, "height": 100},
    }

    metadata = normalize_macos_metadata(ax_output)
    assert metadata.role == "unknown"


def test_control_type_mapping_coverage_windows():
    """Test Windows control type mapping has 14+ entries."""
    # AC4: Must have 14+ Windows types
    assert len(WINDOWS_CONTROL_TYPE_MAP) >= 14

    # Verify common types are present
    common_types = [
        "Button",
        "Edit",
        "Text",
        "Window",
        "Image",
        "CheckBox",
        "RadioButton",
        "ComboBox",
        "ListItem",
        "MenuItem",
        "TabItem",
        "Hyperlink",
        "Pane",
        "Document",
    ]
    for control_type in common_types:
        assert control_type in WINDOWS_CONTROL_TYPE_MAP


def test_control_type_mapping_coverage_macos():
    """Test macOS AX role mapping has 12+ entries."""
    # AC4: Must have 12+ macOS types
    assert len(MACOS_AX_ROLE_MAP) >= 12

    # Verify common types are present
    common_types = [
        "AXButton",
        "AXTextField",
        "AXStaticText",
        "AXWindow",
        "AXImage",
        "AXCheckBox",
        "AXRadioButton",
        "AXPopUpButton",
        "AXRow",
        "AXMenuItem",
        "AXTabGroup",
        "AXLink",
    ]
    for ax_role in common_types:
        assert ax_role in MACOS_AX_ROLE_MAP


@pytest.mark.parametrize(
    "control_type,expected_role",
    [
        ("Button", "button"),
        ("Edit", "text_field"),
        ("CheckBox", "checkbox"),
        ("ListItem", "list_item"),
        ("ProgressBar", "progress_bar"),
    ],
)
def test_windows_control_type_normalization(control_type, expected_role):
    """Test specific Windows control type → normalized role mappings."""
    ui_output = {
        "control_type": control_type,
        "name": "Test",
        "bounding_rectangle": {"x": 0, "y": 0, "width": 100, "height": 100},
    }

    metadata = normalize_windows_metadata(ui_output)
    assert metadata.role == expected_role


@pytest.mark.parametrize(
    "ax_role,expected_role",
    [
        ("AXButton", "button"),
        ("AXTextField", "text_field"),
        ("AXCheckBox", "checkbox"),
        ("AXRow", "list_item"),
        ("AXProgressIndicator", "progress_bar"),
    ],
)
def test_macos_ax_role_normalization(ax_role, expected_role):
    """Test specific macOS AX role → normalized role mappings."""
    ax_output = {
        "AXRole": ax_role,
        "AXTitle": "Test",
        "AXPosition": {"x": 0, "y": 0},
        "AXSize": {"width": 100, "height": 100},
    }

    metadata = normalize_macos_metadata(ax_output)
    assert metadata.role == expected_role


def test_get_confidence_score_baseline():
    """Test get_confidence_score baseline (no penalties) = 1.0."""
    score = get_confidence_score()
    assert score == 1.0


def test_get_confidence_score_high_latency():
    """Test get_confidence_score with high latency (>1000ms) → -0.1."""
    score = get_confidence_score(query_latency_ms=1500)
    assert score == pytest.approx(0.9)


def test_get_confidence_score_fallback():
    """Test get_confidence_score with fallback → -0.2."""
    score = get_confidence_score(fallback_used=True)
    assert score == pytest.approx(0.8)


def test_get_confidence_score_permission_denied():
    """Test get_confidence_score with permission denied → -0.3."""
    score = get_confidence_score(permission_status="denied")
    assert score == pytest.approx(0.7)


def test_get_confidence_score_combined_penalties():
    """Test get_confidence_score with all penalties → 0.4."""
    score = get_confidence_score(
        query_latency_ms=1500, fallback_used=True, permission_status="denied"
    )
    assert score == pytest.approx(0.4)


def test_get_confidence_score_clamping():
    """Test get_confidence_score clamps to minimum 0.0."""
    # Simulate extreme penalties that would go negative
    score = get_confidence_score(
        query_latency_ms=5000,  # Multiple penalties
        fallback_used=True,
        permission_status="denied",
    )
    assert score >= 0.0


def test_dict_to_element_metadata_legacy_format():
    """Test dict_to_element_metadata converts legacy dict format."""
    legacy = {
        "name": "Submit",
        "type": "button",
        "bounds": {"x": 100, "y": 200, "width": 150, "height": 50},
        "confidence": 0.95,
        "source": "visual",
    }

    metadata = dict_to_element_metadata(legacy)

    assert metadata.name == "Submit"
    assert metadata.role == "button"
    assert metadata.bounds.x == 100
    assert metadata.confidence_score == 0.95
    assert metadata.fallback_used is True  # source == "visual"


# ============================================================================
# Multi-Monitor and Edge Case Tests
# ============================================================================


def test_multi_monitor_negative_coordinates():
    """Test coordinate validation and clipping with multi-monitor negative coords."""
    # Secondary monitor at x=-1920
    assert validate_screen_coordinates(-1920, 100, 1920, 1080) is True

    # Bounds from secondary monitor (negative x)
    bounds = Rect(-1920, 100, 300, 200)
    # When converting to image space, negative coords should be clamped to 0
    clipped = clip_bounds_to_image(bounds, image_width=1920, image_height=1080)

    assert clipped.x == 0  # Clamped from -1920
    assert clipped.width == 1  # Minimal width (entire bounds was off-screen)


def test_serialization_round_trip_preserves_data():
    """Test ElementMetadata serialization → deserialization preserves all data."""
    original = ElementMetadata(
        element_id="test_123",
        name="Test Element",
        role="text_field",
        bounds=Rect(50, 100, 200, 30),
        confidence_score=0.85,
        platform="macos",
        macos_ax_identifier="testField",
        macos_ax_role="AXTextField",
        properties={"AXFocused": True, "AXValue": "test"},
        query_latency_ms=75.3,
        permission_status="granted",
        fallback_used=False,
    )

    # Serialize to dict
    data = original.to_dict()

    # Verify dict structure
    assert isinstance(data["bounds"], dict)
    assert data["bounds"]["x"] == 50

    # Deserialize
    reconstructed = ElementMetadata.from_dict(data)

    # Verify all fields match
    assert reconstructed.element_id == original.element_id
    assert reconstructed.name == original.name
    assert reconstructed.role == original.role
    assert reconstructed.bounds == original.bounds
    assert reconstructed.confidence_score == original.confidence_score
    assert reconstructed.platform == original.platform
    assert reconstructed.macos_ax_identifier == original.macos_ax_identifier
    assert reconstructed.properties == original.properties

    # Test equality
    assert reconstructed == original
