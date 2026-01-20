---
title: Skill API
description: Complete reference for SKILL.md parameters and triggers
---

# Skill API Reference

Complete reference for DocuGen's SKILL.md configuration and capabilities.

## Trigger phrases

DocuGen activates when you use these phrases:

| Trigger | Example |
|---------|---------|
| `document this workflow` | "Document this workflow: reset password" |
| `create a walkthrough` | "Create a walkthrough for the signup process" |
| `generate documentation` | "Generate documentation for settings page" |
| `record this process` | "Record this process: create new project" |
| `make a guide for` | "Make a guide for configuring notifications" |
| `document how to` | "Document how to invite team members" |
| `create step-by-step guide` | "Create step-by-step guide for deployment" |

## Recording parameters

### Required

| Parameter | Description | Example |
|-----------|-------------|---------|
| `Starting URL` | Initial page to navigate to | `https://github.com/new` |

### Optional

| Parameter | Default | Description |
|-----------|---------|-------------|
| `Audience` | `intermediate` | `beginner`, `intermediate`, or `expert` |
| `Template` | `walkthrough` | `walkthrough`, `quick_reference`, or `tutorial` |
| `Output` | Auto-generated | Output file path |
| `Image format` | `png` | `png` or `jpg` |
| `Embed images` | `false` | `true` for Base64 embedding |

### Example with all options

```
Document this workflow: Configure repository settings
Starting URL: https://github.com/user/repo/settings
Audience: beginner
Template: walkthrough
Output: ./docs/repo-settings.md
Image format: png
Embed images: false
```

## Workflow phases

### Phase 1: Initiation

DocuGen validates requirements and sets up:

1. Checks for Playwright MCP or Chrome DevTools MCP
2. Creates output directory for images
3. Navigates to starting URL
4. Confirms workflow goal with user

### Phase 2: Recording

For each action:

1. Captures screenshot before action
2. Records element metadata
3. Executes action via MCP
4. Captures screenshot after action
5. Compares using SSIM (threshold < 0.90)
6. Marks significant changes as step boundaries

### Phase 3: Processing

After recording:

1. `detect_step.py` — Finalizes step boundaries
2. `annotate_screenshot.py` — Adds visual annotations
3. `process_images.py` — Optimizes file sizes

### Phase 4: Generation

1. Loads `writing_style_guide.md` reference
2. Runs `generate_markdown.py`
3. Enriches descriptions with context
4. Auto-detects prerequisites
5. Generates expected results
6. Adds troubleshooting section

### Phase 5: Output

1. Saves markdown to output directory
2. Verifies image references
3. Generates TOC if needed
4. Presents summary

## Session data format

Recording sessions are stored as JSON:

```json
{
  "sessionId": "uuid",
  "startUrl": "https://example.com",
  "workflowDescription": "Create a new project",
  "startTime": "2026-01-20T10:00:00Z",
  "steps": [
    {
      "step": 1,
      "action": "click",
      "selector": "button#new-project",
      "elementText": "New Project",
      "ariaLabel": "Create new project",
      "boundingBox": {
        "x": 100, "y": 200, "width": 120, "height": 40
      },
      "screenshotBefore": "step-01-before.png",
      "screenshotAfter": "step-01-after.png",
      "ssimScore": 0.72,
      "timestamp": "2026-01-20T10:00:05Z"
    }
  ],
  "endTime": "2026-01-20T10:05:00Z"
}
```

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SSIM_THRESHOLD` | `0.90` | Step detection sensitivity |
