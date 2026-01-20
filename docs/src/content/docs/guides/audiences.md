---
title: Audience Adaptation
description: Adjust documentation for different skill levels
---

# Audience Adaptation

DocuGen generates documentation tailored to your audience's expertise level.

## Audience levels

### Beginner

Full context for users new to the application:

- Detailed explanations of *why* each step matters
- Warnings for irreversible actions
- Navigation hints ("in the sidebar", "top-right corner")
- Technical terms defined
- Verbose expected results

### Intermediate

Standard documentation for regular users:

- Brief purpose for each step
- Critical warnings only
- Concise expected results
- Technical terms assumed known

### Expert

Minimal documentation for power users:

- Actions only, no context
- No warnings (except critical)
- Expected results abbreviated or omitted
- Fastest path through workflow

## Specifying audience

### During recording

```
Document this workflow: Configure CI/CD pipeline
Starting URL: https://github.com/settings/actions
Audience: expert
```

### During generation

```
Regenerate documentation for beginner audience
```

### Via CLI

```bash
# Not directly supported in CLI — audience affects Claude's generation
```

## Comparison example

The same step rendered for each audience:

### Beginner version

```markdown
### Step 3: Save your project

Before you can share your project with others, you need to save it
first. This ensures all your changes are stored permanently and
creates a unique link you can share with collaborators.

> **Warning:** Saving cannot be undone. Make sure you're satisfied
> with your project name and settings before proceeding.

Click the **Save** button (the blue button with a disk icon) in the
top-right corner of the screen.

**Expected result:** A green "Saved successfully!" message appears
briefly at the top of the screen, and the URL in your browser's
address bar changes to include your new project ID (e.g.,
`/projects/abc123`).
```

### Intermediate version

```markdown
### Step 3: Save your project

Click **Save** in the top-right corner to store your changes.

> **Warning:** This action cannot be undone.

**Expected result:** "Saved successfully!" confirmation appears.
```

### Expert version

```markdown
### Step 3: Save your project

Click **Save**. Confirmation message confirms success.
```

## Adaptation matrix

| Aspect | Beginner | Intermediate | Expert |
|--------|----------|--------------|--------|
| Step length | 50-100 words | 25-50 words | 10-25 words |
| Context | Full explanation | Brief purpose | Omit |
| Warnings | All applicable | Critical only | Rare |
| Screenshots | Every step | Key steps | Minimal |
| Navigation hints | Detailed | Brief | Omit |
| Terminology | Defined inline | Assumed known | Assumed known |
| Troubleshooting | Comprehensive | Common issues | Omit |

## Mixed audiences

For documentation serving multiple audiences, consider:

### 1. Collapsible details

```markdown
### Step 3: Save your project

Click **Save** to store your changes.

<details>
<summary>More information</summary>

Saving creates a permanent record of your project. Once saved,
the project URL becomes shareable with collaborators.

</details>
```

### 2. Separate documents

Generate multiple versions:

```
Generate beginner version to ./docs/guide-beginner.md
Generate expert version to ./docs/guide-expert.md
```

### 3. Quick reference companion

Pair a full guide with a quick reference:

```
Generate walkthrough for beginners
Also generate quick_reference for the same workflow
```

## When to use each level

| Audience | Use case |
|----------|----------|
| Beginner | Onboarding docs, training materials, external users |
| Intermediate | Internal knowledge base, standard procedures |
| Expert | Quick references, cheat sheets, power user guides |

## Troubleshooting by audience

DocuGen also adapts troubleshooting sections:

### Beginner troubleshooting

```markdown
**Form won't submit**

This usually means a required field is missing or has an error.

1. Look for fields marked with a red border or asterisk (*)
2. Check that email addresses include @ and a domain
3. Scroll up — error messages sometimes appear at the top
4. Try a different browser if the problem persists
```

### Expert troubleshooting

```markdown
**Form won't submit**

Check required fields and input validation. Clear cache if persists.
```
