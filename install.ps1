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
    Write-ColorOutput "+===========================================+" "Cyan"
    Write-ColorOutput "|         DocuGen Installer v1.1            |" "Cyan"
    Write-ColorOutput "|   AI-Powered Documentation Generator      |" "Cyan"
    Write-ColorOutput "+===========================================+" "Cyan"
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
    Write-ColorOutput "[1/6] Checking Python..." "Cyan"

    $pythonCmd = $null
    try {
        $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
        if (-not $pythonCmd) {
            $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
        }

        if ($pythonCmd) {
            $version = & $pythonCmd.Source -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
            $major, $minor = $version -split '\.'

            if ([int]$major -ge 3 -and [int]$minor -ge 8) {
                Write-ColorOutput "  + Python $version found" "Green"
                return $pythonCmd.Source
            } else {
                Write-ColorOutput "  x Python 3.8+ required (found $version)" "Red"
                Write-Host ""
                Write-Host "Install Python 3.8+ from https://python.org"
                Write-Host "Or use: winget install Python.Python.3.11"
                exit 1
            }
        } else {
            throw "Python not found"
        }
    } catch {
        Write-ColorOutput "  x Python 3 not found" "Red"
        Write-Host ""
        Write-Host "Install Python 3.8+ from https://python.org"
        Write-Host "Or use: winget install Python.Python.3.11"
        exit 1
    }
}

function New-InstallDirectory {
    Write-ColorOutput "[2/6] Creating installation directory..." "Cyan"

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
    New-Item -ItemType Directory -Path "$Path\bin" -Force | Out-Null

    Write-ColorOutput "  + Created $Path" "Green"
}

function Get-SkillFile {
    param([string]$RemotePath, [string]$LocalPath)

    $url = "$RawUrl/docugen/$RemotePath"
    $destination = "$Path\$LocalPath"

    try {
        Invoke-WebRequest -Uri $url -OutFile $destination -UseBasicParsing
        Write-ColorOutput "  + $LocalPath" "Green"
    } catch {
        Write-ColorOutput "  x Failed to download $RemotePath" "Red"
        exit 1
    }
}

function Install-SkillFiles {
    Write-ColorOutput "[3/6] Downloading DocuGen skill..." "Cyan"

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

function New-VirtualEnvironment {
    param([string]$PythonPath)

    if ($NoDeps) {
        Write-ColorOutput "[4/6] Skipping virtual environment (-NoDeps)" "Cyan"
        Write-ColorOutput "[5/6] Skipping dependency installation (-NoDeps)" "Cyan"
        return $null
    }

    Write-ColorOutput "[4/6] Creating virtual environment..." "Cyan"

    $venvPath = "$Path\.venv"

    # Remove old venv if updating
    if ((Test-Path $venvPath) -and $Update) {
        Remove-Item -Recurse -Force $venvPath
    }

    try {
        & $PythonPath -m venv $venvPath
        Write-ColorOutput "  + Created virtual environment" "Green"
    } catch {
        Write-ColorOutput "  x Failed to create virtual environment" "Red"
        exit 1
    }

    Write-ColorOutput "[5/6] Installing Python dependencies..." "Cyan"

    $pipPath = "$venvPath\Scripts\pip.exe"
    try {
        & $pipPath install --quiet pillow scikit-image jinja2 numpy 2>$null
        Write-ColorOutput "  + Installed: pillow, scikit-image, jinja2, numpy" "Green"
    } catch {
        Write-ColorOutput "  x Failed to install dependencies" "Red"
        exit 1
    }

    return $venvPath
}

function New-WrapperScripts {
    param([string]$VenvPath)

    Write-ColorOutput "[6/6] Creating wrapper scripts..." "Cyan"

    $venvPython = "$VenvPath\Scripts\python.exe"
    $scriptsDir = "$Path\scripts"
    $binDir = "$Path\bin"

    # Create wrapper batch files for each script
    $scripts = @{
        "detect_step.py" = "detect-step"
        "annotate_screenshot.py" = "annotate-screenshot"
        "generate_markdown.py" = "generate-markdown"
        "process_images.py" = "process-images"
    }

    foreach ($script in $scripts.GetEnumerator()) {
        $wrapperPath = "$binDir\$($script.Value).cmd"
        $content = "@echo off`r`n`"$venvPython`" `"$scriptsDir\$($script.Key)`" %*"
        Set-Content -Path $wrapperPath -Value $content
        Write-ColorOutput "  + bin\$($script.Value).cmd" "Green"
    }
}

function Test-Installation {
    Write-Host ""
    Write-ColorOutput "Verifying installation..." "Cyan"

    if ((Test-Path "$Path\SKILL.md") -and (Test-Path "$Path\bin\detect-step.cmd")) {
        Write-ColorOutput "  + Installation verified" "Green"
    } else {
        Write-ColorOutput "  x Installation verification failed" "Red"
        exit 1
    }
}

function Show-Success {
    Write-Host ""
    Write-ColorOutput "+===========================================+" "Green"
    Write-ColorOutput "|      DocuGen installed successfully!      |" "Green"
    Write-ColorOutput "+===========================================+" "Green"
    Write-Host ""
    Write-Host "Installed to: " -NoNewline
    Write-ColorOutput $Path "Cyan"
    Write-Host ""
    Write-Host "Scripts available in: " -NoNewline
    Write-ColorOutput "$Path\bin\" "Cyan"
    Write-Host "  detect-step, annotate-screenshot, generate-markdown, process-images"
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
$venvPath = New-VirtualEnvironment -PythonPath $pythonPath
if ($venvPath) {
    New-WrapperScripts -VenvPath $venvPath
} else {
    Write-ColorOutput "[6/6] Skipping wrapper scripts (-NoDeps)" "Cyan"
}
Test-Installation
Show-Success
