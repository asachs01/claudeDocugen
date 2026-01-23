# Product Requirements Document: DocuGen Desktop Capture Enhancement

**Document Version:** 1.0  
**Last Updated:** January 21, 2026  
**Author:** Aaron (WYRE Technology)  
**Status:** Draft  
**Parent Document:** DocuGen Skill PRD v1.0

---

## Executive Summary

This PRD defines the enhancement of DocuGen to support desktop application documentation alongside its existing web workflow capabilities. The enhancement adds cross-platform screenshot capture, platform-specific UI element identification, and eventually full-motion video recording—transforming DocuGen from a web-only tool into a comprehensive documentation solution for any software workflow.

The enhancement follows a phased approach:
- **v2.0**: Visual-only desktop capture with Claude vision analysis
- **v2.5**: Windows and macOS accessibility API integration for precise element identification
- **v3.0**: Full-motion video recording with intelligent frame extraction

---

## Problem Statement

### Current Limitation

DocuGen v1.x only documents web-based workflows via Playwright MCP. Users documenting desktop applications (Windows admin tools, macOS utilities, cross-platform software like VS Code, Office applications) cannot use DocuGen and must resort to manual documentation or competing tools.

### User Pain Points

1. **Platform fragmentation**: IT administrators and trainers work with both web and desktop applications daily but need different tools for each
2. **Manual desktop documentation**: Without automation, desktop documentation requires manual screenshots, cropping, annotation, and writing—the exact problems DocuGen solves for web
3. **Inconsistent output**: Using different tools for web vs desktop creates inconsistent documentation styles
4. **Training material gaps**: MSP customers need documentation for desktop workflows (Windows Server, AD tools, VMware consoles) as much as web interfaces

### Market Opportunity

Competitors like Scribe and Tango offer desktop capture via browser extensions with varying quality. An AI-native desktop solution that understands UI context (not just click coordinates) would provide significant differentiation, particularly for technical documentation use cases.

---

## Goals & Success Criteria

### Primary Goals

| Goal | Success Criteria |
|------|------------------|
| **Cross-platform capture** | Screenshots work on Windows, macOS, and Linux without code changes |
| **Unified experience** | Same "Document this workflow" command works for web and desktop |
| **Quality parity** | Desktop documentation quality matches web output |
| **Minimal friction** | Users can start documenting in <30 seconds |

### Secondary Goals

| Goal | Success Criteria |
|------|------------------|
| **Windows excellence** | Precise element identification via UI Automation on Windows |
| **Graceful degradation** | Visual-only mode works when accessibility APIs unavailable |
| **Future-proof architecture** | Clean path to video recording in v3.0 |

### Non-Goals (This Release)

- Linux accessibility API integration (visual-only for now)
- Mobile device capture
- Remote desktop/VM capture
- Real-time streaming documentation

---

## User Stories

### Core Desktop Capture

**US-D1: Basic Desktop Walkthrough**  
*As an IT administrator, I want to document a Windows Server configuration process so that I can train new team members without screen-sharing.*

Acceptance Criteria:
- I can specify "desktop" mode when starting documentation
- Screenshots capture the full screen or specific window
- Steps are detected based on visual changes (SSIM)
- Output is markdown with annotated screenshots
- Works without installing additional software beyond DocuGen

**US-D2: Window-Specific Capture**  
*As a technical writer, I want to capture only a specific application window so that my documentation isn't cluttered with other desktop content.*

Acceptance Criteria:
- I can select a target window by title or application name
- Only the selected window is captured (not full screen)
- Window title is included in documentation metadata
- If window is moved/resized, capture adjusts automatically

**US-D3: Multi-Application Workflow**  
*As a trainer, I want to document a workflow that spans multiple applications (e.g., copying from Excel to a web form) so that learners see the complete process.*

Acceptance Criteria:
- Can capture across application boundaries
- Application context switches are noted in documentation
- Screenshots show whichever application is active
- Final documentation clearly indicates application transitions

### Platform-Specific Features

**US-D4: Windows Element Identification**  
*As a documentation specialist on Windows, I want precise identification of UI elements so that annotations point exactly to buttons and fields, not approximate locations.*

Acceptance Criteria:
- Clicked elements are identified by name and control type
- Annotation boxes match exact element bounds
- Element metadata (automation ID, control type) available for technical docs
- Works with standard Windows applications (Office, Settings, Admin tools)

