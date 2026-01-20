---
name: docugen
description: |
  Automate creation of step-by-step documentation from web-based workflows.
  Use when: (1) "document this workflow", (2) "create a walkthrough for [URL]",
  (3) "generate documentation", (4) "record this process", (5) "make a guide for".
  Produces professional markdown with annotated screenshots, contextual explanations,
  prerequisites, and expected results.
author: WYRE Technology
version: 1.0.0
date: 2026-01-20
triggers:
  - document this workflow
  - create a walkthrough
  - generate documentation
  - record this process
  - make a guide for
  - document how to
  - create step-by-step guide
---

# DocuGen: Intelligent Documentation Generator

DocuGen transforms web-based workflows into professional-quality documentation with
annotated screenshots and contextual explanations.

## Quick Start

To document a workflow:
1. Provide the starting URL
2. Describe the workflow goal (e.g., "create a new project")
3. DocuGen will guide you through the recording process

**Example:**
```
Document this workflow: Create a new repository on GitHub
Starting URL: https://github.com/new
```

## Capabilities

- **Semantic Understanding**: Generates contextual explanations, not just "click here"
- **Screenshot Annotation**: Highlights, arrows, and numbered callouts
- **Professional Output**: Markdown with proper structure, prerequisites, and expected results
- **Audience Adaptation**: Adjust detail level for beginner/intermediate/expert

## Requirements

### MCP Integrations (Required)
- **Playwright MCP** or **Chrome DevTools MCP**: For browser automation and DOM access

### Python Dependencies
- PIL/Pillow: Screenshot annotation
- scikit-image: SSIM step detection

## Workflow Orchestration

### Phase 1: Initiation
When user provides URL and workflow description:
1. Validate Playwright MCP or Chrome DevTools MCP is available
2. Create output directory for images
3. Navigate to starting URL
4. Confirm workflow goal with user

### Phase 2: Recording
For each user action:
1. Capture screenshot before action
2. Record element metadata (selector, text, ARIA labels)
3. Execute action via MCP
4. Capture screenshot after action
5. Compare screenshots using SSIM (threshold < 0.90)
6. If significant change detected, mark as step boundary

### Phase 3: Processing
After recording completes:
1. Run `detect_step.py` to finalize step boundaries
2. Run `annotate_screenshot.py` to add visual annotations
3. Run `process_images.py` to optimize file sizes

### Phase 4: Generation
1. Load `writing_style_guide.md` reference for quality standards
2. Run `generate_markdown.py` with captured data
3. Enrich step descriptions with contextual explanations
4. Auto-detect prerequisites based on workflow analysis
5. Generate expected results for each step
6. Add troubleshooting section for common issues

### Phase 5: Output
1. Save markdown to output directory
2. Verify all image references are valid
3. Generate table of contents if multi-section
4. Present summary to user

## Progressive Disclosure

Load references as needed:
- `references/writing_style_guide.md` - During Phase 4 generation
- `references/annotation_conventions.md` - During Phase 3 processing
- `references/troubleshooting_patterns.md` - For troubleshooting section

## Output Structure

Generated documentation follows this structure:
```markdown
# [Workflow Title]

## Overview
[Brief description of what this guide covers]

## Prerequisites
- [Auto-detected requirements]
- [User-provided prerequisites]

## Steps

### Step 1: [Action Title]
[Contextual description explaining WHY this step matters]

![Step 1 Screenshot](./images/step-01-description.png)

**Expected result:** [What user should see after this step]

[... additional steps ...]

## Troubleshooting

**[Common Issue]**
[Description and resolution]
```

## Configuration

### Audience Levels
- `beginner`: Full context, warnings, detailed explanations
- `intermediate`: Standard detail, key warnings only
- `expert`: Concise, minimal explanation

### Output Options
- `imageFormat`: png (default), jpg
- `embedImages`: false (file references) or true (base64)
- `includeTableOfContents`: true for 5+ steps

## Playwright MCP Integration

### Browser Launch and Navigation

Use Playwright MCP to control the browser. The following tools are essential:

```
# Launch browser with appropriate viewport
browser_launch: { headless: false, viewport: { width: 1280, height: 720 } }

# Navigate to starting URL
browser_navigate: { url: "https://example.com" }

# Take screenshot at native resolution
browser_screenshot: { path: "step-01.png", fullPage: false }
```

### Element Interaction and Metadata Capture

Before each action, capture element metadata for documentation:

```javascript
// Get element metadata
{
  selector: "button#submit",           // CSS selector used
  text: "Submit",                       // Visible text content
  ariaLabel: "Submit form",            // ARIA label if present
  role: "button",                       // ARIA role
  boundingBox: { x, y, width, height } // Position for annotation
}
```

### DOM Event Tracking (FR-1.5)

For dynamic content, track DOM mutations:

```
// MutationObserver events to track:
- childList: Elements added/removed
- attributes: Class changes, visibility changes
- characterData: Text content changes
```

### Session Data Structure

Store recording session as JSON for processing:

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
      "boundingBox": { "x": 100, "y": 200, "width": 120, "height": 40 },
      "screenshotBefore": "step-01-before.png",
      "screenshotAfter": "step-01-after.png",
      "ssimScore": 0.72,
      "timestamp": "2026-01-20T10:00:05Z",
      "domChanges": ["modal opened", "form displayed"]
    }
  ],
  "endTime": "2026-01-20T10:05:00Z"
}
```

### Screenshot Capture Guidelines

- **Timing**: Capture before AND after each action
- **Resolution**: Native viewport resolution (target: 1280x720 minimum)
- **Performance**: Target <200ms per capture
- **Naming**: `step-{nn}-{action}.png` (e.g., `step-01-click-submit.png`)

### Action Recording

For each user-directed action:

1. **Identify target element** using Playwright selectors
2. **Capture element metadata** (selector, text, ARIA, bounds)
3. **Take pre-action screenshot**
4. **Execute action** via appropriate Playwright tool:
   - `browser_click`: Click interactions
   - `browser_type`: Text input
   - `browser_select`: Dropdown selection
   - `browser_scroll`: Scroll actions
5. **Wait for network idle** or specified condition
6. **Take post-action screenshot**
7. **Compare with SSIM** to detect step boundary
8. **Record DOM mutations** if significant

### Example Recording Flow

```
User: "Document creating a new GitHub repository"

1. browser_navigate: https://github.com/new
2. browser_screenshot: step-01-before.png
3. [User says: "Enter repository name 'my-project'"]
4. Capture metadata for input#repository-name
5. browser_type: { selector: "input#repository-name", text: "my-project" }
6. browser_screenshot: step-01-after.png
7. Run detect_step.py step-01-before.png step-01-after.png
8. If significant change: record as Step 1
9. Continue with next action...
```

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `detect_step.py` | SSIM-based step boundary detection |
| `annotate_screenshot.py` | Add highlights, arrows, callouts |
| `generate_markdown.py` | Template-based markdown assembly |
| `process_images.py` | Optimization and compression |

## Templates

| Template | Use Case |
|----------|----------|
| `walkthrough.md` | Default step-by-step guide |
| `quick_reference.md` | Condensed expert guide |
| `tutorial.md` | Learning-focused with exercises |
