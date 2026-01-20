# DocuGen

AI-powered documentation generator for web workflows. Transform click-throughs into professional documentation with annotated screenshots and contextual explanations.

[![Documentation](https://img.shields.io/badge/docs-asachs01.github.io%2FclaudeDocugen-blue)](https://asachs01.github.io/claudeDocugen)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Install

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/asachs01/claudeDocugen/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/asachs01/claudeDocugen/main/install.ps1 | iex
```

## Quick Start

In Claude Code or Claude.ai:

```
Document this workflow: Create a new GitHub repository
Starting URL: https://github.com/new
```

DocuGen will:
1. Navigate to the URL
2. Guide you through recording each action
3. Capture and annotate screenshots
4. Generate professional markdown documentation

## Features

- **Semantic Understanding** — Not just "click here" — explains *why* each step matters
- **Annotated Screenshots** — Automatic highlights, arrows, callouts, and click indicators
- **Sensitive Data Protection** — Auto-blurs passwords, SSNs, API keys
- **Audience Adaptation** — Generate beginner, intermediate, or expert versions
- **Professional Output** — Prerequisites, numbered steps, expected results, troubleshooting

## Example Output

```markdown
# Create a New GitHub Repository

## Prerequisites
- Active GitHub account
- Logged into GitHub

## Steps

### Step 1: Enter repository name
The repository name identifies your project and becomes part of the URL.

Enter `my-project` in the **Repository name** field.

![Step 1](./images/step-01-enter-repository-name.png)

**Expected result:** Green checkmark indicates name is available.
```

## Documentation

Full documentation: **[asachs01.github.io/claudeDocugen](https://asachs01.github.io/claudeDocugen)**

- [Quick Start](https://asachs01.github.io/claudeDocugen/getting-started/)
- [Recording Workflows](https://asachs01.github.io/claudeDocugen/guides/recording/)
- [API Reference](https://asachs01.github.io/claudeDocugen/reference/skill-api/)
- [Extending DocuGen](https://asachs01.github.io/claudeDocugen/developers/extending/)

## Requirements

- Python 3.8+
- Claude Code or Claude.ai with Playwright MCP

## License

MIT
