---
title: Configuration
description: All configuration options for DocuGen
---

# Configuration Reference

## Environment variables

### SSIM_THRESHOLD

Controls step detection sensitivity.

```bash
export SSIM_THRESHOLD=0.90  # Default
export SSIM_THRESHOLD=0.85  # More sensitive
export SSIM_THRESHOLD=0.95  # Less sensitive
```

## Annotation styles

Create `annotation_styles.json`:

```json
{
  "highlight_color": [255, 87, 51, 180],
  "highlight_width": 3,
  "arrow_color": [255, 87, 51],
  "callout_bg_color": [255, 87, 51],
  "callout_text_color": [255, 255, 255],
  "callout_size": 24,
  "blur_strength": 15,
  "click_color": [255, 87, 51],
  "click_inner_radius": 8,
  "click_outer_radius": 20
}
```

## Sensitive field patterns

Auto-detected for blurring:

| Pattern | Matches |
|---------|---------|
| `password` | password, passwd, pwd, secret |
| `ssn` | ssn, social security, tax id |
| `credit_card` | credit card, card number, cvv |
| `api_key` | api key, access token, secret key |

## Built-in templates

| Template | Use case |
|----------|----------|
| `walkthrough` | Full step-by-step guide |
| `quick_reference` | Condensed checklist |
| `tutorial` | Learning-focused |

## File locations

Default installation:

```
~/.claude/skills/docugen/
├── SKILL.md
├── scripts/
├── references/
├── templates/
└── assets/
```
