#!/usr/bin/env python3
"""
generate_markdown.py - Template-based markdown assembly for DocuGen

This script generates documentation markdown from captured workflow data,
applying templates and assembling the final output.

Usage:
    python generate_markdown.py <workflow_data.json> <output.md> [--template walkthrough]

Input JSON structure:
    {
        "title": "Workflow Title",
        "description": "Brief description",
        "prerequisites": ["Prerequisite 1", "Prerequisite 2"],
        "steps": [
            {
                "number": 1,
                "title": "Step Title",
                "description": "What this step does and why",
                "screenshot": "images/step-01.png",
                "expected_result": "What user should see"
            }
        ],
        "troubleshooting": [
            {
                "issue": "Issue title",
                "description": "What went wrong",
                "resolution": "How to fix it"
            }
        ]
    }

Dependencies:
    - jinja2 (optional, for advanced templates)
"""

import argparse
import base64
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Try to import Jinja2 for advanced templating
try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False


def encode_image_base64(image_path: Path) -> str:
    """
    Encode an image file as base64 data URI for embedding (FR-3.6).

    Args:
        image_path: Path to image file

    Returns:
        Base64 data URI string (e.g., "data:image/png;base64,...")
    """
    if not image_path.exists():
        return str(image_path)  # Return original path if file not found

    suffix = image_path.suffix.lower()
    mime_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
    }
    mime_type = mime_types.get(suffix, 'image/png')

    with open(image_path, 'rb') as f:
        encoded = base64.b64encode(f.read()).decode('utf-8')

    return f"data:{mime_type};base64,{encoded}"


def generate_toc(sections: List[Dict[str, Any]], min_steps: int = 5) -> str:
    """
    Generate table of contents for multi-section documents (FR-4.3).

    Args:
        sections: List of section dicts with 'title' and 'level' keys
        min_steps: Minimum steps to include TOC (default 5)

    Returns:
        Markdown TOC string, or empty string if below threshold
    """
    if len(sections) < min_steps:
        return ""

    lines = ["## Table of Contents", ""]
    for section in sections:
        title = section['title']
        level = section.get('level', 2)
        anchor = slugify(title)
        indent = "  " * (level - 2) if level > 2 else ""
        lines.append(f"{indent}- [{title}](#{anchor})")
    lines.append("")
    return "\n".join(lines)


def create_zip_package(
    output_dir: Path,
    markdown_file: Path,
    image_dir: Path,
    zip_name: str = None
) -> Path:
    """
    Create a zip package containing markdown and images.

    Args:
        output_dir: Directory to save zip file
        markdown_file: Path to markdown file
        image_dir: Directory containing images
        zip_name: Name for zip file (default: based on markdown filename)

    Returns:
        Path to created zip file
    """
    if zip_name is None:
        zip_name = markdown_file.stem + "_documentation.zip"

    zip_path = output_dir / zip_name

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add markdown file
        if markdown_file.exists():
            zf.write(markdown_file, markdown_file.name)

        # Add images
        if image_dir.exists() and image_dir.is_dir():
            for img_file in image_dir.iterdir():
                if img_file.is_file() and img_file.suffix.lower() in {'.png', '.jpg', '.jpeg', '.gif'}:
                    arcname = f"images/{img_file.name}"
                    zf.write(img_file, arcname)

    return zip_path


