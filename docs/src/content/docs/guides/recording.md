---
title: Recording Workflows
description: Master the workflow recording process
---

# Recording Workflows

Learn how to capture workflows effectively for high-quality documentation.

## Starting a recording

### Basic syntax

```
Document this workflow: [description]
Starting URL: [url]
```

### With options

```
Document this workflow: Configure project settings
Starting URL: https://app.example.com/settings
Audience: intermediate
Template: walkthrough
Output: ./docs/settings-guide.md
```

## Recording actions

### Click actions

```
Click the "Settings" button in the sidebar
```

DocuGen captures:
- Element selector
- Button text and ARIA label
- Bounding box for annotation
- Before/after screenshots

### Text input

```
Enter "project-name" in the name field
```

For sensitive fields (passwords), DocuGen automatically blurs the input.

### Selections

```
Select "Admin" from the role dropdown
```

### Navigation

```
Navigate to the Users tab
```

## Step detection

DocuGen uses SSIM (Structural Similarity Index) to detect meaningful changes:

| SSIM Score | Interpretation |
|------------|----------------|
| > 0.95 | No significant change (hover, focus) |
| 0.90 - 0.95 | Minor change (dropdown open) |
| < 0.90 | Significant change (new step) |

### Adjusting sensitivity

Set the threshold via environment variable:

```bash
export SSIM_THRESHOLD=0.85  # More sensitive
export SSIM_THRESHOLD=0.95  # Less sensitive
```

## Multi-action steps

When multiple actions result in minimal visual change, DocuGen can combine them:

```
Fill out the form: name="John", email="john@example.com"
```

This creates a single step with multiple instructions rather than separate steps.

## Handling dynamic content

### Wait for content

```
Wait for the loading spinner to disappear
```

### Wait for specific element

```
Wait for the success message to appear
```

### Handle modals

```
Click "Confirm" in the confirmation dialog
```

## Best practices

### 1. Describe intent, not mechanics

**Good:**
```
Create a new project with name "Demo"
```

**Less helpful:**
```
Click the blue button at coordinates 150,200
```

### 2. One action per instruction

**Good:**
```
Click Settings
```
```
Select the Privacy tab
```

**Avoid:**
```
Click Settings and go to Privacy and enable two-factor auth
```

### 3. Be specific about elements

**Good:**
```
Click the "Save" button in the form footer
```

**Ambiguous:**
```
Click Save
```

### 4. Mention expected results

```
Click Submit — the form should close and show a success message
```

## Ending a recording

### Generate immediately

```
End recording and generate documentation
```

### Save session for later

```
End recording and save session to ./sessions/settings-workflow.json
```

### Generate with specific options

```
End recording and generate:
- Template: quick_reference
- Audience: expert
- Output: ./docs/settings-quick-ref.md
```

## Troubleshooting recordings

### Screenshots not capturing

Ensure Playwright MCP has browser permissions:

```
Check Playwright MCP status
```

### SSIM not detecting changes

Lower the threshold:

```bash
export SSIM_THRESHOLD=0.80
```

### Element not found

Provide more context:

```
Click the Submit button — it's the blue button at the bottom of the form
```
