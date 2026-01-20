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
    --blur x,y,w,h         Blur region (for sensitive data)
    --style <style_file>   Load custom styles from JSON

Dependencies:
    - PIL/Pillow
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Tuple, List, Optional

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
    'blur_strength': 15
}


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
    parser.add_argument('--style', type=Path, help='Custom style JSON file')

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

    # Apply blur regions first (before other annotations)
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

    # Save output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    img = img.convert('RGB')  # Convert back to RGB for PNG/JPG
    img.save(args.output, optimize=True)
    print(f"Annotated image saved: {args.output}")


if __name__ == '__main__':
    main()
