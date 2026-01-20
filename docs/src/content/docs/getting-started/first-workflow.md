---
title: Your First Workflow
description: Create your first documentation with DocuGen
---

# Your First Workflow

Let's create documentation for a simple workflow: creating a new GitHub repository.

## Prerequisites

- DocuGen installed ([installation guide](/claudeDocugen/getting-started/installation))
- Claude Code or Claude.ai with Playwright MCP
- GitHub account

## Step 1: Start the recording

Tell Claude what you want to document:

```
Document this workflow: Create a new GitHub repository
Starting URL: https://github.com/new
Audience: beginner
```

Claude will:
1. Launch a browser via Playwright MCP
2. Navigate to github.com/new
3. Wait for your instructions

## Step 2: Perform the workflow

Walk Claude through each action:

```
Enter "my-test-project" in the repository name field
```

Claude captures:
- Screenshot before the action
- Element metadata (selector, text, ARIA labels)
- Screenshot after the action
- SSIM comparison to detect meaningful changes

Continue with each step:

```
Add description: "A test project for DocuGen"
```

```
Select "Public" for visibility
```

```
Check "Add a README file"
```

```
Click "Create repository"
```

## Step 3: End recording

When finished:

```
End recording and generate documentation
```

## Step 4: Review output

DocuGen generates markdown like this:

```markdown
# Create a New GitHub Repository

## Overview

This guide walks you through creating a new GitHub repository
with a README file.

## Prerequisites

- Active GitHub account
- Logged into GitHub

## Steps

### Step 1: Enter repository name

The repository name identifies your project and becomes part of
the URL. Choose something descriptive and memorable.

Enter `my-test-project` in the **Repository name** field.

![Step 1: Enter repository name](./images/step-01-enter-repository-name.png)

**Expected result:** The name field shows your text with a green
checkmark indicating the name is available.

### Step 2: Add description

A description helps others understand your project's purpose.

Enter your description in the **Description** field.

![Step 2: Add description](./images/step-02-add-description.png)

...
```

## What happened behind the scenes

1. **Screenshot capture** — Before/after each action
2. **SSIM analysis** — Detected which actions caused meaningful visual changes
3. **Element detection** — Captured selectors and accessibility labels
4. **Context generation** — Inferred *why* each step matters
5. **Annotation** — Added highlight boxes to screenshots
6. **Template rendering** — Assembled markdown from walkthrough template

## Customizing the output

### Change audience level

```
Regenerate for expert audience
```

Output becomes more concise, warnings removed.

### Use different template

```
Generate as quick reference instead
```

Creates condensed checklist format.

### Add more troubleshooting

```
Add troubleshooting for "repository name already exists"
```

## Next steps

- [Recording workflows](/claudeDocugen/guides/recording) — Advanced recording techniques
- [Screenshot annotation](/claudeDocugen/guides/annotation) — Customize highlights and callouts
- [Templates](/claudeDocugen/guides/templates) — Create your own templates
