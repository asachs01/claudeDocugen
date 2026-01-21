#!/usr/bin/env python3
"""
annotate_screenshot.py - PIL-based screenshot annotation for DocuGen

This script adds visual annotations to screenshots including:
- Highlight boxes around target elements
- Numbered step callouts
- Arrows pointing to elements
- Auto-blur for sensitive data

Usage:
    python annotate_screenshot.py <input_image> <output_image> --box x,y,w,h [options]

Options:
    --box x,y,w,h          Draw highlight box at coordinates
    --arrow x1,y1,x2,y2    Draw arrow from (x1,y1) to (x2,y2)
    --callout x,y,number   Add numbered callout at position
    --click x,y[,type]     Draw click indicator (type: single/double/right)
    --blur x,y,w,h         Blur region (for sensitive data)
    --style <style_file>   Load custom styles from JSON
    --elements <json>      Element metadata for auto-blur detection
    --auto-blur            Auto-detect and blur sensitive fields
    --smart                Smart auto-annotation (no config required!)
    --step <n>             Step number for smart annotation callout

Dependencies:
    - PIL/Pillow
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Tuple, List, Optional, Dict, Any

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False


# Default annotation styles
DEFAULT_STYLES = {
    'highlight_color': (255, 87, 51, 180),      # Orange-red with alpha
    'highlight_width': 3,
    'arrow_color': (255, 87, 51),               # Orange-red
    'arrow_width': 3,
    'callout_bg_color': (255, 87, 51),          # Orange-red
    'callout_text_color': (255, 255, 255),      # White
    'callout_size': 24,
    'blur_strength': 15,
    # Click indicator styles (like Scribe/CleanShot)
    'click_color': (255, 87, 51),               # Orange-red
    'click_inner_radius': 8,                     # Inner circle radius
    'click_outer_radius': 20,                    # Outer ripple radius
    'click_ring_width': 2,                       # Ring stroke width
    'click_opacity': 200,                        # 0-255
}

# Patterns for detecting sensitive fields (FR-2.5)
SENSITIVE_PATTERNS = {
    'password': re.compile(r'password|passwd|pwd|secret', re.IGNORECASE),
    'ssn': re.compile(r'ssn|social.?security|tax.?id', re.IGNORECASE),
    'credit_card': re.compile(r'credit.?card|card.?number|cvv|cvc|expir', re.IGNORECASE),
    'api_key': re.compile(r'api.?key|access.?token|secret.?key|auth.?token', re.IGNORECASE),
    'email': re.compile(r'email|e-mail', re.IGNORECASE),
    'phone': re.compile(r'phone|tel|mobile', re.IGNORECASE),
}


def detect_sensitive_fields(elements: List[Dict[str, Any]]) -> List[Tuple[int, int, int, int]]:
    """
    Detect sensitive fields from element metadata and return their bounding boxes.

    Args:
        elements: List of element metadata dicts with keys:
            - selector: CSS selector
            - text: Visible text
            - ariaLabel: ARIA label
            - inputType: Input type attribute (e.g., 'password')
            - boundingBox: {x, y, width, height}

    Returns:
        List of (x, y, width, height) tuples for regions to blur
    """
    blur_regions = []

    for elem in elements:
        is_sensitive = False

        # Check input type
        input_type = elem.get('inputType', '').lower()
        if input_type in ('password', 'hidden'):
            is_sensitive = True

        # Check selector, text, and aria label against patterns
        check_fields = [
            elem.get('selector', ''),
            elem.get('text', ''),
            elem.get('ariaLabel', ''),
            elem.get('placeholder', ''),
            elem.get('name', ''),
            elem.get('id', ''),
        ]

        for field in check_fields:
            if not field:
                continue
            for pattern_name, pattern in SENSITIVE_PATTERNS.items():
                if pattern.search(field):
                    is_sensitive = True
                    break

        if is_sensitive and 'boundingBox' in elem:
            bbox = elem['boundingBox']
            blur_regions.append((
                int(bbox.get('x', 0)),
                int(bbox.get('y', 0)),
                int(bbox.get('width', 0)),
                int(bbox.get('height', 0))
            ))

    return blur_regions


def load_styles(style_path: Optional[Path]) -> dict:
    """Load annotation styles from JSON file or use defaults."""
    styles = DEFAULT_STYLES.copy()
    if style_path and style_path.exists():
        with open(style_path) as f:
            custom = json.load(f)
            styles.update(custom)
    return styles


def draw_highlight_box(
    draw: ImageDraw.Draw,
    coords: Tuple[int, int, int, int],
    styles: dict
) -> None:
    """
    Draw a highlight box around a region.

    Args:
        draw: PIL ImageDraw object
        coords: (x, y, width, height) of the region
        styles: Style configuration dict
    """
    x, y, w, h = coords
    color = styles['highlight_color'][:3]  # RGB only for rectangle
    width = styles['highlight_width']

    # Draw rectangle outline
    draw.rectangle(
        [x, y, x + w, y + h],
        outline=color,
        width=width
    )


def draw_arrow(
    draw: ImageDraw.Draw,
    start: Tuple[int, int],
    end: Tuple[int, int],
    styles: dict
) -> None:
    """
    Draw an arrow from start to end point.

    Args:
        draw: PIL ImageDraw object
        start: (x, y) start position
        end: (x, y) end position (arrow head)
        styles: Style configuration dict
    """
    import math

    color = styles['arrow_color']
    width = styles['arrow_width']

    # Draw main line
    draw.line([start, end], fill=color, width=width)

    # Draw arrow head
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    arrow_length = 15
    arrow_angle = math.pi / 6  # 30 degrees

    left_x = end[0] - arrow_length * math.cos(angle - arrow_angle)
    left_y = end[1] - arrow_length * math.sin(angle - arrow_angle)
    right_x = end[0] - arrow_length * math.cos(angle + arrow_angle)
    right_y = end[1] - arrow_length * math.sin(angle + arrow_angle)

    draw.polygon(
        [end, (left_x, left_y), (right_x, right_y)],
        fill=color
    )


def draw_callout(
    img: Image.Image,
    draw: ImageDraw.Draw,
    position: Tuple[int, int],
    number: int,
    styles: dict
) -> None:
    """
    Draw a numbered callout circle.

    Args:
        img: PIL Image object
        draw: PIL ImageDraw object
        position: (x, y) center position
        number: Step number to display
        styles: Style configuration dict
    """
    x, y = position
    size = styles['callout_size']
    radius = size // 2

    # Draw circle background
    draw.ellipse(
        [x - radius, y - radius, x + radius, y + radius],
        fill=styles['callout_bg_color']
    )

    # Draw number text
    text = str(number)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size - 8)
    except OSError:
        font = ImageFont.load_default()

    # Center text in circle
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x = x - text_w // 2
    text_y = y - text_h // 2 - 2

    draw.text((text_x, text_y), text, fill=styles['callout_text_color'], font=font)


def blur_region(
    img: Image.Image,
    coords: Tuple[int, int, int, int],
    styles: dict
) -> Image.Image:
    """
    Apply blur to a region of the image (for sensitive data).

    Args:
        img: PIL Image object
        coords: (x, y, width, height) of region to blur
        styles: Style configuration dict

    Returns:
        Modified image with blurred region
    """
    x, y, w, h = coords
    region = img.crop((x, y, x + w, y + h))
    blurred = region.filter(ImageFilter.GaussianBlur(styles['blur_strength']))
    img.paste(blurred, (x, y))
    return img


def draw_click_indicator(
    img: Image.Image,
    draw: ImageDraw.Draw,
    position: Tuple[int, int],
    styles: dict,
    click_type: str = 'single'
) -> None:
    """
    Draw a click indicator (ripple effect) at the specified position.
    Similar to Scribe/CleanShot click visualization.

    Args:
        img: PIL Image object
        draw: PIL ImageDraw object
        position: (x, y) center of click
        styles: Style configuration dict
        click_type: 'single', 'double', or 'right' for different styles
    """
    x, y = position
    color = styles.get('click_color', (255, 87, 51))
    inner_r = styles.get('click_inner_radius', 8)
    outer_r = styles.get('click_outer_radius', 20)
    ring_width = styles.get('click_ring_width', 2)
    opacity = styles.get('click_opacity', 200)

    # Create color with opacity
    if len(color) == 3:
        fill_color = (*color, opacity)
        ring_color = (*color, opacity // 2)
    else:
        fill_color = color
        ring_color = (*color[:3], color[3] // 2)

    # Draw outer ring (ripple effect)
    draw.ellipse(
        [x - outer_r, y - outer_r, x + outer_r, y + outer_r],
        outline=ring_color[:3],
        width=ring_width
    )

    # Draw middle ring for double-click
    if click_type == 'double':
        mid_r = (inner_r + outer_r) // 2
        draw.ellipse(
            [x - mid_r, y - mid_r, x + mid_r, y + mid_r],
            outline=ring_color[:3],
            width=ring_width
        )

    # Draw inner filled circle
    draw.ellipse(
        [x - inner_r, y - inner_r, x + inner_r, y + inner_r],
        fill=fill_color[:3]
    )

    # For right-click, add a small "R" indicator
    if click_type == 'right':
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
        except OSError:
            font = ImageFont.load_default()
        draw.text((x + inner_r + 2, y - 6), "R", fill=color[:3], font=font)


def smart_annotate(
    img: Image.Image,
    draw: ImageDraw.Draw,
    elements: List[Dict[str, Any]],
    step_number: int,
    styles: dict
) -> Image.Image:
    """
    Smart auto-annotation: automatically detect what to highlight and annotate.
    Requires NO manual configuration - just pass element metadata from Playwright.

    Smart detection logic:
    1. Find the "target" element (highest z-index, focused, or has action)
    2. Draw highlight box around target
    3. Add callout with step number
    4. Auto-blur any sensitive fields
    5. Optionally add arrow for small/hard-to-find elements

    Args:
        img: PIL Image object
        draw: PIL ImageDraw object
        elements: Element metadata from Playwright capture
        step_number: Step number for callout
        styles: Style configuration

    Returns:
        Modified image with smart annotations
    """
    if not elements:
        return img

    # Find the target element (the one being interacted with)
    target = find_target_element(elements)
    if not target or 'boundingBox' not in target:
        return img

    bbox = target['boundingBox']
    x = int(bbox.get('x', 0))
    y = int(bbox.get('y', 0))
    w = int(bbox.get('width', 0))
    h = int(bbox.get('height', 0))

    # Skip if element is too small to be meaningful
    if w < 5 or h < 5:
        return img

    # Auto-blur sensitive fields first
    blur_regions = detect_sensitive_fields(elements)
    for coords in blur_regions:
        img = blur_region(img, coords, styles)
        draw = ImageDraw.Draw(img)

    # Draw highlight box around target element
    draw_highlight_box(draw, (x, y, w, h), styles)

    # Determine optimal callout position
    img_width, img_height = img.size
    callout_pos = calculate_callout_position(x, y, w, h, img_width, img_height, styles)

    # Draw callout
    draw_callout(img, draw, callout_pos, step_number, styles)

    # Draw arrow from callout to element for small elements
    if w < 100 or h < 30:
        # Point arrow to center of element
        element_center = (x + w // 2, y + h // 2)
        draw_arrow(draw, callout_pos, element_center, styles)

    # Add click indicator if this is a clickable element
    if is_clickable_element(target):
        click_pos = (x + w // 2, y + h // 2)
        draw_click_indicator(img, draw, click_pos, styles, 'single')

    return img


def find_target_element(elements: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Identify the target element from a list of captured elements.

    Priority order:
    1. Element marked as 'target' or 'focused'
    2. Element with an action (clicked, typed, etc.)
    3. Element with highest z-index
    4. First interactive element (button, input, link)
    5. First element with bounding box

    Args:
        elements: List of element metadata

    Returns:
        Target element dict or None
    """
    # Look for explicitly marked target
    for elem in elements:
        if elem.get('isTarget') or elem.get('focused'):
            return elem

    # Look for element with action
    for elem in elements:
        if elem.get('action') or elem.get('clicked') or elem.get('typed'):
            return elem

    # Sort by z-index if available
    with_zindex = [e for e in elements if 'zIndex' in e]
    if with_zindex:
        return max(with_zindex, key=lambda e: int(e.get('zIndex', 0)))

    # Look for interactive elements
    interactive_tags = {'button', 'input', 'a', 'select', 'textarea'}
    interactive_roles = {'button', 'link', 'textbox', 'checkbox', 'radio', 'combobox'}

    for elem in elements:
        tag = elem.get('tagName', '').lower()
        role = elem.get('role', '').lower()
        if tag in interactive_tags or role in interactive_roles:
            return elem

    # Fall back to first element with bounding box
    for elem in elements:
        if 'boundingBox' in elem:
            return elem

    return None


