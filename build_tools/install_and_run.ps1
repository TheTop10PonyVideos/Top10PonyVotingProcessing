# Top 10 Pony Voting Processing - PowerShell Installer and Launcher
# This PowerShell script will run the Python installer with proper error handling

param(
    [switch]$SkipPause = $false
)

function Write-ColoredText {
    param(
        [string]$Text,
        [string]$Color = "White"
    )
    Write-Host $Text -ForegroundColor $Color
}

function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Set console title
$Host.UI.RawUI.WindowTitle = "Top 10 Pony Voting Processing - Setup"

Write-Host ""
Write-ColoredText "=====================================" "Cyan"
Write-ColoredText "Top 10 Pony Voting Processing Setup" "Cyan"
Write-ColoredText "=====================================" "Cyan"
Write-Host ""
Write-ColoredText "This will automatically install and set up everything needed:" "Yellow"
Write-ColoredText "- Git (if not installed)" "White"
Write-ColoredText "- Python 3.13.5 (if not installed)" "White"
Write-ColoredText "- Poetry (if not installed)" "White"
Write-ColoredText "- Clone/update the repository" "White"
Write-ColoredText "- Set up the virtual environment" "White"
Write-ColoredText "- Launch the application" "White"
Write-Host ""

if (-not $SkipPause) {
    Write-ColoredText "Press any key to continue..." "Green"
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    Write-Host ""
}

# Check if Python is available
$pythonFound = $false
$pythonCommands = @("python", "python3", "py")

foreach ($cmd in $pythonCommands) {
    if (Test-Command $cmd) {
        Write-ColoredText "Found Python command: $cmd" "Green"
        try {
            & $cmd build_exe.py
            $pythonFound = $true
            break
        }
        catch {
            Write-ColoredText "Failed to run with $cmd" "Red"
            continue
        }
    }
}

if (-not $pythonFound) {
    Write-Host ""
    Write-ColoredText "ERROR: Python is not installed or not in PATH" "Red"
    Write-ColoredText "Please install Python 3.13.5 from https://python.org" "Yellow"
    Write-ColoredText "Make sure to check 'Add Python to PATH' during installation" "Yellow"
    Write-Host ""
    
    # Offer to open Python download page
    $response = Read-Host "Would you like to open the Python download page? (y/n)"
    if ($response -eq "y" -or $response -eq "Y") {
        Start-Process "https://www.python.org/downloads/"
    }
    
    if (-not $SkipPause) {
        Write-ColoredText "Press any key to exit..." "Red"
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
    exit 1
}

Write-Host ""
Write-ColoredText "Setup completed!" "Green"

if (-not $SkipPause) {
    Write-ColoredText "Press any key to exit..." "Green"
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
