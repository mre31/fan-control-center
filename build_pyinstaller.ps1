Write-Host "Starting PyInstaller build process..." -ForegroundColor Green

# Check if Python virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Install or upgrade requirements
Write-Host "Installing requirements..." -ForegroundColor Yellow
python -m pip install -r requirements.txt
python -m pip install pyinstaller # Install PyInstaller

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "installer_output") { Remove-Item -Recurse -Force "installer_output" }
if (Test-Path "*.spec") { Remove-Item -Force "*.spec" }

# Build the executable
Write-Host "Building executable..." -ForegroundColor Yellow
$mainPath = "Uygulama\main.py"
$version = "1.0.0"
Write-Host "Building version $version..." -ForegroundColor Green

# PyInstaller build command
pyinstaller `
    --name="FanControlCenter" `
    --icon="Uygulama/src/assets/app.ico" `
    --add-data="Uygulama/src;src" `
    --hidden-import=win32api `
    --hidden-import=win32event `
    --hidden-import=winerror `
    --hidden-import=wmi `
    --hidden-import=keyboard `
    --hidden-import=PySide6 `
    --manifest="Uygulama/src/app.manifest" `
    --noconsole `
    --onefile `
    --clean `
    $mainPath

# Move the executable to dist folder (already done by PyInstaller)
Write-Host "Build completed successfully!" -ForegroundColor Green

# Check for Inno Setup Compiler
$innoSetupCompiler = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $innoSetupCompiler)) {
    $innoSetupCompiler = "${env:ProgramFiles}\Inno Setup 6\ISCC.exe"
}

if (Test-Path $innoSetupCompiler) {
    Write-Host "Creating installer..." -ForegroundColor Yellow
    
    # Create installer_output directory if it doesn't exist
    if (-not (Test-Path "installer_output")) {
        New-Item -ItemType Directory -Path "installer_output"
    }
    
    # Run Inno Setup Compiler
    & $innoSetupCompiler "installer.iss"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Installer created successfully!" -ForegroundColor Green
        Write-Host "The installer can be found in the 'installer_output' folder." -ForegroundColor Cyan
    } else {
        Write-Host "Error creating installer!" -ForegroundColor Red
    }
} else {
    Write-Host "Inno Setup not found! Please install Inno Setup 6 to create the installer." -ForegroundColor Red
    Write-Host "Download from: https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
}

# Deactivate virtual environment
deactivate 