**US-D5: macOS Accessibility Integration**  
*As a Mac user, I want DocuGen to use macOS accessibility features so that element identification is accurate when I've granted permission.*

Acceptance Criteria:
- DocuGen detects if Accessibility permission is granted
- If granted, uses Apple Accessibility API for element identification
- If not granted, falls back to visual-only mode gracefully
- Clear instructions for granting permission if needed

**US-D6: Visual-Only Fallback**  
*As a Linux user, I want DocuGen to work even without full accessibility support so that I can still generate documentation.*

Acceptance Criteria:
- Screenshot capture works on all Linux desktop environments
- Claude vision analyzes screenshots to identify likely click targets
- Annotations are placed based on visual analysis
- Documentation quality is acceptable (even if not pixel-perfect)

### Capture Triggers

**US-D7: Manual Trigger Mode**  
*As a user, I want to control exactly when screenshots are taken so that I can capture the precise moments I need.*

Acceptance Criteria:
- Hotkey triggers screenshot capture (configurable)
- Visual/audio feedback confirms capture
- Can add notes/narration at capture time
- Manual mode works alongside automatic detection

**US-D8: Automatic Step Detection**  
*As a user documenting a complex workflow, I want DocuGen to automatically detect when significant UI changes occur so that I don't have to manually trigger every capture.*

Acceptance Criteria:
- SSIM-based detection identifies significant visual changes
- Threshold is configurable (default 0.90)
- Debounce prevents duplicate captures (300ms minimum)
- Can be combined with manual triggers

### Output & Integration

**US-D9: Unified Web+Desktop Documentation**  
*As a product owner, I want to combine web and desktop steps in a single document so that users see the complete workflow regardless of platform.*

Acceptance Criteria:
- Single document can contain both web and desktop sections
- Consistent formatting across capture types
- Clear indication of which steps are web vs desktop
- Table of contents handles mixed content

**US-D10: Cross-Platform Consistency**  
*As a documentation team lead, I want the same workflow documented on Windows and Mac to produce similar output so that our docs are consistent.*

Acceptance Criteria:
- Same template structure regardless of capture platform
- Element naming conventions are consistent where possible
- Visual annotation style is identical
- Markdown output is platform-agnostic

---

## Functional Requirements

### FR-D1: Screenshot Capture

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-D1.1 | P0 | Capture full screen on Windows, macOS, Linux |
| FR-D1.2 | P0 | Capture specific monitor in multi-monitor setup |
| FR-D1.3 | P0 | Capture specific window by title or process |
| FR-D1.4 | P1 | Capture active/focused window automatically |
| FR-D1.5 | P1 | Handle high-DPI/Retina displays correctly |
| FR-D1.6 | P2 | Capture specific rectangular region |
| FR-D1.7 | P2 | Exclude cursor from capture (optional) |

### FR-D2: Platform Detection & Routing

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-D2.1 | P0 | Detect operating system at runtime |
| FR-D2.2 | P0 | Route to appropriate capture backend |
| FR-D2.3 | P1 | Detect accessibility API availability |
| FR-D2.4 | P1 | Fall back to visual mode gracefully |
| FR-D2.5 | P2 | Report platform capabilities to user |

### FR-D3: Windows Accessibility (v2.5)

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-D3.1 | P0 | Initialize UI Automation connection |
| FR-D3.2 | P0 | Get element at screen coordinates |
| FR-D3.3 | P0 | Extract element name, type, bounds |
| FR-D3.4 | P1 | Walk UI tree for focused application |
| FR-D3.5 | P1 | Track focus changes across elements |
| FR-D3.6 | P2 | Get element automation ID for technical docs |
| FR-D3.7 | P2 | Detect and handle Chrome/Edge accessibility mode |

### FR-D4: macOS Accessibility (v2.5)

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-D4.1 | P0 | Check Accessibility permission status |
| FR-D4.2 | P0 | Initialize Apple Accessibility API connection |
| FR-D4.3 | P0 | Get element at screen coordinates |
| FR-D4.4 | P1 | Extract AX attributes (role, title, position, size) |
| FR-D4.5 | P1 | Provide clear permission instructions |
| FR-D4.6 | P2 | Handle permission request workflow |