def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug for image naming.

    Args:
        text: Text to convert

    Returns:
        Lowercase slug with hyphens (e.g., "Click Submit Button" -> "click-submit-button")
    """
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and underscores with hyphens
    text = re.sub(r'[\s_]+', '-', text)
    # Remove non-alphanumeric characters except hyphens
    text = re.sub(r'[^a-z0-9-]', '', text)
    # Remove multiple consecutive hyphens
    text = re.sub(r'-+', '-', text)
    # Remove leading/trailing hyphens
    text = text.strip('-')
    # Limit length
    return text[:50]


def generate_image_filename(step_number: int, title: str, extension: str = 'png') -> str:
    """
    Generate consistent image filename for a step.

    Format: step-{nn}-{description_slug}.{ext}
    Example: step-01-click-submit-button.png
    """
    slug = slugify(title)
    return f"step-{step_number:02d}-{slug}.{extension}"


def generate_alt_text(step_number: int, title: str, action: str = None) -> str:
    """
    Generate WCAG-compliant alt text for screenshot.

    Args:
        step_number: Step number
        title: Step title
        action: Optional action description

    Returns:
        Descriptive alt text for accessibility
    """
    if action:
        return f"Step {step_number}: {title} - {action}"
    return f"Step {step_number}: {title}"


def load_workflow_data(data_path: Path) -> Dict[str, Any]:
    """Load workflow data from JSON file."""
    with open(data_path) as f:
        return json.load(f)


def load_template(template_name: str, template_dir: Path) -> Optional[str]:
    """Load a template file if it exists."""
    template_path = template_dir / f"{template_name}.md"
    if template_path.exists():
        return template_path.read_text()
    return None


def render_with_jinja2(template_path: Path, data: Dict[str, Any]) -> str:
    """
    Render a template using Jinja2.

    Args:
        template_path: Path to template file
        data: Data to pass to template

    Returns:
        Rendered markdown string
    """
    if not JINJA2_AVAILABLE:
        raise ImportError("Jinja2 is required for template rendering. Install with: pip install jinja2")

    template_dir = template_path.parent
    template_name = template_path.name

    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(['html', 'xml']),
        trim_blocks=True,
        lstrip_blocks=True
    )

    # Add custom filters
    env.filters['slugify'] = slugify
    env.filters['generate_image_filename'] = lambda s, n: generate_image_filename(n, s)
    env.filters['generate_alt_text'] = lambda s, n: generate_alt_text(n, s)

    template = env.get_template(template_name)

    # Add utility data
    data['generated_date'] = datetime.now().strftime('%Y-%m-%d')
    data['generated_timestamp'] = datetime.now().isoformat()

    return template.render(**data)


def generate_prerequisites_section(prerequisites: List[str]) -> str:
    """Generate the prerequisites section."""
    if not prerequisites:
        return ""

    lines = ["## Prerequisites", ""]
    for prereq in prerequisites:
        lines.append(f"- {prereq}")
    lines.append("")
    return "\n".join(lines)


def generate_step_section(
    step: Dict[str, Any],
    image_dir: str = './images',
    embed_images: bool = False,
    base_path: Path = None
) -> str:
    """
    Generate markdown for a single step with WCAG-compliant alt text.

    Args:
        step: Step data dictionary
        image_dir: Relative path to images directory
        embed_images: If True, embed images as base64 (FR-3.6)
        base_path: Base path for resolving image files when embedding
    """
    lines = [
        f"### Step {step['number']}: {step['title']}",
        "",
        step['description'],
        ""
    ]

    if step.get('screenshot'):
        screenshot_path = step['screenshot']
        # Generate proper alt text for accessibility (WCAG compliance)
        alt_text = generate_alt_text(
            step['number'],
            step['title'],
            step.get('action')
        )

        # Handle base64 embedding
        if embed_images and base_path:
            # Resolve the actual file path
            if screenshot_path.startswith('./'):
                actual_path = base_path / screenshot_path[2:]
            else:
                actual_path = base_path / screenshot_path
            screenshot_src = encode_image_base64(actual_path)
        else:
            screenshot_src = screenshot_path

        lines.append(f"![{alt_text}]({screenshot_src})")
        lines.append("")

    if step.get('expected_result'):
        lines.append(f"**Expected result:** {step['expected_result']}")
        lines.append("")

    return "\n".join(lines)


def generate_troubleshooting_section(issues: List[Dict[str, str]]) -> str:
    """Generate the troubleshooting section."""
    if not issues:
        return ""

    lines = ["## Troubleshooting", ""]

    for issue in issues:
        lines.append(f"**{issue['issue']}**")
        if issue.get('description'):
            lines.append(f"{issue['description']}")
        lines.append(f"{issue['resolution']}")
        lines.append("")

    return "\n".join(lines)


def generate_walkthrough(
    data: Dict[str, Any],
    embed_images: bool = False,
    base_path: Path = None,
    include_toc: bool = True
) -> str:
    """
    Generate a complete walkthrough document from workflow data.

    Args:
        data: Workflow data dictionary
        embed_images: If True, embed images as base64 (FR-3.6)
        base_path: Base path for resolving image files when embedding
        include_toc: If True, include table of contents for 5+ steps (FR-4.3)

    Returns:
        Complete markdown document string
    """
    sections = []
    toc_sections = []

    # Title
    sections.append(f"# {data['title']}")
    sections.append("")

    # Build TOC entries
    if data.get('description'):
        toc_sections.append({'title': 'Overview', 'level': 2})
    if data.get('prerequisites'):
        toc_sections.append({'title': 'Prerequisites', 'level': 2})
    toc_sections.append({'title': 'Steps', 'level': 2})
    for step in data.get('steps', []):
        toc_sections.append({
            'title': f"Step {step['number']}: {step['title']}",
            'level': 3
        })
    if data.get('troubleshooting'):
        toc_sections.append({'title': 'Troubleshooting', 'level': 2})

    # Include TOC if enough sections (FR-4.3)
    steps_count = len(data.get('steps', []))
    if include_toc and steps_count >= 5:
        sections.append(generate_toc(toc_sections, min_steps=5))

    # Overview
    if data.get('description'):
        sections.append("## Overview")
        sections.append("")
        sections.append(data['description'])
        sections.append("")

    # Prerequisites
    prereqs = generate_prerequisites_section(data.get('prerequisites', []))
    if prereqs:
        sections.append(prereqs)

    # Steps
    sections.append("## Steps")
    sections.append("")

    for step in data.get('steps', []):
        sections.append(generate_step_section(
            step,
            embed_images=embed_images,
            base_path=base_path
        ))

    # Troubleshooting
    troubleshooting = generate_troubleshooting_section(data.get('troubleshooting', []))
    if troubleshooting:
        sections.append(troubleshooting)

    # Footer
    sections.append("---")
    sections.append("")
    sections.append(f"*Documentation generated by DocuGen on {datetime.now().strftime('%Y-%m-%d')}*")

    return "\n".join(sections)


def generate_quick_reference(data: Dict[str, Any]) -> str:
    """
    Generate a condensed quick reference document.

    Args:
        data: Workflow data dictionary

    Returns:
        Condensed markdown document string
    """
    sections = []

    # Title
    sections.append(f"# {data['title']} - Quick Reference")
    sections.append("")

    # Condensed steps
    for step in data.get('steps', []):
        sections.append(f"{step['number']}. **{step['title']}**")

    sections.append("")
    sections.append("---")
    sections.append(f"*Quick reference generated by DocuGen*")

    return "\n".join(sections)


def main():
    parser = argparse.ArgumentParser(
        description='Generate markdown documentation from workflow data'
    )
    parser.add_argument('input', type=Path, help='Workflow data JSON file')
    parser.add_argument('output', type=Path, help='Output markdown file')
    parser.add_argument(
        '--template',
        choices=['walkthrough', 'quick_reference', 'tutorial'],
        default='walkthrough',
        help='Output template to use'
    )
    parser.add_argument(
        '--template-dir',
        type=Path,
        default=Path(__file__).parent.parent / 'templates',
        help='Directory containing template files'
    )
    parser.add_argument(
        '--jinja2',
        action='store_true',
        help='Use Jinja2 templating engine for advanced templates'
    )
    parser.add_argument(
        '--image-dir',
        type=str,
        default='./images',
        help='Relative path to images directory in output'
    )
    parser.add_argument(
        '--embed-images',
        action='store_true',
        help='Embed images as base64 data URIs (FR-3.6)'
    )
    parser.add_argument(
        '--no-toc',
        action='store_true',
        help='Disable table of contents generation'
    )
    parser.add_argument(
        '--zip',
        action='store_true',
        help='Create a zip package with markdown and images'
    )

    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(2)

    data = load_workflow_data(args.input)

    # Process steps to ensure proper image paths
    for step in data.get('steps', []):
        if not step.get('screenshot'):
            # Generate screenshot filename if not provided
            step['screenshot'] = f"{args.image_dir}/{generate_image_filename(step['number'], step['title'])}"

    # Determine base path for image embedding
    base_path = args.output.parent if args.embed_images else None

    # Use Jinja2 templating if requested
    if args.jinja2:
        if not JINJA2_AVAILABLE:
            print("Error: Jinja2 not installed. Run: pip install jinja2", file=sys.stderr)
            sys.exit(2)

        template_path = args.template_dir / f"{args.template}.md"
        if not template_path.exists():
            print(f"Error: Template not found: {template_path}", file=sys.stderr)
            sys.exit(2)

        output = render_with_jinja2(template_path, data)
    # Generate based on template type (built-in generation)
    elif args.template == 'walkthrough':
        output = generate_walkthrough(
            data,
            embed_images=args.embed_images,
            base_path=base_path,
            include_toc=not args.no_toc
        )
    elif args.template == 'quick_reference':
        output = generate_quick_reference(data)
    elif args.template == 'tutorial':
        # Tutorial template is similar to walkthrough but with learning objectives
        output = generate_walkthrough(
            data,
            embed_images=args.embed_images,
            base_path=base_path,
            include_toc=not args.no_toc
        )
    else:
        print(f"Error: Unknown template: {args.template}", file=sys.stderr)
        sys.exit(2)

    # Write output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output)
    print(f"Documentation generated: {args.output}")

    # Create zip package if requested
    if args.zip:
        image_dir = args.output.parent / args.image_dir.lstrip('./')
        zip_path = create_zip_package(
            args.output.parent,
            args.output,
            image_dir
        )
        print(f"Zip package created: {zip_path}")


if __name__ == '__main__':
    main()
