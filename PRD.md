# Product Requirements Document: DocuGen Skill

**Document Version:** 1.0  
**Last Updated:** January 20, 2026  
**Author:** Aaron (WYRE Technology)  
**Status:** Draft

---

## Executive Summary

DocuGen is a Claude skill that automates the creation of step-by-step documentation, walkthroughs, and procedural guides from web-based workflows. Unlike click-capture tools like Scribe or Tango that simply record mouse actions, DocuGen leverages Claude's semantic understanding to generate documentation that explains not just *what* users click, but *why*—producing context-aware, audience-adaptive documentation suitable for training materials, knowledge bases, and technical guides.

The skill will be designed for use in Claude.ai (with computer use), Claude Code (via MCP browser integrations), and potentially the Anthropic API, making it a versatile tool for individual developers, technical writers, and organizations building documentation at scale.

---

## Problem Statement

### Current Pain Points

**1. Click-capture tools produce shallow documentation**  
Existing tools like Scribe and Tango generate text like "Click the Submit button" without context. They capture *what* happened but not *why* it matters, leaving readers without the understanding needed to troubleshoot or adapt procedures.

**2. Documentation becomes stale immediately**  
Screenshots captured today become outdated when UIs change. Existing tools offer no mechanism for intelligent updates or detecting when documentation no longer matches the application.

**3. One-size-fits-all output**  
Current tools produce a single output format regardless of audience. A quick reference for power users requires different content than a detailed walkthrough for beginners, but existing tools can't adapt.

**4. Manual effort remains high**  
Even with auto-capture, significant editing is required: rewriting generic descriptions, adding context, fixing missed steps, and formatting for different platforms.

**5. No intelligence layer**  
Existing tools can't infer missing prerequisites, anticipate failure scenarios, suggest process improvements, or answer questions about documented procedures.

### Market Opportunity

The documentation automation market is growing rapidly, with tools like Scribe raising $60M+ in funding. However, all major players have converged on the same click-capture approach, creating an opportunity for an AI-native solution that fundamentally reimagines what automated documentation can be.

---

## Vision & Goals

### Vision Statement

DocuGen transforms Claude into a documentation specialist that observes workflows, understands intent, and produces professional-quality documentation that reads like it was written by an expert technical writer who deeply understands both the application and the reader.

### Primary Goals

| Goal | Success Criteria |
|------|------------------|
| **Semantic Understanding** | Generated documentation includes contextual explanations, not just action descriptions |
| **Professional Quality** | Output meets technical writing standards (imperative verbs, consistent structure, appropriate detail level) |
| **Minimal Editing** | 80%+ of generated content usable without modification |
| **Flexible Output** | Support multiple output formats and audience levels from single capture |
| **Standalone Operation** | Produce self-contained markdown with embedded or referenced images |

### Secondary Goals

- Enable voice narration capture alongside clicks to capture the "why" behind actions
- Support batch documentation of multiple related workflows
- Provide troubleshooting section generation based on anticipated failure points
- Enable documentation templates for organizational consistency

---

## Target Users

### Primary Personas

**1. Technical Writer / Documentation Specialist**  
- Creates documentation for software products
- Needs to document dozens of procedures efficiently
- Values consistency, accuracy, and professional quality
- Wants to focus on content strategy, not screenshot management

**2. Developer / DevRel Engineer**  
- Building web applications and needs to document features
- Creates README files, tutorials, and API guides
- Prefers markdown output for version control
- Values automation and CLI/programmatic access

**3. IT Administrator / MSP Professional**  
- Documents internal processes and client-facing procedures
- Creates training materials for end users
- Needs to document workflows across multiple applications
- Values time savings and consistent output

**4. Trainer / Instructional Designer**  
- Creates learning materials for software training
- Needs multiple versions for different skill levels
- Values pedagogical structure (prerequisites, outcomes, practice)
- Wants to maintain documentation as software evolves

### Secondary Personas

- Product managers creating feature documentation
- Support teams building knowledge base articles
- Consultants documenting client systems
- Quality assurance engineers documenting test procedures