### FR-D5: Visual Analysis Fallback

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-D5.1 | P0 | Analyze screenshot with Claude vision |
| FR-D5.2 | P0 | Identify likely UI elements (buttons, fields, menus) |
| FR-D5.3 | P1 | Estimate element bounds for annotation |
| FR-D5.4 | P1 | Generate element descriptions from visual context |
| FR-D5.5 | P2 | Confidence scoring for element identification |

### FR-D6: Capture Triggers

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-D6.1 | P0 | Manual trigger via command/instruction |
| FR-D6.2 | P1 | Automatic SSIM-based step detection |
| FR-D6.3 | P1 | Configurable SSIM threshold |
| FR-D6.4 | P2 | Hotkey trigger (platform-specific) |
| FR-D6.5 | P2 | Interval-based capture mode |
| FR-D6.6 | P2 | Click-event trigger (where detectable) |

### FR-D7: Window Management

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-D7.1 | P0 | List available windows |
| FR-D7.2 | P0 | Select window by title (exact/partial match) |
| FR-D7.3 | P1 | Select window by process name |
| FR-D7.4 | P1 | Track window position/size changes |
| FR-D7.5 | P2 | Handle window minimize/restore |
| FR-D7.6 | P2 | Focus/bring window to front |

### FR-D8: Video Recording (v3.0)

| Requirement | Priority | Description |
|-------------|----------|-------------|
| FR-D8.1 | P0 | Record screen to video file (MP4) |
| FR-D8.2 | P0 | Cross-platform recording (FFmpeg) |
| FR-D8.3 | P1 | Record specific window only |
| FR-D8.4 | P1 | Extract frames at intervals |
| FR-D8.5 | P1 | Intelligent frame extraction (motion-based) |
| FR-D8.6 | P2 | Audio capture (narration) |
| FR-D8.7 | P2 | Export to animated GIF |

---

## Non-Functional Requirements

### NFR-D1: Performance

| Requirement | Target |
|-------------|--------|
| Screenshot capture latency | <50ms (mss target: ~12ms) |
| Accessibility query latency | <100ms per element |
| Visual analysis (Claude) | <2s per screenshot |
| Memory footprint | <100MB additional |
| Video recording frame rate | 30fps minimum |

### NFR-D2: Compatibility

| Platform | Capture | Accessibility | Video |
|----------|---------|---------------|-------|
| Windows 10/11 | Full | Full (UI Automation) | Full |
| macOS 12+ | Full | Full (with permission) | Full |
| Ubuntu 22.04+ | Full | Visual-only | Full |
| Other Linux | Best effort | Visual-only | Best effort |

### NFR-D3: Reliability

| Requirement | Target |
|-------------|--------|
| Screenshot success rate | >99% |
| Accessibility query success | >95% (when available) |
| Visual fallback accuracy | >80% element identification |
| Graceful degradation | 100% (never crash on unsupported platform) |

### NFR-D4: Security & Privacy

| Requirement | Description |
|-------------|-------------|
| No persistent permissions | Don't require admin/root for basic capture |
| Sensitive data detection | Auto-blur password fields (where detectable) |
| Permission transparency | Clear indication of what permissions are used |
| No data exfiltration | Screenshots processed locally, not uploaded without consent |

---

## Technical Architecture

### Enhanced Skill Structure

```
docugen/
├── SKILL.md                              # Updated with desktop triggers
├── scripts/
│   ├── detect_step.py                    # SSIM (unchanged)
│   ├── annotate_screenshot.py            # PIL annotation (unchanged)
│   ├── generate_markdown.py              # Template assembly (unchanged)
│   ├── process_images.py                 # Image optimization (unchanged)
│   │
│   ├── # NEW: Desktop capture modules
│   ├── desktop_capture.py                # mss-based screenshot capture
│   ├── window_manager.py                 # Cross-platform window enumeration
│   ├── platform_router.py                # OS detection and capability routing
│   │
│   ├── # NEW: Accessibility modules (v2.5)
│   ├── windows_accessibility.py          # pywinauto UI Automation
│   ├── macos_accessibility.py            # atomac/atomacos integration
│   ├── element_mapper.py                 # Map accessibility to screenshot coords
│   │
│   └── # NEW: Video recording (v3.0)
│       ├── video_recorder.py             # FFmpeg-based recording
│       └── frame_extractor.py            # Intelligent frame extraction
│
├── references/
│   ├── writing_style_guide.md            # (unchanged)
│   ├── annotation_conventions.md         # (unchanged)
│   ├── troubleshooting_patterns.md       # (unchanged)
│   │
│   └── # NEW: Desktop references
│       ├── desktop_setup.md              # Platform-specific setup instructions
│       └── accessibility_permissions.md  # Permission grant guides
│
├── templates/
│   ├── walkthrough.md                    # (unchanged, works for both)
│   ├── quick_reference.md                # (unchanged)
│   └── tutorial.md                       # (unchanged)
│
└── assets/
    └── annotation_styles.json            # (unchanged)
```

