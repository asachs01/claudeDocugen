---
title: Architecture
description: How DocuGen works internally
---

# Architecture

Understanding DocuGen's internal architecture.

## System overview

```
┌─────────────────────────────────────────────────────────┐
│                      Claude                              │
│  ┌─────────────────────────────────────────────────┐   │
│  │               SKILL.md                           │   │
│  │  • Trigger detection                            │   │
│  │  • Workflow orchestration                       │   │
│  │  • Semantic analysis                            │   │
│  │  • Context generation                           │   │
│  └─────────────────────────────────────────────────┘   │
│                          │                              │
│                          ▼                              │
│  ┌─────────────────────────────────────────────────┐   │
│  │           Playwright MCP                         │   │
│  │  • Browser control                              │   │
│  │  • Screenshot capture                           │   │
│  │  • DOM inspection                               │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  Python Scripts                          │
│                                                          │
│  detect_step.py ──► annotate_screenshot.py              │
│        │                    │                            │
│        ▼                    ▼                            │
│  process_images.py ◄── generate_markdown.py             │
│                                                          │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                     Output                               │
│                                                          │
│  documentation.md + images/ + (optional) .zip           │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Component responsibilities

### SKILL.md

The brain of DocuGen — orchestrates the entire process:

- **Trigger detection**: Recognizes natural language commands
- **Phase management**: Coordinates the 5-phase workflow
- **Semantic analysis**: Generates contextual descriptions
- **Reference loading**: Progressive disclosure of style guides

### Playwright MCP

Browser automation interface:

- **Navigation**: Go to URLs, click, type
- **Screenshot capture**: Before/after each action
- **DOM inspection**: Element metadata, selectors, ARIA labels
- **Event tracking**: MutationObserver for dynamic content

### Python scripts

Processing pipeline:

| Script | Input | Output | Purpose |
|--------|-------|--------|---------|
| `detect_step.py` | 2 images | SSIM score | Determine if action is significant |
| `annotate_screenshot.py` | Image + coords | Annotated image | Add visual markers |
| `process_images.py` | Image directory | Optimized images | Compress, crop, combine |
| `generate_markdown.py` | JSON data | Markdown file | Render final documentation |

## Data flow

### Phase 1: Initiation

```
User input: "Document this workflow: Create repo"
                    │
                    ▼
           ┌───────────────┐
           │   SKILL.md    │
           │ Parse trigger │
           └───────────────┘
                    │
                    ▼
           ┌───────────────┐
           │ Playwright MCP│
           │ browser_launch│
           └───────────────┘
                    │
                    ▼
           Browser opened at URL
```

### Phase 2: Recording

```
User: "Click New Project"
           │
           ▼
    ┌──────────────┐
    │ Screenshot   │──► step-01-before.png
    │ (before)     │
    └──────────────┘
           │
           ▼
    ┌──────────────┐
    │ Get element  │──► {selector, text, boundingBox}
    │ metadata     │
    └──────────────┘
           │
           ▼
    ┌──────────────┐
    │ Execute      │──► browser_click
    │ action       │
    └──────────────┘
           │
           ▼
    ┌──────────────┐
    │ Screenshot   │──► step-01-after.png
    │ (after)      │
    └──────────────┘
           │
           ▼
    ┌──────────────┐
    │ detect_step  │──► SSIM: 0.72 (significant)
    │              │
    └──────────────┘
           │
           ▼
    Record step in session.json
```

### Phase 3: Processing

```
session.json
     │
     ▼
┌─────────────────┐
│ annotate_       │
│ screenshot.py   │──► Add boxes, callouts
└─────────────────┘
     │
     ▼
┌─────────────────┐
│ process_        │
│ images.py       │──► Optimize, crop
└─────────────────┘
     │
     ▼
optimized images/
```

### Phase 4: Generation

```
session.json + writing_style_guide.md
                    │
                    ▼
           ┌───────────────┐
           │   SKILL.md    │
           │ Semantic      │──► Contextual descriptions
           │ analysis      │──► Prerequisites
           └───────────────┘──► Expected results
                    │
                    ▼
           ┌───────────────┐
           │ generate_     │
           │ markdown.py   │──► documentation.md
           └───────────────┘
```

## Key algorithms

### SSIM step detection

Structural Similarity Index compares images:

```python
def compare_images(before, after):
    # Convert to grayscale
    before_gray = to_grayscale(before)
    after_gray = to_grayscale(after)

    # Calculate SSIM
    score = ssim(before_gray, after_gray)

    # Score < 0.90 = significant change
    return score < SSIM_THRESHOLD
```

### Sensitive field detection

Pattern matching on element metadata:

```python
PATTERNS = {
    'password': r'password|passwd|pwd|secret',
    'ssn': r'ssn|social.?security|tax.?id',
    # ...
}

def is_sensitive(element):
    for field in [element.selector, element.text, element.ariaLabel]:
        for pattern in PATTERNS.values():
            if re.search(pattern, field, re.IGNORECASE):
                return True
    return element.inputType == 'password'
```

### Contextual description generation

Claude analyzes:

1. **Workflow goal**: User's stated objective
2. **Element semantics**: Button text, ARIA labels
3. **Step position**: Is this login? Configuration? Final submit?
4. **Visual context**: What changed on screen

Output structure:

```json
{
  "context": "Why this step matters",
  "description": "Imperative action instruction",
  "expected": "What user should observe"
}
```

## Extension points

### Custom templates

Add Jinja2 templates to `templates/`:

```jinja
# {{ title }}

{% for step in steps %}
{{ step.number }}. {{ step.title }}
{% endfor %}
```

### Custom annotation styles

Modify `assets/annotation_styles.json`:

```json
{
  "highlight_color": [0, 120, 255, 180]
}
```

### Additional patterns

Extend `SENSITIVE_PATTERNS` in `annotate_screenshot.py`.

## Performance considerations

### Screenshot capture

- Target: <200ms per capture
- Use native viewport resolution
- Avoid full-page captures unless needed

### Image processing

- Compress to <200KB per image
- Crop to relevant region when possible
- Combine similar screenshots (SSIM > 0.95)

### Session data

- Store JSON incrementally during recording
- Load references only when needed (progressive disclosure)
