#!/usr/bin/env bash
#
# DocuGen Installer
# Usage: curl -fsSL https://raw.githubusercontent.com/asachs01/claudeDocugen/main/install.sh | bash
#
# Options:
#   --no-deps    Skip Python dependency installation
#   --path DIR   Install to custom directory (default: ~/.claude/skills/docugen)
#   --update     Update existing installation
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default settings
INSTALL_PATH="${HOME}/.claude/skills/docugen"
INSTALL_DEPS=true
UPDATE_MODE=false
REPO_URL="https://github.com/asachs01/claudeDocugen"
RAW_URL="https://raw.githubusercontent.com/asachs01/claudeDocugen/main"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-deps)
            INSTALL_DEPS=false
            shift
            ;;
        --path)
            INSTALL_PATH="$2"
            shift 2
            ;;
        --update)
            UPDATE_MODE=true
            shift
            ;;
        -h|--help)
            echo "DocuGen Installer"
            echo ""
            echo "Usage: curl -fsSL ${RAW_URL}/install.sh | bash -s -- [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --no-deps    Skip Python dependency installation"
            echo "  --path DIR   Install to custom directory"
            echo "  --update     Update existing installation"
            echo "  -h, --help   Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════╗"
echo "║         DocuGen Installer v1.0            ║"
echo "║   AI-Powered Documentation Generator      ║"
echo "╚═══════════════════════════════════════════╝"
echo -e "${NC}"

# Check for existing installation
if [[ -d "$INSTALL_PATH" ]] && [[ "$UPDATE_MODE" == false ]]; then
    echo -e "${YELLOW}DocuGen is already installed at ${INSTALL_PATH}${NC}"
    echo "Use --update to update, or --path to install elsewhere"
    exit 1
fi

# Check Python version
echo -e "${BLUE}[1/5]${NC} Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
    PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

    if [[ "$PYTHON_MAJOR" -ge 3 ]] && [[ "$PYTHON_MINOR" -ge 8 ]]; then
        echo -e "  ${GREEN}✓${NC} Python ${PYTHON_VERSION} found"
    else
        echo -e "  ${RED}✗${NC} Python 3.8+ required (found ${PYTHON_VERSION})"
        echo ""
        echo "Install Python 3.8+ from https://python.org or use your package manager:"
        echo "  macOS:  brew install python@3.11"
        echo "  Ubuntu: sudo apt install python3"
        exit 1
    fi
else
    echo -e "  ${RED}✗${NC} Python 3 not found"
    echo ""
    echo "Install Python 3.8+ from https://python.org or use your package manager:"
    echo "  macOS:  brew install python@3.11"
    echo "  Ubuntu: sudo apt install python3"
    exit 1
fi

# Create installation directory
echo -e "${BLUE}[2/5]${NC} Creating installation directory..."
mkdir -p "$INSTALL_PATH"
echo -e "  ${GREEN}✓${NC} Created ${INSTALL_PATH}"

# Download skill files
echo -e "${BLUE}[3/5]${NC} Downloading DocuGen skill..."

# Create subdirectories
mkdir -p "${INSTALL_PATH}/scripts"
mkdir -p "${INSTALL_PATH}/references"
mkdir -p "${INSTALL_PATH}/templates"
mkdir -p "${INSTALL_PATH}/assets"

# Download files
download_file() {
    local remote_path="$1"
    local local_path="$2"
    if curl -fsSL "${RAW_URL}/docugen/${remote_path}" -o "${INSTALL_PATH}/${local_path}"; then
        echo -e "  ${GREEN}✓${NC} ${local_path}"
    else
        echo -e "  ${RED}✗${NC} Failed to download ${remote_path}"
        exit 1
    fi
}

download_file "SKILL.md" "SKILL.md"
download_file "scripts/detect_step.py" "scripts/detect_step.py"
download_file "scripts/annotate_screenshot.py" "scripts/annotate_screenshot.py"
download_file "scripts/generate_markdown.py" "scripts/generate_markdown.py"
download_file "scripts/process_images.py" "scripts/process_images.py"
download_file "references/writing_style_guide.md" "references/writing_style_guide.md"
download_file "references/annotation_conventions.md" "references/annotation_conventions.md"
download_file "references/troubleshooting_patterns.md" "references/troubleshooting_patterns.md"
download_file "templates/walkthrough.md" "templates/walkthrough.md"
download_file "templates/quick_reference.md" "templates/quick_reference.md"
download_file "templates/tutorial.md" "templates/tutorial.md"
download_file "assets/annotation_styles.json" "assets/annotation_styles.json"

# Install Python dependencies
if [[ "$INSTALL_DEPS" == true ]]; then
    echo -e "${BLUE}[4/5]${NC} Installing Python dependencies..."
    # Use --user to avoid PEP 668 "externally managed environment" errors on macOS/Homebrew
    if python3 -m pip install --user --quiet pillow scikit-image jinja2 numpy 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} Installed: pillow, scikit-image, jinja2, numpy"
    elif python3 -m pip install --quiet pillow scikit-image jinja2 numpy 2>/dev/null; then
        # Fallback for systems without --user restriction
        echo -e "  ${GREEN}✓${NC} Installed: pillow, scikit-image, jinja2, numpy"
    else
        echo -e "  ${YELLOW}⚠${NC} Could not install dependencies automatically."
        echo "     Install manually with:"
        echo "     pip install --user pillow scikit-image jinja2 numpy"
        echo ""
        echo "     Or use a virtual environment:"
        echo "     python3 -m venv ~/.docugen-venv && source ~/.docugen-venv/bin/activate"
        echo "     pip install pillow scikit-image jinja2 numpy"
    fi
else
    echo -e "${BLUE}[4/5]${NC} Skipping dependency installation (--no-deps)"
fi

# Verify installation
echo -e "${BLUE}[5/5]${NC} Verifying installation..."
if [[ -f "${INSTALL_PATH}/SKILL.md" ]] && [[ -f "${INSTALL_PATH}/scripts/detect_step.py" ]]; then
    echo -e "  ${GREEN}✓${NC} Installation verified"
else
    echo -e "  ${RED}✗${NC} Installation verification failed"
    exit 1
fi

# Success message
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      DocuGen installed successfully!      ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════╝${NC}"
echo ""
echo -e "Installed to: ${BLUE}${INSTALL_PATH}${NC}"
echo ""
echo -e "${YELLOW}Try it now in Claude:${NC}"
echo ""
echo "  \"Document this workflow: Create a new GitHub repository"
echo "   Starting URL: https://github.com/new\""
echo ""
echo -e "Documentation: ${BLUE}https://asachs01.github.io/claudeDocugen${NC}"
echo ""