def calculate_callout_position(
    x: int, y: int, w: int, h: int,
    img_width: int, img_height: int,
    styles: dict
) -> Tuple[int, int]:
    """
    Calculate optimal callout position relative to target element.
    Avoids placing callout outside image bounds or overlapping the element.

    Args:
        x, y, w, h: Element bounding box
        img_width, img_height: Image dimensions
        styles: Style config (for callout size)

    Returns:
        (x, y) position for callout center
    """
    callout_radius = styles.get('callout_size', 24) // 2
    padding = 10

    # Preferred position: top-left of element, offset outward
    callout_x = x - callout_radius - padding
    callout_y = y - callout_radius - padding

    # Adjust if too close to left edge
    if callout_x < callout_radius + padding:
        # Place to the right of element instead
        callout_x = x + w + callout_radius + padding

    # Adjust if too close to top
    if callout_y < callout_radius + padding:
        # Place below instead
        callout_y = y + h + callout_radius + padding

    # Adjust if off right edge
    if callout_x > img_width - callout_radius - padding:
        callout_x = x - callout_radius - padding

    # Adjust if off bottom
    if callout_y > img_height - callout_radius - padding:
        callout_y = y - callout_radius - padding

    # Final bounds check
    callout_x = max(callout_radius + 5, min(img_width - callout_radius - 5, callout_x))
    callout_y = max(callout_radius + 5, min(img_height - callout_radius - 5, callout_y))

    return (callout_x, callout_y)


