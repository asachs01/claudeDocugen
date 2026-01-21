---
title: Screenshot Annotation
description: Customize how screenshots are annotated
---

# Screenshot Annotation

DocuGen automatically annotates screenshots with highlights, arrows, and callouts.

## Smart Auto-Annotation (Recommended)

**Zero configuration required!** Smart mode automatically detects what to annotate:

```bash
python annotate_screenshot.py screenshot.png annotated.png \
  --smart --elements elements.json --step 1
```

Smart mode handles everything:
- Detects the target element from Playwright metadata
- Draws highlight box around target
- Adds numbered callout in optimal position
- Draws arrow for small elements
- Adds click indicator for buttons/links
- Auto-blurs sensitive fields (passwords, SSNs, API keys)

DocuGen passes element metadata automatically during workflow recording - you don't need to do anything special.

## Default annotations

### Highlight boxes

Orange-red boxes (#FF5733) surround the target element:

- 3px solid border
- 4px padding around element
- Semi-transparent fill (70% opacity)

### Numbered callouts

Circular badges indicate step order:

- 24px diameter
- White text on orange background
- Positioned near (not overlapping) element

### Click indicators

Ripple-style markers show click locations:

- Inner filled circle (8px radius)
- Outer ring (20px radius)
- Supports single, double, and right-click styles

## Using annotate_screenshot.py

### Basic usage

```bash
python annotate_screenshot.py input.png output.png --box 100,200,150,40
```

### Add multiple annotations

```bash
python annotate_screenshot.py input.png output.png \
  --box 100,200,150,40 \
  --callout 90,180,1 \
  --click 175,220
```

### Options

| Option | Format | Description |
|--------|--------|-------------|
| `--box` | x,y,w,h | Highlight box at coordinates |
| `--arrow` | x1,y1,x2,y2 | Arrow from start to end |
| `--callout` | x,y,number | Numbered callout |
| `--click` | x,y[,type] | Click indicator (single/double/right) |
| `--blur` | x,y,w,h | Blur sensitive region |
| `--style` | path | Custom style JSON file |

## Custom styles

Create `annotation_styles.json`:

```json
{
  "highlight_color": [59, 130, 246, 180],
  "highlight_width": 4,
  "arrow_color": [59, 130, 246],
  "arrow_width": 3,
  "callout_bg_color": [59, 130, 246],
  "callout_text_color": [255, 255, 255],
  "callout_size": 28,
  "click_color": [59, 130, 246],
  "click_inner_radius": 10,
  "click_outer_radius": 24,
  "blur_strength": 20
}
```

Apply with:

```bash
python annotate_screenshot.py input.png output.png \
  --style annotation_styles.json \
  --box 100,200,150,40
```

## Auto-blur sensitive data

DocuGen automatically detects and blurs:

- Password fields (`type="password"`)
- Fields labeled: SSN, Credit Card, API Key
- Email addresses in forms

### Enable auto-blur

```bash
python annotate_screenshot.py input.png output.png \
  --elements elements.json \
  --auto-blur
```

### Elements JSON format

```json
{
  "elements": [
    {
      "selector": "input#password",
      "inputType": "password",
      "boundingBox": {"x": 100, "y": 200, "width": 200, "height": 40}
    }
  ]
}
```

### Manual blur

Override or add additional blur regions:

```bash
python annotate_screenshot.py input.png output.png \
  --blur 100,200,200,40
```

## Annotation layering

Annotations are drawn in this order (bottom to top):

1. Blur regions
2. Highlight boxes
3. Arrows
4. Numbered callouts
5. Click indicators

This ensures callouts appear above other elements.

## Color guidelines

### Primary color (default)

Orange-red (#FF5733) provides high contrast against most backgrounds.

### Alternative colors

| Color | Hex | Use case |
|-------|-----|----------|
| Blue | #3498DB | Secondary highlights |
| Green | #2ECC71 | Success states |
| Yellow | #F1C40F | Warnings |

### Contrast testing

If annotations don't stand out:

1. Try alternative colors
2. Add a slight drop shadow
3. Use thicker borders

## Image optimization

### Compression

```bash
python process_images.py ./images --max-size 200
```

Target: <200KB per image.

### Cropping

Focus on the relevant area:

```bash
python process_images.py ./images \
  --elements elements.json \
  --crop-padding 50
```

### Combining similar screenshots

Merge screenshots with minimal differences:

```bash
python process_images.py ./images --combine 0.95
```
