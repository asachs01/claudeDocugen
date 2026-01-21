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
echo "║         DocuGen Installer v1.1            ║"
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
echo -e "${BLUE}[1/6]${NC} Checking Python..."
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
fi

if [[ -n "$PYTHON_CMD" ]]; then
    PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
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
echo -e "${BLUE}[2/6]${NC} Creating installation directory..."
mkdir -p "$INSTALL_PATH"
echo -e "  ${GREEN}✓${NC} Created ${INSTALL_PATH}"

# Download skill files
echo -e "${BLUE}[3/6]${NC} Downloading DocuGen skill..."

# Create subdirectories
mkdir -p "${INSTALL_PATH}/scripts"
mkdir -p "${INSTALL_PATH}/references"
mkdir -p "${INSTALL_PATH}/templates"
mkdir -p "${INSTALL_PATH}/assets"
mkdir -p "${INSTALL_PATH}/bin"

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

# Create virtual environment and install dependencies
if [[ "$INSTALL_DEPS" == true ]]; then
    echo -e "${BLUE}[4/6]${NC} Creating virtual environment..."
    VENV_PATH="${INSTALL_PATH}/.venv"

    # Remove old venv if updating
    if [[ -d "$VENV_PATH" ]] && [[ "$UPDATE_MODE" == true ]]; then
        rm -rf "$VENV_PATH"
    fi

    if $PYTHON_CMD -m venv "$VENV_PATH"; then
        echo -e "  ${GREEN}✓${NC} Created virtual environment"
    else
        echo -e "  ${RED}✗${NC} Failed to create virtual environment"
        echo "     Make sure python3-venv is installed:"
        echo "     Ubuntu/Debian: sudo apt install python3-venv"
        exit 1
    fi

    echo -e "${BLUE}[5/6]${NC} Installing Python dependencies..."
    if "${VENV_PATH}/bin/pip" install --quiet pillow scikit-image jinja2 numpy 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} Installed: pillow, scikit-image, jinja2, numpy"
    else
        echo -e "  ${RED}✗${NC} Failed to install dependencies"
        exit 1
    fi
else
    echo -e "${BLUE}[4/6]${NC} Skipping virtual environment (--no-deps)"
    echo -e "${BLUE}[5/6]${NC} Skipping dependency installation (--no-deps)"
fi

# Create wrapper scripts in bin/
echo -e "${BLUE}[6/6]${NC} Creating wrapper scripts..."

VENV_PYTHON="${INSTALL_PATH}/.venv/bin/python"
SCRIPTS_DIR="${INSTALL_PATH}/scripts"
BIN_DIR="${INSTALL_PATH}/bin"

# Create wrapper for each script
create_wrapper() {
    local script_name="$1"
    local wrapper_name="$2"
    cat > "${BIN_DIR}/${wrapper_name}" << EOF
#!/usr/bin/env bash
exec "${VENV_PYTHON}" "${SCRIPTS_DIR}/${script_name}" "\$@"
EOF
    chmod +x "${BIN_DIR}/${wrapper_name}"
    echo -e "  ${GREEN}✓${NC} bin/${wrapper_name}"
}

create_wrapper "detect_step.py" "detect-step"
create_wrapper "annotate_screenshot.py" "annotate-screenshot"
create_wrapper "generate_markdown.py" "generate-markdown"
create_wrapper "process_images.py" "process-images"

# Verify installation
echo ""
echo -e "${BLUE}Verifying installation...${NC}"
if [[ -f "${INSTALL_PATH}/SKILL.md" ]] && [[ -x "${BIN_DIR}/detect-step" ]]; then
    # Test that the venv works
    if "${BIN_DIR}/detect-step" --help &>/dev/null || [[ $? -eq 2 ]]; then
        echo -e "  ${GREEN}✓${NC} Installation verified"
    else
        echo -e "  ${YELLOW}⚠${NC} Scripts installed but may need manual testing"
    fi
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
echo -e "Scripts available in: ${BLUE}${BIN_DIR}/${NC}"
echo "  detect-step, annotate-screenshot, generate-markdown, process-images"
echo ""
echo -e "${YELLOW}Try it now in Claude:${NC}"
echo ""
echo "  \"Document this workflow: Create a new GitHub repository"
echo "   Starting URL: https://github.com/new\""
echo ""
echo -e "Documentation: ${BLUE}https://asachs01.github.io/claudeDocugen${NC}"
echo ""
