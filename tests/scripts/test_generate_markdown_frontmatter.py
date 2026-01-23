"""Tests for generate_markdown.py frontmatter generation."""

import unittest

from docugen.scripts.generate_markdown import generate_frontmatter, generate_walkthrough


class TestGenerateFrontmatter(unittest.TestCase):
    """Tests for YAML frontmatter generation."""

    def test_basic_frontmatter(self):
        data = {"title": "My Workflow", "steps": []}
        result = generate_frontmatter(data)

        self.assertTrue(result.startswith("---"))
        self.assertTrue(result.endswith("---"))
        self.assertIn('title: "My Workflow"', result)
        self.assertIn("generator: DocuGen", result)
        self.assertIn("steps: 0", result)

    def test_includes_mode_and_platform(self):
        data = {
            "title": "Test",
            "mode": "desktop",
            "platform": {"os": "macos"},
            "steps": [{}, {}],
        }
        result = generate_frontmatter(data)

        self.assertIn("mode: desktop", result)
        self.assertIn("platform: macos", result)
        self.assertIn("steps: 2", result)

    def test_includes_app_name(self):
        data = {
            "title": "Test",
            "app_name": "System Settings",
            "steps": [],
        }
        result = generate_frontmatter(data)
        self.assertIn('application: "System Settings"', result)

    def test_includes_description(self):
        data = {
            "title": "Test",
            "description": "How to configure settings",
            "steps": [],
        }
        result = generate_frontmatter(data)
        self.assertIn('description: "How to configure settings"', result)

    def test_escapes_quotes_in_description(self):
        data = {
            "title": "Test",
            "description": 'Click "Save" button',
            "steps": [],
        }
        result = generate_frontmatter(data)
        self.assertIn('description: "Click \\"Save\\" button"', result)

    def test_includes_tags(self):
        data = {
            "title": "Test",
            "tags": ["tutorial", "macos"],
            "steps": [],
        }
        result = generate_frontmatter(data)
        self.assertIn("tags: [tutorial, macos]", result)


class TestWalkthroughFrontmatter(unittest.TestCase):
    """Tests that generate_walkthrough respects include_frontmatter flag."""

    def test_no_frontmatter_by_default(self):
        data = {"title": "Test", "steps": []}
        result = generate_walkthrough(data)
        self.assertFalse(result.startswith("---"))

    def test_frontmatter_when_requested(self):
        data = {"title": "Test", "steps": []}
        result = generate_walkthrough(data, include_frontmatter=True)
        self.assertTrue(result.startswith("---"))
        self.assertIn('title: "Test"', result)
        # Title should still appear as H1
        self.assertIn("# Test", result)


if __name__ == "__main__":
    unittest.main()
