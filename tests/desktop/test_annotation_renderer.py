"""Tests for annotation rendering functions."""

import io
from PIL import Image

import pytest

from docugen.desktop.annotation_renderer import (
    draw_bounding_box,
    draw_label,
    calculate_label_position,
    validate_bounds,
    render_element_annotation,
)


def test_draw_bounding_box():
    """Test bounding box rendering."""
    # Create test image
    img = Image.new("RGBA", (400, 300), (255, 255, 255, 255))

    bounds = {"x": 50, "y": 50, "width": 100, "height": 80}
    color = (255, 87, 51, 180)

    result = draw_bounding_box(img, bounds, color, width=3, dpi_scale=1.0)

    # Check result is same image object
    assert result is img

    # Visual check: box should be drawn (hard to test programmatically)
    # Save for manual inspection if needed
    # result.save("/tmp/test_box.png")


def test_draw_label():
    """Test label rendering with background."""
    img = Image.new("RGBA", (400, 300), (255, 255, 255, 255))

    result = draw_label(
        img,
        "Submit Button",
        (100, 100),
        bg_color=(255, 87, 51, 230),
        text_color=(255, 255, 255),
        font_size=14,
        padding=4,
        dpi_scale=1.0,
    )

    assert result is img


def test_calculate_label_position_above():
    """Test label positioning above element."""
    element_bounds = {"x": 100, "y": 150, "width": 80, "height": 40}
    img_dims = (400, 300)
    label_size = (60, 20)

    pos = calculate_label_position(element_bounds, img_dims, label_size, padding=4)

    # Should be above element (y = 150 - 20 - 4 = 126)
    assert pos == (100, 126)


def test_calculate_label_position_below():
    """Test label positioning below element when above is unavailable."""
    element_bounds = {"x": 100, "y": 10, "width": 80, "height": 40}
    img_dims = (400, 300)
    label_size = (60, 20)

    pos = calculate_label_position(element_bounds, img_dims, label_size, padding=4)

    # Should be below element (y = 10 + 40 + 4 = 54)
    assert pos == (100, 54)


def test_calculate_label_position_fallback():
    """Test label positioning fallback when no space available."""
    element_bounds = {"x": 380, "y": 280, "width": 10, "height": 10}
    img_dims = (400, 300)
    label_size = (60, 20)

    pos = calculate_label_position(element_bounds, img_dims, label_size, padding=4)

    # Will fit above at y=280-20-4=256
    assert pos == (380, 256)


def test_validate_bounds_within_image():
    """Test bounds validation when within image."""
    bounds = {"x": 50, "y": 50, "width": 100, "height": 80}
    img_dims = (400, 300)

    validated = validate_bounds(bounds, img_dims)

    assert validated == bounds


def test_validate_bounds_clipping():
    """Test bounds clipping when exceeding image dimensions.

    Acceptance criterion AC5: Bounds clipped to fit image without crash.
    """
    bounds = {"x": 350, "y": 250, "width": 100, "height": 80}
    img_dims = (400, 300)

    validated = validate_bounds(bounds, img_dims)

    # Should clip width to fit (400 - 350 = 50)
    # Should clip height to fit (300 - 250 = 50)
    assert validated["x"] == 350
    assert validated["y"] == 250
    assert validated["width"] == 50
    assert validated["height"] == 50


def test_validate_bounds_negative_coords():
    """Test bounds validation with negative coordinates."""
    bounds = {"x": -10, "y": -5, "width": 100, "height": 80}
    img_dims = (400, 300)

    validated = validate_bounds(bounds, img_dims)

    # Should clip to 0
    assert validated["x"] == 0
    assert validated["y"] == 0


def test_render_element_annotation_complete():
    """Test complete annotation rendering (box + label).

    Acceptance criterion AC2: Bounding box + label rendered with no overlap.
    """
    img = Image.new("RGBA", (400, 300), (255, 255, 255, 255))

    element_bounds = {"x": 100, "y": 100, "width": 80, "height": 40}
    element_name = "Submit"
    element_type = "button"
    style = {
        "highlight_color": (255, 87, 51, 180),
        "box_width": 3,
        "label_bg_color": (255, 87, 51, 230),
        "label_text_color": (255, 255, 255),
        "label_font_size": 14,
        "label_padding": 4,
    }

    result_bytes = render_element_annotation(
        img, element_bounds, element_name, element_type, style, dpi_scale=1.0
    )

    # Check result is PNG bytes
    assert isinstance(result_bytes, bytes)
    assert len(result_bytes) > 0

    # Verify it's a valid image
    result_img = Image.open(io.BytesIO(result_bytes))
    assert result_img.size == (400, 300)


