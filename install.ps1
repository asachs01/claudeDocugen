#Requires -Version 5.1
<#
.SYNOPSIS
    DocuGen Installer for Windows
.DESCRIPTION
    Installs DocuGen, an AI-powered documentation generator for web workflows.
.PARAMETER NoDeps
    Skip Python dependency installation
.PARAMETER Path
    Install to custom directory (default: ~/.claude/skills/docugen)
.PARAMETER Update
    Update existing installation
.EXAMPLE
    irm https://raw.githubusercontent.com/asachs01/claudeDocugen/main/install.ps1 | iex
.EXAMPLE
    .\install.ps1 -Path "C:\Tools\docugen" -NoDeps
#>

param(
    [switch]$NoDeps,
    [string]$Path = "$env:USERPROFILE\.claude\skills\docugen",
    [switch]$Update,
    [switch]$Help
)

$ErrorActionPreference = "Stop"

# Configuration
$RepoUrl = "https://github.com/asachs01/claudeDocugen"
$RawUrl = "https://raw.githubusercontent.com/asachs01/claudeDocugen/main"

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Show-Banner {
    Write-Host ""
    Write-ColorOutput "╔═══════════════════════════════════════════╗" "Cyan"
    Write-ColorOutput "║         DocuGen Installer v1.0            ║" "Cyan"
    Write-ColorOutput "║   AI-Powered Documentation Generator      ║" "Cyan"
    Write-ColorOutput "╚═══════════════════════════════════════════╝" "Cyan"
    Write-Host ""
}

function Show-Help {
    Write-Host "DocuGen Installer for Windows"
    Write-Host ""
    Write-Host "Usage: irm $RawUrl/install.ps1 | iex"
    Write-Host "   or: .\install.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -NoDeps     Skip Python dependency installation"
    Write-Host "  -Path DIR   Install to custom directory"
    Write-Host "  -Update     Update existing installation"
    Write-Host "  -Help       Show this help message"
    exit 0
}

function Test-PythonVersion {
    Write-ColorOutput "[1/5] Checking Python..." "Cyan"

    try {
        $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
        if (-not $pythonCmd) {
            $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
        }

        if ($pythonCmd) {
            $version = & $pythonCmd.Source -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
            $major, $minor = $version -split '\.'

            if ([int]$major -ge 3 -and [int]$minor -ge 8) {
                Write-ColorOutput "  ✓ Python $version found" "Green"
                return $pythonCmd.Source
            } else {
                Write-ColorOutput "  ✗ Python 3.8+ required (found $version)" "Red"
                Write-Host ""
                Write-Host "Install Python 3.8+ from https://python.org"
                Write-Host "Or use: winget install Python.Python.3.11"
                exit 1
            }
        } else {
            throw "Python not found"
        }
    } catch {
        Write-ColorOutput "  ✗ Python 3 not found" "Red"
        Write-Host ""
        Write-Host "Install Python 3.8+ from https://python.org"
        Write-Host "Or use: winget install Python.Python.3.11"
        exit 1
    }
}

function New-InstallDirectory {
    Write-ColorOutput "[2/5] Creating installation directory..." "Cyan"

    if ((Test-Path $Path) -and -not $Update) {
        Write-ColorOutput "DocuGen is already installed at $Path" "Yellow"
        Write-Host "Use -Update to update, or -Path to install elsewhere"
        exit 1
    }

    New-Item -ItemType Directory -Path $Path -Force | Out-Null
    New-Item -ItemType Directory -Path "$Path\scripts" -Force | Out-Null
    New-Item -ItemType Directory -Path "$Path\references" -Force | Out-Null
    New-Item -ItemType Directory -Path "$Path\templates" -Force | Out-Null
    New-Item -ItemType Directory -Path "$Path\assets" -Force | Out-Null

    Write-ColorOutput "  ✓ Created $Path" "Green"
}

function Get-SkillFile {
    param([string]$RemotePath, [string]$LocalPath)

    $url = "$RawUrl/docugen/$RemotePath"
    $destination = "$Path\$LocalPath"

    try {
        Invoke-WebRequest -Uri $url -OutFile $destination -UseBasicParsing
        Write-ColorOutput "  ✓ $LocalPath" "Green"
    } catch {
        Write-ColorOutput "  ✗ Failed to download $RemotePath" "Red"
        exit 1
    }
}

