"""Claude Vision-based UI element identification.

Fallback for platforms where native accessibility APIs are unavailable.
Sends screenshots to Claude's vision model to identify interactive
elements with estimated bounding boxes and descriptions.
"""

import base64
import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

ELEMENT_ANALYSIS_PROMPT = (
    "Analyze this desktop application screenshot. "
    "Identify all clearly visible interactive UI elements "
    "(buttons, text inputs, links, menus, checkboxes, dropdowns). "
    "For each element, provide a JSON array of objects with:\n"
    '  "name": visible text or descriptive label,\n'
    '  "type": element type (button, input, link, menu, checkbox, dropdown, tab, icon),\n'
    '  "bounds": {"x": left, "y": top, "width": w, "height": h} in pixels,\n'
    '  "confidence": 0.0-1.0 how certain you are of the bounds\n'
    "Return ONLY the JSON array, no other text."
)

FOCUSED_ELEMENT_PROMPT = (
    "Analyze this desktop application screenshot. "
    "There was a user interaction near coordinates ({x}, {y}). "
    "Identify the specific UI element at or closest to that point. "
    "Return a single JSON object with:\n"
    '  "name": visible text or descriptive label,\n'
    '  "type": element type (button, input, link, menu, checkbox, dropdown, tab, icon),\n'
    '  "bounds": {{"x": left, "y": top, "width": w, "height": h}} in pixels,\n'
    '  "confidence": 0.0-1.0 how certain you are of the bounds\n'
    "Return ONLY the JSON object, no other text."
)


def analyze_screenshot(
    image_path: str | Path,
    click_coords: Optional[tuple[int, int]] = None,
    model: str = "claude-sonnet-4-20250514",
) -> Optional[list[dict]]:
    """Analyze a screenshot to identify interactive UI elements.

    Args:
        image_path: Path to the screenshot PNG file.
        click_coords: Optional (x, y) to focus analysis on a specific point.
        model: Claude model to use for analysis.

    Returns:
        List of element dicts with name, type, bounds, confidence.
        Returns None if analysis fails.
    """
    try:
        import anthropic
    except ImportError:
        logger.warning(
            "anthropic package not installed. Visual analysis unavailable. "
            "Install with: pip install anthropic"
        )
        return None

    image_path = Path(image_path)
    if not image_path.exists():
        logger.error("Screenshot not found: %s", image_path)
        return None

    image_data = base64.b64encode(image_path.read_bytes()).decode("utf-8")
    media_type = _get_media_type(image_path)

    if click_coords:
        prompt = FOCUSED_ELEMENT_PROMPT.format(x=click_coords[0], y=click_coords[1])
    else:
        prompt = ELEMENT_ANALYSIS_PROMPT

    try:
        client = anthropic.Anthropic()
        response = client.messages.create(
            model=model,
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )

        return _parse_response(response, focused=click_coords is not None)

    except Exception as e:
        logger.error("Claude Vision analysis failed: %s", e)
        return None


def analyze_capture_result(
    capture_result,
    click_coords: Optional[tuple[int, int]] = None,
    model: str = "claude-sonnet-4-20250514",
) -> Optional[list[dict]]:
    """Analyze a CaptureResult directly without saving to disk.

    Args:
        capture_result: A CaptureResult with image_bytes.
        click_coords: Optional (x, y) to focus analysis.
        model: Claude model to use.

    Returns:
        List of element dicts or None on failure.
    """
    try:
        import anthropic
    except ImportError:
        logger.warning(
            "anthropic package not installed. Visual analysis unavailable."
        )
        return None

    image_data = base64.b64encode(capture_result.image_bytes).decode("utf-8")

    if click_coords:
        prompt = FOCUSED_ELEMENT_PROMPT.format(x=click_coords[0], y=click_coords[1])
    else:
        prompt = ELEMENT_ANALYSIS_PROMPT

    try:
        client = anthropic.Anthropic()
        response = client.messages.create(
            model=model,
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_data,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )

        return _parse_response(response, focused=click_coords is not None)

    except Exception as e:
        logger.error("Claude Vision analysis failed: %s", e)
        return None


def _parse_response(response, focused: bool = False) -> Optional[list[dict]]:
    """Parse Claude's response into structured element data."""
    try:
        text = response.content[0].text.strip()

        # Strip markdown code fence if present
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1])

        parsed = json.loads(text)

        # Normalize to list
        if isinstance(parsed, dict):
            parsed = [parsed]

        # Validate and tag each element
        elements = []
        for elem in parsed:
            if not isinstance(elem, dict):
                continue
            if "bounds" not in elem:
                continue

            elements.append({
                "name": elem.get("name", "Unknown"),
                "type": elem.get("type", "unknown"),
                "bounds": elem["bounds"],
                "confidence": float(elem.get("confidence", 0.5)),
                "source": "visual",
            })

        return elements if elements else None

    except (json.JSONDecodeError, IndexError, KeyError) as e:
        logger.warning("Failed to parse vision response: %s", e)
        return None


def _get_media_type(path: Path) -> str:
    """Determine MIME type from file extension."""
    suffix = path.suffix.lower()
    types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    return types.get(suffix, "image/png")
