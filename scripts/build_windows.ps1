# PowerShell build and packaging script for Algorithm Arena on Windows
param (
    [switch]$OneFile = $false
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "         Algorithm Arena - Windows Packaging Script        " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$VenvPython = ".\.venv\Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Error "Virtual environment not found at .\.venv. Please create it first."
    exit 1
}

# 1. Ensure PyInstaller is installed
Write-Host "[1/4] Checking PyInstaller in virtual environment..." -ForegroundColor Yellow
& $VenvPython -m pip install pyinstaller

# 2. Prepare PyInstaller command
Write-Host "[2/4] Configuring build parameters..." -ForegroundColor Yellow
$BuildArgs = @(
    "-m", "PyInstaller",
    "--name=AlgorithmArena",
    "--noconsole",
    "--clean",
    "--add-data=content;content"
)

if ($OneFile) {
    $BuildArgs += "--onefile"
    Write-Host "Mode: Standalone Single Executable (--onefile)" -ForegroundColor Green
} else {
    $BuildArgs += "--onedir"
    Write-Host "Mode: Directory Bundle (--onedir)" -ForegroundColor Green
}

$BuildArgs += "main.py"

# 3. Execute PyInstaller
Write-Host "[3/4] Running PyInstaller..." -ForegroundColor Yellow
& $VenvPython @BuildArgs

# 4. Check Output
Write-Host "[4/4] Verifying build output..." -ForegroundColor Yellow
if ($OneFile) {
    $TargetExe = "dist\AlgorithmArena.exe"
} else {
    $TargetExe = "dist\AlgorithmArena\AlgorithmArena.exe"
}

if (Test-Path $TargetExe) {
    Write-Host "==========================================================" -ForegroundColor Green
    Write-Host " BUILD SUCCESSFUL! Native Windows executable generated at:" -ForegroundColor Green
    Write-Host " $TargetExe" -ForegroundColor White
    Write-Host "==========================================================" -ForegroundColor Green
} else {
    Write-Error "Build completed, but executable was not found at expected path: $TargetExe"
}
