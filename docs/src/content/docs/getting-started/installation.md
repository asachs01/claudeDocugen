---
title: Installation
description: Install DocuGen and its dependencies
---

# Installation

DocuGen requires Python 3.8+ and installs as a Claude Code skill.

## Quick install

### macOS / Linux

```bash
curl -fsSL https://raw.githubusercontent.com/asachs01/claudeDocugen/main/install.sh | bash
```

### Windows (PowerShell)

```powershell
irm https://raw.githubusercontent.com/asachs01/claudeDocugen/main/install.ps1 | iex
```

## What the installer does

1. **Checks Python version** — Requires Python 3.8 or higher
2. **Creates skill directory** — `~/.claude/skills/docugen/`
3. **Downloads skill files** — SKILL.md, scripts, templates, references
4. **Installs dependencies** — pillow, scikit-image, jinja2, numpy
5. **Verifies installation** — Confirms all files are in place

## Installation options

### Skip dependency installation

If you prefer to manage Python packages yourself:

```bash
# Unix/macOS
curl -fsSL https://raw.githubusercontent.com/asachs01/claudeDocugen/main/install.sh | bash -s -- --no-deps

# Windows
.\install.ps1 -NoDeps
```

Then install manually:

```bash
pip install pillow scikit-image jinja2 numpy
```

### Custom installation path

```bash
# Unix/macOS
curl -fsSL https://raw.githubusercontent.com/asachs01/claudeDocugen/main/install.sh | bash -s -- --path /custom/path

# Windows
.\install.ps1 -Path "C:\custom\path"
```

### Update existing installation

```bash
# Unix/macOS
curl -fsSL https://raw.githubusercontent.com/asachs01/claudeDocugen/main/install.sh | bash -s -- --update

# Windows
.\install.ps1 -Update
```

## Manual installation

If you prefer not to use the installer:

1. Clone the repository:
   ```bash
   git clone https://github.com/asachs01/claudeDocugen.git
   ```

2. Copy the skill to your Claude skills directory:
   ```bash
   cp -r claudeDocugen/docugen ~/.claude/skills/docugen
   ```

3. Install Python dependencies:
   ```bash
   pip install pillow scikit-image jinja2 numpy
   ```

## Requirements

### Python packages

| Package | Version | Purpose |
|---------|---------|---------|
| pillow | 9.0+ | Screenshot annotation |
| scikit-image | 0.19+ | SSIM step detection |
| jinja2 | 3.0+ | Template rendering |
| numpy | 1.21+ | Image processing |

### MCP servers (for recording)

DocuGen works with browser automation MCPs:

- **Playwright MCP** (recommended) — Full browser control
- **Chrome DevTools MCP** — Lightweight alternative

See [Recording workflows](/claudeDocugen/guides/recording) for MCP setup.

## Verify installation

After installation, verify by asking Claude:

```
What DocuGen templates are available?
```

Claude should list: walkthrough, quick_reference, tutorial

## Troubleshooting

### "Python not found"

Install Python 3.8+ from [python.org](https://python.org) or:

```bash
# macOS
brew install python@3.11

# Ubuntu/Debian
sudo apt install python3

# Windows
winget install Python.Python.3.11
```

### "Permission denied" on install

Run with sudo (Unix) or as Administrator (Windows):

```bash
# Unix/macOS
sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/asachs01/claudeDocugen/main/install.sh)"
```

### Dependencies fail to install

Try installing in a virtual environment:

```bash
python3 -m venv ~/.docugen-venv
source ~/.docugen-venv/bin/activate
pip install pillow scikit-image jinja2 numpy
```