### Component Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DocuGen v2.5 Architecture                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                        SKILL.md                                  │    │
│  │  • Unified trigger detection (web + desktop keywords)           │    │
│  │  • Mode selection (auto-detect or explicit)                     │    │
│  │  • Workflow orchestration                                       │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│                                    ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                     platform_router.py                           │    │
│  │  • OS detection (Windows/macOS/Linux)                           │    │
│  │  • Capability detection (accessibility available?)              │    │
│  │  • Route to appropriate backend                                 │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                    │                              │                      │
│         ┌─────────┴─────────┐          ┌────────┴────────┐              │
│         ▼                   ▼          ▼                 ▼              │
│  ┌─────────────┐    ┌─────────────┐   ┌─────────────────────────┐      │
│  │ Web Mode    │    │Desktop Mode │   │   Accessibility Layer   │      │
│  │             │    │             │   │                         │      │
│  │ Playwright  │    │ mss         │   │ Windows: pywinauto     │      │
│  │ MCP         │    │ screenshots │   │ macOS: atomac          │      │
│  │             │    │             │   │ Linux: (visual only)   │      │
│  └─────────────┘    └─────────────┘   └─────────────────────────┘      │
│         │                   │                      │                    │
│         └─────────┬─────────┴──────────────────────┘                    │
│                   ▼                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    Shared Processing Pipeline                    │    │
│  │                                                                  │    │
│  │  detect_step.py ──► annotate_screenshot.py ──► generate_md.py   │    │
│  │       (SSIM)            (PIL)                   (Templates)      │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│                                    ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                          Output                                  │    │
│  │              documentation.md + images/ + metadata               │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Data Flow: Desktop Capture Session

```
User: "Document this desktop workflow: Configure Windows Firewall"
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. INITIALIZATION                                                        │
│    • platform_router.py detects Windows                                 │
│    • Checks UI Automation availability → available                      │
│    • Initializes pywinauto Desktop(backend="uia")                       │
│    • Initializes mss for screenshots                                    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 2. WINDOW TARGETING                                                      │
│    • window_manager.py lists available windows                          │
│    • User/Claude selects "Windows Defender Firewall"                    │
│    • Window handle acquired, bounds tracked                             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 3. CAPTURE LOOP                                                          │
│                                                                          │
│    For each action:                                                      │
│    ┌────────────────────────────────────────────────────────────────┐   │
│    │ a. Capture screenshot (mss) → step-N-before.png                │   │
│    │ b. User performs action (click "Advanced settings")            │   │
│    │ c. Get element at click point (pywinauto)                      │   │
│    │    → {name: "Advanced settings", type: "Hyperlink", bounds: ...}│   │
│    │ d. Capture screenshot (mss) → step-N-after.png                 │   │
│    │ e. Compare SSIM(before, after) → 0.73 (significant)            │   │
│    │ f. Record step: {action, element, before_img, after_img}       │   │
│    └────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│    Repeat until user signals completion                                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 4. PROCESSING                                                            │
│    • annotate_screenshot.py adds highlight boxes at element bounds      │
│    • process_images.py optimizes/compresses                             │
│    • Claude generates contextual descriptions                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 5. GENERATION                                                            │
│    • generate_markdown.py assembles from template                       │
│    • Output: configure-windows-firewall.md + images/                    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## SKILL.md Trigger Updates

### Current Triggers (Web)
```
document workflow, create walkthrough, generate tutorial, 
capture how-to, step-by-step guide
```

### Enhanced Triggers (Web + Desktop)
```yaml
description: >
  AI-powered documentation generator for web and desktop workflows.
  Captures screenshots, identifies UI elements, and generates professional
  markdown documentation with annotated images.
  
  Use for WEB workflows when: Playwright MCP available, URL provided,
  browser-based application
  
  Use for DESKTOP workflows when: documenting Windows/macOS/Linux applications,
  desktop software, admin tools, native applications, system settings
  
  Trigger phrases: document workflow, create walkthrough, generate tutorial,
  capture how-to, step-by-step guide, document this process, 
  create documentation for [app name], capture desktop workflow,
  document Windows/macOS/Linux procedure