---

## User Stories

### Core Workflow

**US-1: Basic Walkthrough Generation**  
*As a developer, I want to record myself navigating a web interface so that Claude generates a step-by-step markdown guide with annotated screenshots.*

Acceptance Criteria:
- I can initiate recording with a simple command
- Each meaningful action is captured as a numbered step
- Screenshots are automatically annotated with highlights/arrows
- Output is a single markdown file with referenced images
- Steps include action descriptions and expected results

**US-2: Contextual Documentation**  
*As a technical writer, I want Claude to understand what I'm documenting so that the generated text includes relevant context, not just "click here" instructions.*

Acceptance Criteria:
- Step descriptions explain the purpose of each action
- Prerequisites are automatically identified and listed
- Related concepts or terminology are briefly explained
- Warnings about potential issues are included where appropriate

**US-3: Voice-Enhanced Capture**  
*As a trainer, I want to narrate what I'm doing while recording so that my explanations are incorporated into the documentation.*

Acceptance Criteria:
- Voice narration is transcribed and associated with relevant steps
- Narrated context is woven into step descriptions
- Option to include verbatim quotes vs. paraphrased content
- Timestamps allow re-association if needed

### Output Customization

**US-4: Audience-Adaptive Output**  
*As a documentation specialist, I want to generate different versions for different audiences from a single recording so that I don't have to record the same workflow multiple times.*

Acceptance Criteria:
- Can specify audience level (beginner, intermediate, expert)
- Beginner version includes more context and warnings
- Expert version is concise with minimal explanation
- All versions maintain accuracy and completeness

**US-5: Template-Based Output**  
*As an organization, we want documentation to follow our standard format so that all guides are consistent across the company.*

Acceptance Criteria:
- Custom templates can be provided
- Template variables are populated from captured data
- Organizational branding/headers can be included
- Style preferences (heading levels, callout formats) are respected

### Advanced Features

**US-6: Troubleshooting Generation**  
*As a support engineer, I want Claude to anticipate common issues and generate troubleshooting content so that documentation helps users recover from problems.*

Acceptance Criteria:
- Common error scenarios are identified based on workflow type
- Each potential issue has a description and resolution
- Troubleshooting section follows the procedural content
- Can specify additional known issues to include

**US-7: Multi-Workflow Documentation**  
*As a product owner, I want to document multiple related workflows and have them organized into a cohesive guide so that users have comprehensive documentation.*

Acceptance Criteria:
- Multiple recordings can be combined into one document
- Table of contents is auto-generated
- Cross-references between sections are created
- Shared prerequisites are consolidated

---

## Functional Requirements

### FR-1: Workflow Recording

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-1.1 | P0 | Initiate recording session via natural language command |
| FR-1.2 | P0 | Navigate web pages using Playwright MCP or Chrome DevTools MCP |
| FR-1.3 | P0 | Capture screenshots at each significant user action |
| FR-1.4 | P0 | Detect step boundaries using SSIM visual comparison (threshold < 0.90) |
| FR-1.5 | P1 | Track DOM changes via MutationObserver for dynamic content |
| FR-1.6 | P1 | Record element metadata (selector, text content, ARIA labels) |
| FR-1.7 | P2 | Support voice narration capture and transcription |
| FR-1.8 | P2 | Handle authentication flows (OAuth, SSO) with user credentials |

### FR-2: Screenshot Processing

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-2.1 | P0 | Capture viewport screenshots at native resolution |
| FR-2.2 | P0 | Annotate screenshots with highlight boxes around clicked elements |
| FR-2.3 | P1 | Add numbered step callouts for multi-action screenshots |
| FR-2.4 | P1 | Draw arrows pointing to target elements |
| FR-2.5 | P1 | Auto-blur detected sensitive fields (password, SSN patterns) |
| FR-2.6 | P2 | Support full-page screenshot capture |
| FR-2.7 | P2 | Crop screenshots to relevant regions |

