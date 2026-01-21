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
2. **Interactive Redaction Review** (see below)
3. Run `annotate_screenshot.py` to add visual annotations
4. Run `process_images.py` to optimize file sizes

### Interactive Redaction (User Prompts)

Before annotating screenshots, prompt the user to review detected sensitive regions.
Use `AskUserQuestion` to give users control over what gets redacted.

#### Auto-Detection First

Smart annotation auto-detects common sensitive fields:
- Password fields (`type="password"`)
- SSN, credit card, API key fields
- Email and phone number inputs

#### Prompt User for Confirmation

After auto-detection, present findings to user:

```
AskUserQuestion:
  question: "I detected 3 potentially sensitive fields to blur. Review?"
  header: "Redaction"
  options:
    - label: "Show me what you found"
      description: "Review auto-detected fields before blurring"
    - label: "Blur all detected fields"
      description: "Trust auto-detection and blur everything"
    - label: "No redaction needed"
      description: "Skip all blurring for this workflow"
```

#### If User Selects Review

Present each detected field:

```
AskUserQuestion:
  question: "Field: 'Password' input at coordinates (120, 340). Blur this?"
  header: "Blur field?"
  options:
    - label: "Yes, blur it"
      description: "Add blur to hide this content"
    - label: "No, keep visible"
      description: "This content is safe to show"
    - label: "Blur all remaining"
      description: "Skip review, blur everything else"
```

#### Custom Redaction Regions

After auto-detection review, offer to add custom regions:

```
AskUserQuestion:
  question: "Add any custom regions to blur?"
  header: "Custom blur"
  options:
    - label: "Yes, let me specify"
      description: "I'll describe regions that need blurring"
    - label: "No, we're done"
      description: "Proceed with current selections"
```

If user wants custom regions, prompt for description:
- "Describe what to blur (e.g., 'the email address in the top right')"
- Use element metadata to locate described content
- Confirm coordinates before applying

#### Redaction Session Data

Track redaction decisions in session:

```json
{
  "redactionReview": {
    "autoDetected": [
      {"field": "password", "coords": [120, 340, 200, 30], "approved": true},
      {"field": "email", "coords": [120, 400, 200, 30], "approved": false}
    ],
    "customRegions": [
      {"description": "company logo", "coords": [10, 10, 100, 50]}
    ],
    "userChoice": "reviewed"
  }
}
```

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

## Contextual Description Generation (FR-3.2, US-2)

During Phase 4, analyze the captured workflow data to generate contextual descriptions that explain
**why** each step matters, not just what to do.

### Semantic Analysis Process

For each recorded step, analyze:

1. **Workflow Context**: The overall goal described by the user
2. **DOM Metadata**: Element text, ARIA labels, and semantic roles
3. **Step Sequence**: Position in workflow and relationship to adjacent steps
4. **Visual Changes**: What changed between before/after screenshots

### Description Generation Rules

Apply `references/writing_style_guide.md` and generate:

1. **Purpose Statement**: Why this action is necessary
   - Connect action to workflow goal
   - Explain what capability or state this enables
   - Example: "Access the project settings to configure team permissions"

2. **Action Description**: What to do (imperative, ≤25 words)
   - Use element text/label for specificity
   - Include location hints from DOM structure
   - Example: "Click **Settings** in the left sidebar menu"

3. **Expected Result**: What user should observe
   - Describe visible confirmation of success
   - Use present tense
   - Example: "The Settings panel opens with the General tab selected"

### Output Format

Generate enriched step data as JSON:

```json
{
  "step": 1,
  "action": "click",
  "elementText": "New Project",
  "context": "Creates a new project workspace to organize your team's work",
  "description": "Click **New Project** in the top navigation bar to start creating your project.",
  "expected": "The New Project dialog appears with fields for project name and description.",
  "prerequisites_detected": ["Logged into account", "On dashboard page"]
}
```

### Prerequisites Auto-Detection

Analyze the workflow to automatically detect prerequisites:

| Pattern | Detected Prerequisite |
|---------|----------------------|
| Login page in first steps | "Active user account" |
| Navigation from dashboard | "Logged into the application" |
| Specific URL patterns | "Access to [feature name]" |
| Role-specific UI elements | "Appropriate permissions" |
| Form pre-filled data | "Required information prepared" |

### Context Inference Examples