```

### Mode Detection Logic

```python
def detect_mode(user_request: str, context: dict) -> str:
    """Determine whether to use web or desktop capture mode."""
    
    # Explicit desktop indicators
    desktop_keywords = [
        "desktop", "windows", "macos", "linux", "native app",
        "application", "software", "admin tool", "system settings",
        "file explorer", "terminal", "command prompt", "powershell"
    ]
    
    # Explicit web indicators
    web_keywords = [
        "website", "web app", "browser", "url", "http", 
        "chrome", "firefox", "edge", "safari"
    ]
    
    request_lower = user_request.lower()
    
    # Check for explicit mode
    if any(kw in request_lower for kw in desktop_keywords):
        return "desktop"
    if any(kw in request_lower for kw in web_keywords):
        return "web"
    
    # Check context
    if context.get("url_provided"):
        return "web"
    if context.get("playwright_available"):
        return "web"  # Default to web if Playwright is available
    
    # Default to desktop if no web context
    return "desktop"
```

---

## Dependencies

### Required (All Platforms)

```
# Core capture
mss>=9.0.0                    # Cross-platform screenshots
Pillow>=10.0.0                # Image processing
scikit-image>=0.21.0          # SSIM calculation

# Already in DocuGen
# (no changes to existing dependencies)
```

### Optional (Platform-Specific)

```
# Windows accessibility (v2.5)
pywinauto>=0.6.8              # UI Automation
comtypes>=1.1.10              # COM interface (pywinauto dependency)

# macOS accessibility (v2.5)
atomacos>=2.0.0               # Apple Accessibility API
# or atomac>=2.0.0
pyobjc-framework-Cocoa        # macOS framework bindings
pyobjc-framework-Quartz       # Screen capture support

# Video recording (v3.0)
# FFmpeg (system installation, not pip)
opencv-python>=4.8.0          # Frame extraction
```

### Dependency Installation Strategy

```python
# platform_router.py - Graceful dependency handling

def get_accessibility_backend():
    """Get appropriate accessibility backend or None."""
    system = platform.system()
    
    if system == "Windows":
        try:
            from pywinauto import Desktop
            return WindowsAccessibility()
        except ImportError:
            logger.warning("pywinauto not installed. Install with: pip install pywinauto")
            return None
    
    elif system == "Darwin":
        try:
            import atomacos
            return MacOSAccessibility()
        except ImportError:
            logger.warning("atomacos not installed. Install with: pip install atomacos")
            return None
    
    # Linux: no accessibility backend currently
    return None