### FR-3: Documentation Generation

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-3.1 | P0 | Generate markdown with standard walkthrough structure |
| FR-3.2 | P0 | Include contextual step descriptions (not just "click X") |
| FR-3.3 | P0 | Embed screenshots via relative file references |
| FR-3.4 | P1 | Auto-generate prerequisites section |
| FR-3.5 | P1 | Include expected results after each step |
| FR-3.6 | P1 | Support base64 image embedding option |
| FR-3.7 | P2 | Generate troubleshooting section |
| FR-3.8 | P2 | Support multiple audience-level outputs |
| FR-3.9 | P2 | Support custom template injection |

### FR-4: Output Management

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-4.1 | P0 | Save markdown and images to specified output directory |
| FR-4.2 | P0 | Use consistent, descriptive file naming |
| FR-4.3 | P1 | Generate table of contents for multi-section docs |
| FR-4.4 | P2 | Export to additional formats (HTML, PDF) via pandoc |
| FR-4.5 | P2 | Package as downloadable zip archive |

---

## Non-Functional Requirements

### NFR-1: Quality Standards

| Requirement | Target |
|-------------|--------|
| Documentation readability | Flesch-Kincaid Grade Level 7-8 |
| Accessibility compliance | WCAG 2.1 AA |
| Alt text coverage | 100% of images |
| Step length | ≤25 words per step |
| Procedure length | 7-12 steps (break longer into sub-procedures) |

### NFR-2: Performance

| Requirement | Target |
|-------------|--------|
| Step detection latency | <500ms after action |
| Screenshot capture | <200ms per capture |
| Full document generation | <30s for 10-step procedure |
| Image file size | <200KB per screenshot (compressed PNG) |

### NFR-3: Compatibility

| Environment | Support Level |
|-------------|---------------|
| Claude.ai (computer use) | Full support |
| Claude Code + Playwright MCP | Full support |
| Claude Code + Chrome DevTools MCP | Full support |
| Anthropic API (with computer use) | Future consideration |

### NFR-4: Reliability

| Requirement | Target |
|-------------|--------|
| Step detection accuracy | >95% of meaningful actions captured |
| Annotation placement | >90% correctly positioned |
| No data loss on interruption | Intermediate state recoverable |

---

## Technical Architecture

### Skill File Structure

```
docugen/
├── SKILL.md                          # Core instructions and triggering
├── scripts/
│   ├── detect_step.py                # SSIM comparison for step detection
│   ├── annotate_screenshot.py        # PIL-based annotation rendering
│   ├── generate_markdown.py          # Template-based markdown assembly
│   └── process_images.py             # Image optimization and formatting
├── references/
│   ├── writing_style_guide.md        # Technical writing standards
│   ├── annotation_conventions.md     # Visual annotation rules
│   └── troubleshooting_patterns.md   # Common issue templates
├── templates/
│   ├── walkthrough.md                # Default output template
│   ├── quick_reference.md            # Condensed format template
│   └── tutorial.md                   # Learning-focused template
└── assets/
    └── annotation_styles.json        # Color/style configuration
```

### Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        DocuGen Skill                            │
├─────────────────────────────────────────────────────────────────┤
│  SKILL.md                                                       │
│  - Workflow orchestration instructions                          │
│  - Trigger keywords and contexts                                │
│  - Progressive disclosure references                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  Recording  │    │  Processing │    │  Generation │         │
│  │   Layer     │───▶│    Layer    │───▶│    Layer    │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│        │                   │                   │                │
│        ▼                   ▼                   ▼                │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │ Playwright  │    │ detect_     │    │ generate_   │         │
│  │ MCP / CDT   │    │ step.py     │    │ markdown.py │         │
│  │ MCP         │    │             │    │             │         │
│  │             │    │ annotate_   │    │ templates/  │         │
│  │ DOM Events  │    │ screenshot  │    │ *.md        │         │
│  │ Screenshots │    │ .py         │    │             │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  references/                                                    │
│  - writing_style_guide.md (loaded during generation)            │
│  - annotation_conventions.md (loaded during processing)         │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Initiation**: User provides URL and workflow description
2. **Recording**: Claude navigates via MCP, capturing DOM events and screenshots
3. **Detection**: `detect_step.py` compares frames, identifies step boundaries
4. **Annotation**: `annotate_screenshot.py` renders highlights, arrows, callouts
5. **Analysis**: Claude analyzes captured data to understand intent and context
6. **Generation**: `generate_markdown.py` assembles output from template
7. **Enhancement**: Claude enriches with contextual explanations
8. **Output**: Final markdown and images saved to output directory