def is_clickable_element(element: Dict[str, Any]) -> bool:
    """
    Determine if an element is clickable based on its metadata.

    Args:
        element: Element metadata dict

    Returns:
        True if element appears to be clickable
    """
    # Check for click action
    if element.get('clicked') or element.get('action') == 'click':
        return True

    # Check tag name
    clickable_tags = {'button', 'a', 'input', 'select'}
    tag = element.get('tagName', '').lower()
    if tag in clickable_tags:
        return True

    # Check role
    clickable_roles = {'button', 'link', 'checkbox', 'radio', 'menuitem', 'tab'}
    role = element.get('role', '').lower()
    if role in clickable_roles:
        return True

    # Check for onclick attribute
    if element.get('onclick') or element.get('hasClickHandler'):
        return True

    return False


def parse_coords(coord_str: str) -> Tuple[int, ...]:
    """Parse comma-separated coordinates string."""
    return tuple(int(x.strip()) for x in coord_str.split(','))


def main():
    parser = argparse.ArgumentParser(
        description='Add annotations to screenshots'
    )
    parser.add_argument('input', type=Path, help='Input image path')
    parser.add_argument('output', type=Path, help='Output image path')
    parser.add_argument('--box', action='append', help='Highlight box: x,y,w,h')
    parser.add_argument('--arrow', action='append', help='Arrow: x1,y1,x2,y2')
    parser.add_argument('--callout', action='append', help='Callout: x,y,number')
    parser.add_argument('--blur', action='append', help='Blur region: x,y,w,h')
    parser.add_argument(
        '--click',
        action='append',
        help='Click indicator: x,y[,type] where type is single/double/right (default: single)'
    )
    parser.add_argument('--style', type=Path, help='Custom style JSON file')
    parser.add_argument(
        '--elements',
        type=Path,
        help='JSON file with element metadata for auto-blur detection (FR-2.5)'
    )
    parser.add_argument(
        '--auto-blur',
        action='store_true',
        help='Auto-detect and blur sensitive fields (requires --elements)'
    )
    parser.add_argument(
        '--smart',
        action='store_true',
        default=True,
        help='Smart auto-annotation: automatically detect target element, add highlight, callout, and blur sensitive data (default: enabled when --elements provided)'
    )
    parser.add_argument(
        '--no-smart',
        action='store_true',
        help='Disable smart annotation, use manual coordinates only'
    )
    parser.add_argument(
        '--step',
        type=int,
        default=1,
        help='Step number for smart annotation callout (default: 1)'
    )

    args = parser.parse_args()

    if not DEPS_AVAILABLE:
        print("Error: PIL/Pillow not installed.", file=sys.stderr)
        print("Run: pip install pillow", file=sys.stderr)
        sys.exit(2)

    if not args.input.exists():
        print(f"Error: Input image not found: {args.input}", file=sys.stderr)
        sys.exit(2)

    styles = load_styles(args.style)
    img = Image.open(args.input).convert('RGBA')
    draw = ImageDraw.Draw(img)

    # Smart annotation mode - automatic everything (default when --elements provided)
    use_smart = args.smart and args.elements and not args.no_smart
    if use_smart:
        if not args.elements.exists():
            print(f"Error: Elements file not found: {args.elements}", file=sys.stderr)
            sys.exit(2)

        with open(args.elements) as f:
            elements_data = json.load(f)
            if isinstance(elements_data, list):
                elements = elements_data
            else:
                elements = elements_data.get('elements', [])

        img = smart_annotate(img, draw, elements, args.step, styles)

        # Save and exit - smart mode handles everything
        args.output.parent.mkdir(parents=True, exist_ok=True)
        img = img.convert('RGB')
        img.save(args.output, optimize=True)
        print(f"Smart annotated image saved: {args.output}")
        return

    # Auto-detect sensitive fields if requested (FR-2.5)
    auto_blur_regions = []
    if args.auto_blur and args.elements:
        if args.elements.exists():
            with open(args.elements) as f:
                elements_data = json.load(f)
                # Handle both list of elements or dict with 'elements' key
                if isinstance(elements_data, list):
                    elements = elements_data
                else:
                    elements = elements_data.get('elements', [])
                auto_blur_regions = detect_sensitive_fields(elements)
                print(f"Auto-detected {len(auto_blur_regions)} sensitive field(s) to blur")
        else:
            print(f"Warning: Elements file not found: {args.elements}", file=sys.stderr)

    # Apply auto-detected blur regions
    for coords in auto_blur_regions:
        img = blur_region(img, coords, styles)
        draw = ImageDraw.Draw(img)

    # Apply manual blur regions (before other annotations)
    if args.blur:
        for blur_spec in args.blur:
            coords = parse_coords(blur_spec)
            img = blur_region(img, coords, styles)
            draw = ImageDraw.Draw(img)  # Recreate draw after modification

    # Draw highlight boxes
    if args.box:
        for box_spec in args.box:
            coords = parse_coords(box_spec)
            draw_highlight_box(draw, coords, styles)

    # Draw arrows
    if args.arrow:
        for arrow_spec in args.arrow:
            coords = parse_coords(arrow_spec)
            start = (coords[0], coords[1])
            end = (coords[2], coords[3])
            draw_arrow(draw, start, end, styles)

    # Draw callouts
    if args.callout:
        for callout_spec in args.callout:
            parts = callout_spec.split(',')
            x, y = int(parts[0]), int(parts[1])
            number = int(parts[2])
            draw_callout(img, draw, (x, y), number, styles)

    # Draw click indicators (like Scribe/CleanShot)
    if args.click:
        for click_spec in args.click:
            parts = click_spec.split(',')
            x, y = int(parts[0]), int(parts[1])
            click_type = parts[2] if len(parts) > 2 else 'single'
            draw_click_indicator(img, draw, (x, y), styles, click_type)

    # Save output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    img = img.convert('RGB')  # Convert back to RGB for PNG/JPG
    img.save(args.output, optimize=True)
    print(f"Annotated image saved: {args.output}")


if __name__ == '__main__':
    main()
