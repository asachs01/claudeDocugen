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