### Key Technical Decisions

| Decision | Rationale |
|----------|-----------|
| Use Playwright/CDT MCP over Computer Use | DOM access enables element identification, selectors, and metadata capture |
| SSIM threshold of 0.90 | Balances sensitivity (catches real changes) with noise rejection (ignores hover states) |
| Python scripts for image processing | Deterministic, token-efficient, pre-installed PIL available |
| Relative image references as default | Maintains markdown readability, separates concerns |
| PNG format for screenshots | Lossless compression, sharp text, transparency support |

---

## Success Metrics

### Quantitative Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Steps captured accurately | >95% | Manual review of sample workflows |
| Usable without editing | >80% of content | User survey / editing time tracking |
| Time savings vs. manual | >70% reduction | Comparative timing study |
| Output quality score | 4.5/5 user rating | Post-generation feedback |
| Accessibility compliance | 100% WCAG AA | Automated testing |

### Qualitative Metrics

- Documentation reads naturally, not robotically
- Context explanations are helpful, not generic
- Screenshots are clear and appropriately annotated
- Structure matches professional documentation standards
- Output integrates smoothly into existing documentation systems

---

## Scope Definition

### In Scope (v1.0)

- Web-based workflow documentation
- Single-session recording
- Markdown output with images
- Basic annotation (boxes, arrows, numbers)
- Contextual step descriptions
- Prerequisites and expected results
- Single audience level per generation
- Claude.ai and Claude Code support

### Out of Scope (v1.0)

- Desktop application capture (future version)
- Video output
- Real-time collaboration
- Documentation hosting/publishing
- Version control integration
- Automatic update detection
- Multi-language output
- API-only access (no Claude interface)

### Future Considerations (v2.0+)

- Desktop capture via OS-level screenshot APIs
- Diff-based documentation updates
- Integration with docs platforms (Notion, Confluence, GitBook)
- Team templates and brand management
- Automated testing of documented procedures
- Translation and localization support

---

## Dependencies & Constraints

### Technical Dependencies

| Dependency | Type | Notes |
|------------|------|-------|
| Playwright MCP or Chrome DevTools MCP | Required | Browser automation and DOM access |
| PIL/Pillow | Required | Screenshot annotation |
| scikit-image | Required | SSIM calculation |
| Python 3.x | Required | Script execution |
| File system access | Required | Image and markdown storage |

### Constraints

| Constraint | Impact | Mitigation |
|------------|--------|------------|
| No network access in API environment | Can't fetch external resources | Bundle all dependencies in skill |
| Context window limits | Large workflows consume tokens | Progressive disclosure, external storage |
| Screenshot resolution (1568px max in Computer Use) | Lower quality captures | Use MCP integrations for full resolution |
| Authentication handling | Can't store credentials | User provides credentials per session |

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| SSIM miscalibration causes missed steps | Medium | High | Configurable threshold, manual step addition |
| DOM changes break selectors | Medium | Medium | Fallback to visual descriptions |
| Large workflows exceed context | Medium | High | Chunked processing, external state |
| Annotation placement errors | Low | Low | Visual verification step |

---

## Development Roadmap

### Phase 1: Foundation (Weeks 1-2)

- [ ] Initialize skill structure using skill-creator patterns
- [ ] Implement basic Playwright MCP integration
- [ ] Create `detect_step.py` with SSIM comparison
- [ ] Create `annotate_screenshot.py` with basic box/arrow rendering
- [ ] Build minimal `SKILL.md` with core workflow instructions
- [ ] Test with simple 5-step workflow

