---
title: Python Scripts
description: CLI reference for DocuGen's Python scripts
---

# Python Scripts Reference

DocuGen includes four Python scripts for processing workflows.

## detect_step.py

Compares screenshots using SSIM to detect step boundaries.

```bash
python detect_step.py <before> <after> [--threshold 0.90] [--json]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--threshold` | `0.90` | SSIM threshold (lower = more sensitive) |
| `--json` | - | Output result as JSON |

**Exit codes:** 0 = significant change, 1 = no change, 2 = error

## annotate_screenshot.py

Adds visual annotations to screenshots. Features **smart auto-annotation** that requires no manual configuration.

```bash
python annotate_screenshot.py <input> <output> [options]
```

### Smart Mode (Default)

Smart mode is **enabled by default** when you provide element metadata. Just pass the elements file:

```bash
# Smart annotation is automatic with --elements
python annotate_screenshot.py screenshot.png annotated.png \
  --elements elements.json --step 1

# Disable smart mode if needed
python annotate_screenshot.py screenshot.png annotated.png \
  --elements elements.json --no-smart --box 100,200,150,40
```

Smart mode automatically:
- Detects the target element from metadata
- Draws highlight box around target
- Adds numbered callout in optimal position
- Draws arrow for small/hard-to-find elements
- Adds click indicator for clickable elements
- Auto-blurs sensitive fields (passwords, SSNs, etc.)

### Options

| Option | Format | Description |
|--------|--------|-------------|
| `--smart` | - | Smart auto-annotation (default: enabled with --elements) |
| `--no-smart` | - | Disable smart annotation, use manual mode |
| `--step` | `number` | Step number for smart callout (default: 1) |
| `--elements` | `path` | Element metadata JSON (from Playwright) |
| `--box` | `x,y,w,h` | Draw highlight box |
| `--arrow` | `x1,y1,x2,y2` | Draw arrow |
| `--callout` | `x,y,number` | Numbered callout |
| `--click` | `x,y[,type]` | Click indicator (single/double/right) |
| `--blur` | `x,y,w,h` | Blur region |
| `--style` | `path` | Custom style JSON |
| `--auto-blur` | - | Auto-detect sensitive fields |

### Element Metadata Format

The `--elements` JSON should contain element data captured by Playwright:

```json
{
  "elements": [
    {
      "isTarget": true,
      "tagName": "button",
      "text": "Submit",
      "boundingBox": {"x": 100, "y": 200, "width": 80, "height": 32},
      "role": "button"
    }
  ]
}
```

Target element detection priority:
1. Element marked `isTarget: true` or `focused: true`
2. Element with `action`, `clicked`, or `typed` properties
3. Highest z-index element
4. First interactive element (button, input, link)
5. First element with bounding box

## generate_markdown.py

Generates markdown from workflow data, with optional PDF export.

```bash
python generate_markdown.py <input.json> <output.md> [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--template` | `walkthrough` | Template name |
| `--jinja2` | - | Use Jinja2 templating |
| `--embed-images` | - | Base64 embed images |
| `--no-toc` | - | Disable table of contents |
| `--zip` | - | Create zip package |
| `--pdf` | - | Generate PDF in addition to markdown (default: enabled) |
| `--no-pdf` | - | Disable PDF generation |
| `--pdf-only` | - | Generate only PDF (no markdown) |
| `--pdf-css` | - | Custom CSS file for PDF styling |

### PDF Generation

PDF generation is **enabled by default**. Generate professional PDF documentation for importing into document management systems:

```bash
# Generate both markdown and PDF (default)
python generate_markdown.py workflow.json output.md

# Disable PDF, generate markdown only
python generate_markdown.py workflow.json output.md --no-pdf

# Generate PDF only (no markdown)
python generate_markdown.py workflow.json output.md --pdf-only

# Use custom styling
python generate_markdown.py workflow.json output.md --pdf-css custom.css
```

Requires additional dependencies:
```bash
pip install markdown weasyprint
```

On macOS, you may need: `brew install pango`
On Ubuntu: `sudo apt install libpango-1.0-0 libpangocairo-1.0-0`

## process_images.py

Optimizes screenshot images.

```bash
python process_images.py <input_dir> [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--output-dir` | Same as input | Output directory |
| `--max-width` | `1200` | Maximum width (px) |
| `--max-size` | `200` | Maximum size (KB) |
| `--format` | `png` | Output format |
| `--combine` | - | Combine similar (SSIM threshold) |

## Dependencies

**Core dependencies:**
```bash
pip install pillow scikit-image jinja2 numpy
```

**PDF generation (optional):**
```bash
pip install markdown weasyprint
```

The installer handles dependencies automatically:
```bash
# Install with core dependencies
curl -fsSL https://raw.githubusercontent.com/asachs01/claudeDocugen/main/install.sh | bash

# Install with PDF support
curl -fsSL https://raw.githubusercontent.com/asachs01/claudeDocugen/main/install.sh | bash -s -- --pdf
```
