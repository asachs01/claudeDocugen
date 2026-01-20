# DocuGen Documentation Site Design

**Date:** 2026-01-20
**Status:** Approved

## Overview

Create a documentation website for DocuGen using Astro Starlight, with frictionless curl|bash installation.

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Audience | Both end users and developers | Comprehensive docs for all users |
| Framework | Astro Starlight | Official docs theme, batteries included |
| Location | Same repo in `/docs` folder | Keep docs in sync with code |
| Hosting | GitHub Pages | Free, automatic deploys |
| Installation | curl\|bash + PowerShell | Dead simple, no manual steps |

## Installation Experience

### Unix/macOS
```bash
curl -fsSL https://raw.githubusercontent.com/USER/claudeDocugen/main/install.sh | bash
```

### Windows PowerShell
```powershell
irm https://raw.githubusercontent.com/USER/claudeDocugen/main/install.ps1 | iex
```

### Installer Behavior
1. Check for Python 3.8+
2. Create `~/.claude/skills/docugen/`
3. Download skill files
4. Install dependencies: `pip install pillow scikit-image jinja2`
5. Verify installation
6. Print success with example command

### Installer Flags
- `--no-deps` - Skip Python dependency installation
- `--path <dir>` - Custom install location
- `--update` - Update existing installation

## Site Architecture

```
docs/
├── src/
│   ├── content/
│   │   └── docs/
│   │       ├── getting-started/
│   │       │   ├── index.md          # Quick start
│   │       │   ├── installation.md   # Setup requirements
│   │       │   └── first-workflow.md # Tutorial
│   │       ├── guides/
│   │       │   ├── recording.md      # Recording workflows
│   │       │   ├── annotation.md     # Screenshot options
│   │       │   ├── templates.md      # Template customization
│   │       │   └── audiences.md      # Audience levels
│   │       ├── reference/
│   │       │   ├── skill-api.md      # SKILL.md parameters
│   │       │   ├── scripts.md        # Python CLI reference
│   │       │   └── configuration.md  # Config options
│   │       └── developers/
│   │           ├── architecture.md   # Internals
│   │           ├── extending.md      # Adding templates
│   │           └── contributing.md   # Contribution guide
│   └── assets/
├── astro.config.mjs
└── package.json
```

## Navigation Structure

1. **Getting Started** - Quick start, installation, first tutorial
2. **Guides** - How-to guides for common tasks
3. **Reference** - Complete API and CLI documentation
4. **Developers** - Architecture and contribution info

## Implementation Plan

1. Create GitHub repository
2. Create install.sh and install.ps1
3. Initialize Astro Starlight in /docs
4. Write all documentation pages
5. Configure GitHub Pages deployment
6. Update README with install commands
