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

Adds visual annotations to screenshots.

```bash
python annotate_screenshot.py <input> <output> [options]
```

| Option | Format | Description |
|--------|--------|-------------|
| `--box` | `x,y,w,h` | Draw highlight box |
| `--arrow` | `x1,y1,x2,y2` | Draw arrow |
| `--callout` | `x,y,number` | Numbered callout |
| `--click` | `x,y[,type]` | Click indicator (single/double/right) |
| `--blur` | `x,y,w,h` | Blur region |
| `--style` | `path` | Custom style JSON |
| `--auto-blur` | - | Auto-detect sensitive fields |

## generate_markdown.py

Generates markdown from workflow data.

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

```bash
pip install pillow scikit-image jinja2 numpy
```
