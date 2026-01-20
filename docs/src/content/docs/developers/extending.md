---
title: Extending DocuGen
description: Add templates, scripts, and customizations
---

# Extending DocuGen

Customize DocuGen with new templates, annotation styles, and processing scripts.

## Custom templates

### Create a template

Templates use Jinja2 syntax. Create `templates/my-template.md`:

```jinja
---
title: {{ title }}
---

# {{ title }}

{{ description }}

## Quick Steps

{% for step in steps %}
{{ step.number }}. **{{ step.title }}**
   {{ step.description }}
{% endfor %}

## Screenshots

{% for step in steps %}
{% if step.screenshot %}
### {{ step.title }}
![{{ step.title }}]({{ step.screenshot }})
{% endif %}
{% endfor %}
```

### Available variables

| Variable | Type | Description |
|----------|------|-------------|
| `title` | string | Workflow title |
| `description` | string | Workflow description |
| `prerequisites` | list[string] | Requirements |
| `steps` | list[Step] | Step objects |
| `troubleshooting` | list[Issue] | Troubleshooting items |
| `generated_date` | string | YYYY-MM-DD |
| `generated_timestamp` | string | ISO format |

### Step object

```python
{
    "number": 1,
    "title": "Click Submit",
    "description": "Click the Submit button to save.",
    "screenshot": "images/step-01.png",
    "expected_result": "Form is submitted.",
    "action": "click"
}
```

### Custom filters

DocuGen provides these Jinja2 filters:

```jinja
{{ "My Title" | slugify }}
{# Output: my-title #}

{{ step.title | generate_image_filename(step.number) }}
{# Output: step-01-my-title.png #}

{{ step.title | generate_alt_text(step.number) }}
{# Output: Step 1: My Title #}
```

### Use your template

```bash
python generate_markdown.py data.json output.md \
  --template my-template \
  --template-dir ./templates \
  --jinja2
```

## Custom annotation styles

### Create style file

Create `my-styles.json`:

```json
{
  "highlight_color": [59, 130, 246, 200],
  "highlight_width": 4,
  "arrow_color": [59, 130, 246],
  "arrow_width": 4,
  "callout_bg_color": [59, 130, 246],
  "callout_text_color": [255, 255, 255],
  "callout_size": 28,
  "blur_strength": 20,
  "click_color": [59, 130, 246],
  "click_inner_radius": 10,
  "click_outer_radius": 25
}
```

### Apply styles

```bash
python annotate_screenshot.py input.png output.png \
  --style my-styles.json \
  --box 100,200,150,40
```

### Color schemes

Example schemes:

**Blue (professional)**
```json
{
  "highlight_color": [59, 130, 246, 180],
  "arrow_color": [59, 130, 246],
  "callout_bg_color": [59, 130, 246]
}
```

**Green (success-focused)**
```json
{
  "highlight_color": [34, 197, 94, 180],
  "arrow_color": [34, 197, 94],
  "callout_bg_color": [34, 197, 94]
}
```

**Purple (creative)**
```json
{
  "highlight_color": [168, 85, 247, 180],
  "arrow_color": [168, 85, 247],
  "callout_bg_color": [168, 85, 247]
}
```

## Custom sensitive patterns

### Extend detection

Edit `annotate_screenshot.py`:

```python
SENSITIVE_PATTERNS = {
    # Existing patterns...
    'password': re.compile(r'password|passwd|pwd|secret', re.IGNORECASE),

    # Add custom patterns
    'employee_id': re.compile(r'employee.?id|emp.?num', re.IGNORECASE),
    'internal_code': re.compile(r'internal|confidential', re.IGNORECASE),
}
```

### Per-project patterns

Pass via elements JSON:

```json
{
  "elements": [
    {
      "selector": "input#secret-field",
      "inputType": "password",
      "boundingBox": {"x": 100, "y": 200, "width": 200, "height": 40}
    }
  ],
  "custom_blur_patterns": [
    {"selector": ".internal-data", "reason": "confidential"}
  ]
}
```

## Custom processing scripts

### Add a post-processor

Create `scripts/add_watermark.py`:

```python
#!/usr/bin/env python3
"""Add watermark to processed images."""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import argparse

def add_watermark(image_path: Path, text: str, output_path: Path):
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    # Position in bottom-right
    font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    x = img.width - bbox[2] - 10
    y = img.height - bbox[3] - 10

    draw.text((x, y), text, fill=(128, 128, 128), font=font)
    img.save(output_path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', type=Path)
    parser.add_argument('--text', default='DocuGen')
    args = parser.parse_args()

    for img_path in args.input_dir.glob('*.png'):
        add_watermark(img_path, args.text, img_path)
        print(f"Watermarked: {img_path}")

if __name__ == '__main__':
    main()
```

### Integrate with workflow

Update SKILL.md Phase 3:

```markdown
### Phase 3: Processing
1. Run `detect_step.py` to finalize step boundaries
2. Run `annotate_screenshot.py` to add visual annotations
3. Run `process_images.py` to optimize file sizes
4. Run `add_watermark.py` to add branding  # New step
```

## Custom troubleshooting patterns

### Add workflow-specific patterns

Edit `references/troubleshooting_patterns.md`:

```markdown
### 9. API Rate Limiting

**Template:**
```markdown
**"Too many requests" or "Rate limit exceeded"**
You've made too many API calls in a short period. Wait a few minutes
and try again, or contact support to increase your rate limit.
```

**Variations:**
- 429 error codes
- "Slow down" messages
- Temporary blocks
```

### Map patterns to workflows

The skill uses these mappings:

| UI Pattern | Troubleshooting |
|------------|-----------------|
| `input[type="password"]` | Authentication issues |
| `form[method="post"]` | Form submission issues |
| `input[type="file"]` | File upload issues |

Add custom mappings in SKILL.md's troubleshooting section.

## Packaging extensions

### Create an extension package

Structure:

```
my-docugen-extension/
├── templates/
│   └── my-template.md
├── styles/
│   └── my-styles.json
├── scripts/
│   └── my-processor.py
├── install.sh
└── README.md
```

### Install script

```bash
#!/bin/bash
DOCUGEN_PATH="${HOME}/.claude/skills/docugen"

# Copy templates
cp templates/* "${DOCUGEN_PATH}/templates/"

# Copy styles
cp styles/* "${DOCUGEN_PATH}/assets/"

# Copy scripts
cp scripts/* "${DOCUGEN_PATH}/scripts/"

echo "Extension installed!"
```

## Testing extensions

### Test templates

```bash
# Create sample data
cat > test-data.json << 'EOF'
{
  "title": "Test Workflow",
  "description": "Testing custom template",
  "steps": [
    {"number": 1, "title": "Step One", "description": "Do something"}
  ]
}
EOF

# Generate with custom template
python generate_markdown.py test-data.json output.md \
  --template my-template \
  --jinja2

# Check output
cat output.md
```

### Test annotation styles

```bash
# Create test image (solid color)
python -c "
from PIL import Image
img = Image.new('RGB', (400, 300), 'white')
img.save('test-input.png')
"

# Apply annotations
python annotate_screenshot.py test-input.png test-output.png \
  --style my-styles.json \
  --box 50,50,100,50 \
  --callout 40,40,1

# View result
open test-output.png  # macOS
xdg-open test-output.png  # Linux
```