function Install-SkillFiles {
    Write-ColorOutput "[3/5] Downloading DocuGen skill..." "Cyan"

    Get-SkillFile "SKILL.md" "SKILL.md"
    Get-SkillFile "scripts/detect_step.py" "scripts\detect_step.py"
    Get-SkillFile "scripts/annotate_screenshot.py" "scripts\annotate_screenshot.py"
    Get-SkillFile "scripts/generate_markdown.py" "scripts\generate_markdown.py"
    Get-SkillFile "scripts/process_images.py" "scripts\process_images.py"
    Get-SkillFile "references/writing_style_guide.md" "references\writing_style_guide.md"
    Get-SkillFile "references/annotation_conventions.md" "references\annotation_conventions.md"
    Get-SkillFile "references/troubleshooting_patterns.md" "references\troubleshooting_patterns.md"
    Get-SkillFile "templates/walkthrough.md" "templates\walkthrough.md"
    Get-SkillFile "templates/quick_reference.md" "templates\quick_reference.md"
    Get-SkillFile "templates/tutorial.md" "templates\tutorial.md"
    Get-SkillFile "assets/annotation_styles.json" "assets\annotation_styles.json"
}

function Install-PythonDependencies {
    param([string]$PythonPath)

    if ($NoDeps) {
        Write-ColorOutput "[4/5] Skipping dependency installation (-NoDeps)" "Cyan"
        return
    }

    Write-ColorOutput "[4/5] Installing Python dependencies..." "Cyan"

    # Try --user first (handles PEP 668 restrictions), then fallback to system
    $installed = $false
    try {
        $result = & $PythonPath -m pip install --user --quiet pillow scikit-image jinja2 numpy 2>&1
        if ($LASTEXITCODE -eq 0) {
            $installed = $true
        }
    } catch {}

    if (-not $installed) {
        try {
            $result = & $PythonPath -m pip install --quiet pillow scikit-image jinja2 numpy 2>&1
            if ($LASTEXITCODE -eq 0) {
                $installed = $true
            }
        } catch {}
    }

    if ($installed) {
        Write-ColorOutput "  ✓ Installed: pillow, scikit-image, jinja2, numpy" "Green"
    } else {
        Write-ColorOutput "  ⚠ Could not install dependencies automatically." "Yellow"
        Write-Host "     Install manually with:"
        Write-Host "     pip install --user pillow scikit-image jinja2 numpy"
        Write-Host ""
        Write-Host "     Or use a virtual environment:"
        Write-Host "     python -m venv $env:USERPROFILE\.docugen-venv"
        Write-Host "     $env:USERPROFILE\.docugen-venv\Scripts\Activate.ps1"
        Write-Host "     pip install pillow scikit-image jinja2 numpy"
    }
}

function Test-Installation {
    Write-ColorOutput "[5/5] Verifying installation..." "Cyan"

    if ((Test-Path "$Path\SKILL.md") -and (Test-Path "$Path\scripts\detect_step.py")) {
        Write-ColorOutput "  ✓ Installation verified" "Green"
    } else {
        Write-ColorOutput "  ✗ Installation verification failed" "Red"
        exit 1
    }
}

function Show-Success {
    Write-Host ""
    Write-ColorOutput "╔═══════════════════════════════════════════╗" "Green"
    Write-ColorOutput "║      DocuGen installed successfully!      ║" "Green"
    Write-ColorOutput "╚═══════════════════════════════════════════╝" "Green"
    Write-Host ""
    Write-Host "Installed to: " -NoNewline
    Write-ColorOutput $Path "Cyan"
    Write-Host ""
    Write-ColorOutput "Try it now in Claude:" "Yellow"
    Write-Host ""
    Write-Host '  "Document this workflow: Create a new GitHub repository'
    Write-Host '   Starting URL: https://github.com/new"'
    Write-Host ""
    Write-Host "Documentation: " -NoNewline
    Write-ColorOutput "https://asachs01.github.io/claudeDocugen" "Cyan"
    Write-Host ""
}

# Main execution
if ($Help) {
    Show-Help
}

Show-Banner
$pythonPath = Test-PythonVersion
New-InstallDirectory
Install-SkillFiles
Install-PythonDependencies -PythonPath $pythonPath
Test-Installation
Show-Success
