---
title: Using Templates
description: Customize documentation output with templates
---

# Using Templates

DocuGen uses Jinja2 templates to generate documentation. Choose built-in templates or create your own.

## Built-in templates

### Walkthrough (default)

Full step-by-step guide with:
- Overview section
- Prerequisites list
- Numbered steps with screenshots
- Expected results
- Troubleshooting section

```
Generate documentation using walkthrough template
```

### Quick Reference

Condensed checklist format:
- Numbered steps only
- No screenshots
- Minimal explanation

```
Generate documentation using quick_reference template
```

### Tutorial

Learning-focused format:
- Learning objectives
- Conceptual introduction
- Practice exercises
- Summary

```
Generate documentation using tutorial template
```

## Using templates via CLI

```bash
python generate_markdown.py workflow.json output.md --template walkthrough
```

### With Jinja2 rendering

```bash
python generate_markdown.py workflow.json output.md \
  --template walkthrough \
  --jinja2 \
  --template-dir ./templates
```

## Template variables

Templates receive this data:

```python
{
    "title": "Workflow Title",
    "description": "Brief description",
    "prerequisites": ["Requirement 1", "Requirement 2"],
    "steps": [
        {
            "number": 1,
            "title": "Step Title",
            "description": "What this step does",
            "screenshot": "images/step-01.png",
            "expected_result": "What user should see",
            "action": "click"  # For alt text
        }
    ],
    "troubleshooting": [
        {
            "issue": "Problem title",
            "description": "What went wrong",
            "resolution": "How to fix"
        }
    ],
    "generated_date": "2026-01-20",
    "generated_timestamp": "2026-01-20T12:00:00"
}
```

## Creating custom templates

### 1. Create template file

Save as `templates/my-template.md`:

```jinja
# {{ title }}

{{ description }}

## Before you begin

{% for prereq in prerequisites %}
- {{ prereq }}
{% endfor %}

## Instructions

{% for step in steps %}
### {{ step.number }}. {{ step.title }}

{{ step.description }}

{% if step.screenshot %}
![{{ step.title }}]({{ step.screenshot }})
{% endif %}

{% endfor %}

---
*Generated {{ generated_date }}*
```

### 2. Use custom template

```bash
python generate_markdown.py workflow.json output.md \
  --template my-template \
  --template-dir ./templates \
  --jinja2
```

## Template filters

DocuGen provides custom Jinja2 filters:

### slugify

Convert text to URL-friendly format:

```jinja
{{ "Click Submit Button" | slugify }}
{# Output: click-submit-button #}
```

### generate_image_filename

Create consistent filenames:

```jinja
{{ step.title | generate_image_filename(step.number) }}
{# Output: step-01-enter-repository-name.png #}
```

### generate_alt_text

Create accessible alt text:

```jinja
{{ step.title | generate_alt_text(step.number) }}
{# Output: Step 1: Enter repository name #}
```

## Output options

### Embed images as Base64

Create self-contained markdown:

```bash
python generate_markdown.py workflow.json output.md --embed-images
```

### Generate table of contents

Automatic for 5+ steps, or force:

```bash
python generate_markdown.py workflow.json output.md
# TOC auto-generated if 5+ steps
```

Disable TOC:

```bash
python generate_markdown.py workflow.json output.md --no-toc
```

### Create zip package

Bundle markdown and images:

```bash
python generate_markdown.py workflow.json output.md --zip
```

Creates: `output_documentation.zip`

## Template best practices

### 1. Include WCAG-compliant alt text

```jinja
![Step {{ step.number }}: {{ step.title }}]({{ step.screenshot }})
```

### 2. Use semantic HTML when needed

```jinja
<details>
<summary>Show advanced options</summary>

{{ advanced_content }}

</details>
```

### 3. Handle missing data gracefully

```jinja
{% if step.expected_result %}
**Expected:** {{ step.expected_result }}
{% endif %}
```

### 4. Keep templates focused

Create separate templates for different use cases rather than one complex template with many conditionals.