### Phase 2: Core Generation (Weeks 3-4)

- [ ] Implement `generate_markdown.py` with template support
- [ ] Create default `walkthrough.md` template
- [ ] Add contextual description generation to SKILL.md
- [ ] Implement prerequisites detection logic
- [ ] Add expected results generation
- [ ] Create `writing_style_guide.md` reference

### Phase 3: Polish & Quality (Weeks 5-6)

- [ ] Add numbered callouts and multi-annotation support
- [ ] Implement sensitive data detection and blurring
- [ ] Add image optimization and compression
- [ ] Create `quick_reference.md` template
- [ ] Implement audience-level adaptation
- [ ] Comprehensive testing with diverse workflows

### Phase 4: Advanced Features (Weeks 7-8)

- [ ] Add troubleshooting section generation
- [ ] Implement voice narration support (if feasible)
- [ ] Add custom template support
- [ ] Create `tutorial.md` template
- [ ] Package and validate skill
- [ ] Documentation and examples

---

## Open Questions

1. **Voice capture feasibility**: Can voice narration be captured and transcribed within the skill environment, or does this require external tooling?

2. **Authentication handling**: What's the best UX for workflows requiring login? Should users pre-authenticate, or should the skill guide them through it?

3. **MCP availability**: Should the skill gracefully degrade to Computer Use if MCP integrations aren't available, or require MCP as hard dependency?

4. **State persistence**: For interrupted recordings, how should partial state be stored and recovered?

5. **Custom annotation styles**: How much visual customization should be exposed to users (colors, shapes, fonts)?

6. **Multi-step screenshots**: When should multiple actions be combined into a single annotated screenshot vs. separate images?

---

## Appendix A: Competitive Feature Comparison

| Feature | Scribe | Tango | Loom | DocuGen (Planned) |
|---------|--------|-------|------|-------------------|
| Click capture | ✓ | ✓ | Via video | ✓ |
| Auto screenshots | ✓ | ✓ | Frames | ✓ |
| Annotations | ✓ | ✓ | Limited | ✓ |
| Contextual descriptions | Limited AI | Basic | Transcript | **Full semantic** |
| Audience adaptation | ✗ | ✗ | ✗ | **✓** |
| Prerequisites detection | ✗ | ✗ | ✗ | **✓** |
| Troubleshooting generation | ✗ | ✗ | ✗ | **✓** |
| Voice integration | ✗ | ✗ | ✓ | **Planned** |
| Markdown output | Export | Export | ✗ | **Native** |
| Self-hosted / offline | ✗ | ✗ | ✗ | **✓** |
| Pricing | $12-23/user/mo | Free tier + paid | $12.50/user/mo | **Free (skill)** |

---

## Appendix B: Sample Output Structure

```markdown
# Creating a New Project in Acme Dashboard

## Overview

This guide walks through creating a new project in the Acme Dashboard, 
including setting up basic configuration and inviting team members.

## Prerequisites

- Acme Dashboard account with Admin or Project Creator role
- Project name and description prepared
- Email addresses of team members to invite (optional)

## Steps

### Step 1: Access the Projects section

From the main dashboard, click **Projects** in the left navigation menu 
to view your existing projects and access creation options.

![Navigate to Projects section](./images/step-01-projects-nav.png)

**Expected result:** The Projects list page displays with a "New Project" 
button in the upper right.

### Step 2: Initiate project creation

Click the **New Project** button to open the project creation wizard. 
This begins a guided setup process.

![Click New Project button](./images/step-02-new-project-btn.png)

**Expected result:** The "Create New Project" modal appears with the 
first step (Basic Information) active.

[... additional steps ...]

## Troubleshooting

**"New Project" button is disabled**  
This indicates insufficient permissions. Contact your organization admin 
to request Project Creator role access.

**Project name already exists error**  
Project names must be unique within your organization. Try adding a 
date suffix or department prefix to differentiate.
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-20 | Aaron | Initial draft |
