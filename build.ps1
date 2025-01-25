Write-Host "Starting build process..." -ForegroundColor Green

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
python -m pip install nuitka # Nuitka'yı yükle
python -m pip install ordered-set # Nuitka için gerekli

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "installer_output") { Remove-Item -Recurse -Force "installer_output" }
if (Test-Path "FanControlCenter.build") { Remove-Item -Recurse -Force "FanControlCenter.build" }
if (Test-Path "FanControlCenter.dist") { Remove-Item -Recurse -Force "FanControlCenter.dist" }
if (Test-Path "FanControlCenter.exe") { Remove-Item -Force "FanControlCenter.exe" }

# Build the executable
Write-Host "Building executable..." -ForegroundColor Yellow
$mainPath = "Uygulama\main.py"
$version = "1.0.0"
Write-Host "Building version $version..." -ForegroundColor Green

# Nuitka build command
python -m nuitka `
    --msvc=latest `
    --windows-icon-from-ico="Uygulama/src/assets/app.ico" `
    --enable-plugin=pyside6 `
    --include-package=win32api `
    --include-package=win32event `
    --include-package=winerror `
    --include-package=wmi `
    --include-package=keyboard `
    --include-data-dir="Uygulama/src"="src" `
    --windows-company-name="Nova Web" `
    --windows-product-name="Fan Control Center" `
    --windows-file-version=$version `
    --windows-product-version=$version `
    --windows-file-description="Fan Control Center Application" `
    --windows-console-mode=disable `
    --windows-uac-admin `
    --windows-manifest-file="Uygulama/src/app.manifest" `
    --standalone `
    --onefile `
    --remove-output `
    --assume-yes-for-downloads `
    --output-filename="FanControlCenter.exe" `
    $mainPath

# Move the executable to dist folder
Write-Host "Moving files to dist folder..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "dist"
Move-Item -Force "FanControlCenter.exe" "dist/"

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