| Element Metadata | Generated Context |
|-----------------|-------------------|
| `button#submit-form, "Submit"` | "Submits the completed form for processing" |
| `a[href="/settings"], "Settings"` | "Opens application settings to customize your experience" |
| `input[type="search"], placeholder="Search..."` | "Filters results to find specific items quickly" |
| `button.delete, "Delete"` | "Permanently removes the selected item" |
| `nav > a, "Dashboard"` | "Returns to the main overview of your workspace" |

### Quality Guidelines

- **Avoid generic phrases**: Don't write "Click the button" - specify which button and why
- **Connect to user goals**: Each step should relate to the workflow objective
- **Be specific about outcomes**: "The modal closes" vs "The save is confirmed"
- **Match audience level**: Adjust verbosity based on `beginner|intermediate|expert`

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
- `generatePdf`: true (default) - Generate PDF alongside markdown

### Redaction Options
- `interactiveRedaction`: true (default) - Prompt user to review detected fields
- `autoBlurSensitive`: true (default) - Auto-detect and blur sensitive fields
- `redactionReviewMode`: "summary" | "each" | "none"
  - `summary`: Show count of detected fields, ask to review
  - `each`: Prompt for each detected field individually
  - `none`: Auto-blur without prompting (use with caution)

## Audience Adaptation (US-4)

Adjust documentation detail and tone based on the target audience level.

### Beginner Level (`audience=beginner`)

Generate documentation with:
- **Full context**: Explain why each step is necessary and what it accomplishes
- **Detailed warnings**: Include caution notes for irreversible actions
- **Navigation hints**: Describe where to find elements on screen
- **Terminology explanations**: Define any technical terms
- **Expected results**: Detailed descriptions of what should happen

**Example step (beginner):**
```markdown
### Step 3: Save your project

Before you can share your project with others, you need to save it first.
This ensures all your changes are stored and creates a link you can share.

> **Note:** Saving cannot be undone. Make sure you're happy with your
> project name before proceeding.

Click the **Save** button (the blue button with a disk icon) in the top-right
corner of the screen.

**Expected result:** A green "Saved successfully!" message appears briefly,
and the URL in your browser's address bar changes to include your project ID.
```

### Intermediate Level (`audience=intermediate`)

Generate documentation with:
- **Standard context**: Brief explanation of step purpose
- **Key warnings only**: Only critical cautions
- **Concise expected results**: What confirms success

**Example step (intermediate):**
```markdown
### Step 3: Save your project

Click **Save** in the top-right corner to store your changes.

> **Warning:** This action cannot be undone.

**Expected result:** "Saved successfully!" confirmation appears.
```

### Expert Level (`audience=expert`)

Generate documentation with:
- **Minimal context**: Just the action
- **No warnings**: Unless absolutely critical
- **Brief expected results**: Single sentence or omitted

**Example step (expert):**
```markdown
### Step 3: Save your project

Click **Save**. Confirmation message confirms success.
```

### Adaptation Matrix

| Aspect | Beginner | Intermediate | Expert |
|--------|----------|--------------|--------|
| Step length | 50-100 words | 25-50 words | 10-25 words |
| Context | Full explanation | Brief purpose | Omit |
| Warnings | All applicable | Critical only | Rare |
| Screenshots | Every step | Key steps | Minimal |
| Navigation hints | Detailed | Brief | Omit |
| Terminology | Defined | Assumed known | Assumed known |

## Troubleshooting Generation (FR-3.7)

Automatically generate a troubleshooting section based on workflow analysis.
Reference `references/troubleshooting_patterns.md` for templates.

### Workflow Type Detection

Analyze the recorded workflow to identify type and generate relevant issues:

| Workflow Pattern | Troubleshooting Focus |
|-----------------|----------------------|
| Login/authentication | Session expired, invalid credentials, 2FA issues |
| Form submission | Validation errors, required fields, format issues |
| File upload | Size limits, format restrictions, upload failures |
| Search/filter | No results, too many results, filter confusion |
| Settings/configuration | Permission denied, changes not saving |
| Data creation | Naming conflicts, duplicate entries |
| Navigation | Page not found, access denied |

### Auto-Detection Rules

Based on captured UI elements, automatically detect applicable issues:

```json
{
  "detected_patterns": [
    {"pattern": "input[type='password']", "issue": "authentication"},
    {"pattern": "input[type='file']", "issue": "file_upload"},
    {"pattern": "form[action]", "issue": "form_submission"},
    {"pattern": ".search-input", "issue": "search_results"},
    {"pattern": "button:disabled", "issue": "permissions"}
  ]
}
```

### Troubleshooting Output Format

Generate 2-3 relevant issues per workflow:

```markdown
## Troubleshooting

**Form submission fails without error message**
1. Check all required fields are completed (marked with *)
2. Verify email and phone fields are in correct format
3. Scroll up to check for error messages at the top of the form

**"Invalid input" error on project name**
Project names can only contain letters, numbers, and hyphens. Remove any
special characters or spaces and try again.

**Save button is disabled**
This indicates you may not have edit permissions for this project. Contact
your organization administrator to request Editor access.
```

### Issue Priority

Select troubleshooting issues in this priority:
1. **Highly likely**: Issues directly related to recorded workflow
2. **Commonly encountered**: General issues for this workflow type
3. **Edge cases**: Only if space permits

## Playwright MCP Integration

### Browser Launch and Navigation

Use Playwright MCP to control the browser. The following tools are essential:

```
# Launch browser with appropriate viewport
browser_launch: { headless: false, viewport: { width: 1280, height: 720 } }

# Navigate to starting URL
browser_navigate: { url: "https://example.com" }

# Take screenshot at CSS resolution (ALWAYS use scale: "css"!)
browser_screenshot: { path: "step-01.png", scale: "css", fullPage: false }
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

### Atomic Coordinate Capture (CRITICAL)

**The #1 cause of misaligned annotations is capturing coordinates and screenshots at different times.**

Bounding boxes MUST be captured at the EXACT same page state as the screenshot. Any scroll,
reflow, dynamic content change, or delay between getting coordinates and taking the screenshot
will cause misalignment.

**The Golden Rule: Capture coordinates immediately before/after screenshot, same page state.**

```javascript
// CORRECT: Atomic capture sequence
await page.waitForLoadState('networkidle');  // Wait for page to stabilize
const bbox = await element.boundingBox();     // Get coordinates NOW
await page.screenshot({ path: 'step.png', scale: 'css' });  // Screenshot NOW
// bbox coordinates match the screenshot exactly
```

```javascript
// WRONG: Non-atomic capture (causes misalignment)
const bbox = await element.boundingBox();     // Get coordinates
await someOtherAction();                       // Page might change!
await page.screenshot({ path: 'step.png' });  // Screenshot - bbox is now stale
```

### Always Use CSS Scale

**ALWAYS use `scale: "css"` for screenshots.** This ensures coordinates from `boundingBox()`
match the screenshot pixels directly, eliminating DPI/devicePixelRatio issues entirely.

```
browser_screenshot: { path: "step-01.png", scale: "css" }
```

With `scale: "css"`:
- Screenshot pixels = CSS pixels
- `boundingBox()` returns CSS pixels
- Coordinates work directly, no transformation needed

**Do NOT rely on auto-scale detection** - it's a fallback, not a solution. Get it right the first time.

### Viewport Consistency

Lock viewport size at the start of recording and don't change it:

```javascript
await page.setViewportSize({ width: 1280, height: 720 });
```

Store viewport in session metadata for validation:

```json
{
  "viewport": { "width": 1280, "height": 720 },
  "elements": [
    {
      "isTarget": true,
      "boundingBox": { "x": 100, "y": 200, "width": 120, "height": 40 }
    }
  ]
}
```

### Action Recording

For each user-directed action:

1. **Wait for page stability** (`networkidle` or animations complete)
2. **Identify target element** using Playwright selectors
3. **ATOMIC CAPTURE** (do these together, no delays!):
   - Capture element metadata (selector, text, ARIA, boundingBox)
   - Take pre-action screenshot with `scale: "css"`
4. **Execute action** via appropriate Playwright tool:
   - `browser_click`: Click interactions
   - `browser_type`: Text input
   - `browser_select`: Dropdown selection
   - `browser_scroll`: Scroll actions
5. **Wait for network idle** or specified condition
6. **Take post-action screenshot** with `scale: "css"`
7. **Compare with SSIM** to detect step boundary
8. **Record DOM mutations** if significant

### Example Recording Flow

```
User: "Document creating a new GitHub repository"

1. browser_navigate: https://github.com/new
2. Wait for networkidle
3. [User says: "Enter repository name 'my-project'"]
4. ATOMIC: Capture metadata for input#repository-name (boundingBox, text, ARIA)
5. ATOMIC: browser_screenshot: { path: "step-01-before.png", scale: "css" }
   ↑ Steps 4-5 must happen with NO page changes between them!
6. browser_type: { selector: "input#repository-name", text: "my-project" }
7. Wait for networkidle
8. browser_screenshot: { path: "step-01-after.png", scale: "css" }
9. Run detect_step.py step-01-before.png step-01-after.png
10. If significant change: record as Step 1
11. Continue with next action...
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