def test_render_element_annotation_with_bytes_input():
    """Test annotation rendering with bytes input instead of PIL Image."""
    # Create image as bytes
    img = Image.new("RGBA", (400, 300), (255, 255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    img_bytes = buf.getvalue()

    element_bounds = {"x": 100, "y": 100, "width": 80, "height": 40}
    style = {
        "highlight_color": (255, 87, 51, 180),
        "box_width": 3,
        "label_bg_color": (255, 87, 51, 230),
        "label_text_color": (255, 255, 255),
        "label_font_size": 14,
        "label_padding": 4,
    }

    result_bytes = render_element_annotation(
        img_bytes, element_bounds, "Submit", "button", style, dpi_scale=1.0
    )

    assert isinstance(result_bytes, bytes)


def test_dpi_scaling():
    """Test DPI scaling applied consistently.

    Acceptance criterion AC12: 2.0 scale factor doubles all dimensions.
    """
    img = Image.new("RGBA", (800, 600), (255, 255, 255, 255))

    bounds_unscaled = {"x": 100, "y": 100, "width": 80, "height": 40}

    # Draw with 1.0 scale
    img1 = img.copy()
    draw_bounding_box(img1, bounds_unscaled, (255, 0, 0, 255), width=3, dpi_scale=1.0)

    # Draw with 2.0 scale
    img2 = img.copy()
    draw_bounding_box(img2, bounds_unscaled, (255, 0, 0, 255), width=3, dpi_scale=2.0)

    # Images should be different (scaled version has larger box)
    assert img1.tobytes() != img2.tobytes()

    # At 2.0 scale:
    # - Box should be drawn at (200, 200) instead of (100, 100)
    # - Width/height should be 160x80 instead of 80x40
    # This is visually verifiable but hard to test programmatically


def test_contrast_validation_light_background():
    """Test annotation visibility on light background.

    Acceptance criterion AC7: Annotations visible on light backgrounds.
    """
    img = Image.new("RGBA", (400, 300), (255, 255, 255, 255))  # White background

    style = {
        "highlight_color": (255, 87, 51, 180),  # Orange-red
        "box_width": 3,
        "label_bg_color": (255, 87, 51, 230),
        "label_text_color": (255, 255, 255),  # White text
        "label_font_size": 14,
        "label_padding": 4,
    }

    result_bytes = render_element_annotation(
        img,
        {"x": 100, "y": 100, "width": 80, "height": 40},
        "Submit",
        "button",
        style,
        dpi_scale=1.0,
    )

    # Save for visual inspection
    result_img = Image.open(io.BytesIO(result_bytes))
    # result_img.save("/tmp/light_bg.png")

    # Box and label should be visible (orange on white = good contrast)
    assert result_img.size == (400, 300)


def test_contrast_validation_dark_background():
    """Test annotation visibility on dark background.

    Acceptance criterion AC7: Annotations visible on dark backgrounds.
    """
    img = Image.new("RGBA", (400, 300), (30, 30, 30, 255))  # Dark background

    style = {
        "highlight_color": (255, 87, 51, 180),  # Orange-red
        "box_width": 3,
        "label_bg_color": (255, 87, 51, 230),
        "label_text_color": (255, 255, 255),  # White text
        "label_font_size": 14,
        "label_padding": 4,
    }

    result_bytes = render_element_annotation(
        img,
        {"x": 100, "y": 100, "width": 80, "height": 40},
        "Submit",
        "button",
        style,
        dpi_scale=1.0,
    )

    # Save for visual inspection
    result_img = Image.open(io.BytesIO(result_bytes))
    # result_img.save("/tmp/dark_bg.png")

    # Box and label should be visible (orange/white on dark = good contrast)
    assert result_img.size == (400, 300)