```

---

## Implementation Roadmap

### Phase 1: Visual-Only Desktop Capture (v2.0)

**Duration**: 2-3 weeks  
**Goal**: Desktop documentation works on all platforms via visual capture

#### Week 1: Core Capture Infrastructure

- [ ] Create `desktop_capture.py` with mss integration
- [ ] Create `window_manager.py` for cross-platform window listing
- [ ] Create `platform_router.py` for OS detection
- [ ] Update SKILL.md with desktop triggers
- [ ] Test basic capture on Windows, macOS, Linux

#### Week 2: Integration & Polish

- [ ] Integrate desktop capture with existing SSIM step detection
- [ ] Add Claude vision analysis for element identification
- [ ] Update `annotate_screenshot.py` for visual-estimated bounds
- [ ] Create `references/desktop_setup.md` with setup instructions
- [ ] End-to-end testing: document a 10-step desktop workflow

#### Week 3: Documentation & Release

- [ ] Update docugen documentation site with desktop mode
- [ ] Create example outputs for desktop workflows
- [ ] Package and validate enhanced skill
- [ ] Release v2.0

**Deliverables:**
- DocuGen captures desktop screenshots on all platforms
- Claude vision identifies UI elements from screenshots
- Annotations placed based on visual analysis
- Single unified workflow for web and desktop

---

### Phase 2: Windows Accessibility Integration (v2.5)

**Duration**: 4-5 weeks  
**Goal**: Precise element identification on Windows

#### Week 4-5: pywinauto Integration

- [ ] Create `windows_accessibility.py` with UI Automation
- [ ] Implement `get_element_at_point(x, y)`
- [ ] Implement `get_focused_element()`
- [ ] Implement UI tree walking for application context
- [ ] Create `element_mapper.py` to map bounds to screenshot coords

#### Week 6: Enhanced Annotation

- [ ] Update annotation pipeline to use exact element bounds
- [ ] Add control type to element metadata
- [ ] Handle edge cases (minimized windows, off-screen elements)
- [ ] Test with common Windows applications:
  - [ ] Windows Settings
  - [ ] File Explorer
  - [ ] Microsoft Office (Word, Excel)
  - [ ] Administrative Tools (MMC, Event Viewer)
  - [ ] VS Code / Electron apps

#### Week 7: Fallback & Robustness

- [ ] Implement graceful fallback when accessibility fails
- [ ] Add timeout handling for slow UI Automation queries
- [ ] Handle applications that don't expose accessibility
- [ ] Chrome/Edge accessibility flag detection

#### Week 8: Release

- [ ] Integration testing on Windows 10 and 11
- [ ] Performance benchmarking
- [ ] Documentation updates
- [ ] Release v2.5

**Deliverables:**
- Pixel-perfect element identification on Windows
- Exact annotation bounds from UI Automation
- Graceful fallback to visual mode
- Works with standard Windows applications

---

### Phase 3: macOS Accessibility Integration (v2.5.1)

**Duration**: 2-3 weeks  
**Goal**: Accessibility support on macOS with user permission

#### Week 9: atomac Integration

- [ ] Create `macos_accessibility.py` with atomac/atomacos
- [ ] Implement permission check logic
- [ ] Implement element query by coordinates
- [ ] Map AX attributes to element metadata

#### Week 10: Permission Handling

- [ ] Create clear permission request messaging
- [ ] Create `references/accessibility_permissions.md`
- [ ] Implement permission-denied fallback
- [ ] Test with common macOS applications:
  - [ ] System Preferences
  - [ ] Finder
  - [ ] TextEdit
  - [ ] Safari

#### Week 11: Release

- [ ] Integration testing on macOS 12+
- [ ] Documentation updates
- [ ] Release v2.5.1

**Deliverables:**
- Accessibility integration on macOS (when permitted)
- Clear permission instructions
- Graceful fallback when permission denied

---

### Phase 4: Video Recording (v3.0)

**Duration**: 4-6 weeks  
**Goal**: Full-motion capture with intelligent frame extraction

#### Week 12-13: FFmpeg Integration

- [ ] Create `video_recorder.py` with FFmpeg subprocess
- [ ] Implement cross-platform recording commands
- [ ] Add start/stop recording controls
- [ ] Handle video file management

#### Week 14-15: Frame Extraction

- [ ] Create `frame_extractor.py`
- [ ] Implement interval-based extraction
- [ ] Implement motion-based intelligent extraction
- [ ] Integrate extracted frames with existing pipeline

#### Week 16: Advanced Features

- [ ] Audio capture for narration
- [ ] Animated GIF export option
- [ ] Video timestamp to documentation mapping
- [ ] Integration testing

#### Week 17: Release

- [ ] Full pipeline testing
- [ ] Documentation and examples
- [ ] Release v3.0

**Deliverables:**
- Full-motion screen recording
- Intelligent frame extraction for step detection
- Optional audio narration support
- Animated GIF export

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| pywinauto not available in Claude environment | Medium | High | Document as optional dependency; visual mode always works |
| macOS permission complexity confuses users | Medium | Medium | Clear documentation; fallback to visual mode |
| SSIM miscalibration on desktop (different visual patterns) | Medium | Medium | Configurable threshold; tune for desktop content |
| Accessibility APIs slow/unreliable | Low | Medium | Timeout handling; async queries; caching |
| FFmpeg not available on target system | Medium | Medium | Document installation; defer to v3.0 |
| Multi-monitor coordinate mapping errors | Medium | Low | Test extensively; use primary monitor as default |

---

## Success Metrics

### v2.0 (Visual-Only)

| Metric | Target |
|--------|--------|
| Screenshot capture success rate | >99% |
| Cross-platform coverage | Windows, macOS, Linux |
| Element identification accuracy (Claude vision) | >70% |
| Time to document 10-step desktop workflow | <8 minutes |
| User satisfaction (usable without editing) | >70% |

### v2.5 (Windows Accessibility)

| Metric | Target |
|--------|--------|
| Element identification accuracy (Windows) | >95% |
| Annotation placement accuracy (Windows) | >95% |
| Time to document 10-step Windows workflow | <5 minutes |
| User satisfaction (usable without editing) | >85% |

### v3.0 (Video Recording)

| Metric | Target |
|--------|--------|
| Recording works on all platforms | >95% |
| Frame extraction identifies correct steps | >90% |
| GIF export quality acceptable | >80% user approval |

---

## Open Questions

1. **Hotkey support**: Should we implement system-wide hotkeys for manual capture triggers? This requires a background process and platform-specific implementations.

2. **Capture indicator**: Should there be a visual indicator (overlay, sound) when a screenshot is captured in desktop mode?

3. **Window focus**: Should DocuGen automatically focus/raise the target window before capture?

4. **Multi-window workflows**: How should we handle workflows that span multiple windows (e.g., drag-and-drop between apps)?

5. **Claude Code context**: In Claude Code, should desktop capture use MCP or direct script execution?

6. **Dependency bundling**: Should optional dependencies (pywinauto, atomac) be:
   - Bundled in skill package (larger download)
   - Installed on-demand (requires network)
   - Documented as user prerequisites

---

## Appendix A: Platform-Specific Screenshot Commands

### mss (Recommended)

```python
from mss import mss

