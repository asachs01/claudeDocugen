---
title: Contributing
description: How to contribute to DocuGen
---

# Contributing to DocuGen

We welcome contributions! Here's how to get involved.

## Ways to contribute

- **Report bugs**: Open an issue describing the problem
- **Suggest features**: Share ideas for improvements
- **Improve docs**: Fix typos, add examples, clarify explanations
- **Submit code**: Fix bugs or implement features

## Development setup

### 1. Fork and clone

```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/claudeDocugen.git
cd claudeDocugen
```

### 2. Set up Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
pip install pillow scikit-image jinja2 numpy
pip install pytest  # For running tests
```

### 3. Set up docs site

```bash
cd docs
npm install
npm run dev  # Preview at localhost:4321
```

## Project structure

```
claudeDocugen/
├── docugen/                 # The skill
│   ├── SKILL.md            # Main skill file
│   ├── scripts/            # Python processing scripts
│   ├── references/         # Style guides
│   ├── templates/          # Output templates
│   └── assets/             # Styles, configs
├── docs/                    # Astro documentation site
├── install.sh              # Unix installer
├── install.ps1             # Windows installer
├── PRD.md                  # Product requirements
└── CHANGELOG.md            # Version history
```

## Making changes

### Code style

**Python:**
- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Keep functions focused and small

**Markdown:**
- Use ATX-style headers (`#`)
- One sentence per line (for better diffs)
- Include code examples

### Commit messages

Follow conventional commits:

```
feat: Add support for GIF screenshots
fix: Handle missing ARIA labels gracefully
docs: Add example for custom templates
chore: Update dependencies
```

### Testing

Run tests before submitting:

```bash
# Python tests
pytest docugen/scripts/

# Build docs
cd docs && npm run build
```

## Submitting changes

### 1. Create a branch

```bash
git checkout -b feature/my-feature
# or
git checkout -b fix/bug-description
```

### 2. Make changes

- Keep changes focused on one thing
- Update tests if needed
- Update docs if behavior changes

### 3. Commit

```bash
git add .
git commit -m "feat: Add my feature"
```

### 4. Push and create PR

```bash
git push origin feature/my-feature
```

Then open a Pull Request on GitHub.

### PR checklist

- [ ] Code follows project style
- [ ] Tests pass
- [ ] Docs updated if needed
- [ ] CHANGELOG.md updated
- [ ] Commit messages follow convention

## Issue guidelines

### Bug reports

Include:

1. **Description**: What happened?
2. **Expected**: What should have happened?
3. **Steps to reproduce**: How can we see the bug?
4. **Environment**: OS, Python version, Claude version
5. **Screenshots**: If visual issue

### Feature requests

Include:

1. **Problem**: What problem does this solve?
2. **Solution**: What do you propose?
3. **Alternatives**: Other approaches considered?
4. **Examples**: How would it be used?

## Code of conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn

## Getting help

- **Questions**: Open a Discussion on GitHub
- **Bugs**: Open an Issue
- **Chat**: [Link to Discord/Slack if applicable]

## Recognition

Contributors are recognized in:

- CHANGELOG.md (for each release)
- README.md (all-time contributors)
- Release notes

Thank you for contributing!