with mss() as sct:
    # All monitors
    sct.shot()  # Saves to monitor-1.png, monitor-2.png, etc.
    
    # Specific monitor
    sct.shot(mon=2)  # Second monitor
    
    # Custom region
    region = {"top": 100, "left": 100, "width": 800, "height": 600}
    sct.grab(region)
    
    # Full screenshot as PIL Image
    screenshot = sct.grab(sct.monitors[0])  # All monitors combined
```

### Window-Specific Capture

```python
# Windows
import win32gui
import win32ui
import win32con

def capture_window_windows(hwnd):
    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bot - top
    
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)
    saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
    
    # Convert to PIL
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    im = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
    
    return im

# macOS
import Quartz

def capture_window_macos(window_id):
    image = Quartz.CGWindowListCreateImage(
        Quartz.CGRectNull,
        Quartz.kCGWindowListOptionIncludingWindow,
        window_id,
        Quartz.kCGWindowImageBoundsIgnoreFraming
    )
    return image  # Convert to PIL as needed
```

---

## Appendix B: Sample Desktop Output

```markdown
# Configure Windows Defender Firewall

## Overview

This guide walks through configuring Windows Defender Firewall to allow
a custom application through the firewall.

## Prerequisites

- Windows 10 or Windows 11
- Administrator access
- Application executable path known

## Steps

### Step 1: Open Windows Security

Press the **Windows key** and type "Windows Security", then click the
**Windows Security** app to open it.

![Step 1: Open Windows Security](./images/step-01-windows-security.png)

**Expected result:** Windows Security dashboard opens showing protection
areas.

### Step 2: Navigate to Firewall settings

Click **Firewall & network protection** in the left sidebar to access
firewall configuration options.

![Step 2: Firewall settings](./images/step-02-firewall-settings.png)

**Expected result:** Firewall status for Domain, Private, and Public
networks is displayed.

### Step 3: Open advanced settings

Scroll down and click **Advanced settings** to open Windows Defender
Firewall with Advanced Security.

![Step 3: Advanced settings](./images/step-03-advanced-settings.png)

**Expected result:** Windows Defender Firewall with Advanced Security
MMC console opens.

[... additional steps ...]

## Troubleshooting

**"Advanced settings" link not visible**  
Ensure you are logged in with an Administrator account. Standard users
cannot access advanced firewall settings.

**Application still blocked after rule creation**  
Verify the rule is enabled and applies to the correct network profile
(Domain/Private/Public).
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-21 | Aaron | Initial draft |
