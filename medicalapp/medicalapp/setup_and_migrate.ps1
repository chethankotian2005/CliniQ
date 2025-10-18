# CliniQ Lab Facilities Setup Script for Windows PowerShell
# Run this script to activate virtual environment and create migrations

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CliniQ Lab Facilities Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if we're in the right directory
Write-Host "Step 1: Checking directory..." -ForegroundColor Yellow
$currentPath = Get-Location
Write-Host "Current directory: $currentPath" -ForegroundColor White

# Step 2: Check for virtual environment
Write-Host "`nStep 2: Checking virtual environment..." -ForegroundColor Yellow

$venvPaths = @(
    "smartqueue_env",
    "venv",
    "env",
    ".venv"
)

$venvFound = $null
foreach ($venv in $venvPaths) {
    if (Test-Path $venv) {
        $venvFound = $venv
        Write-Host "Found virtual environment: $venv" -ForegroundColor Green
        break
    }
}

if (-not $venvFound) {
    Write-Host "No virtual environment found. Creating one..." -ForegroundColor Yellow
    Write-Host "Creating virtual environment 'venv'..." -ForegroundColor White
    python -m venv venv
    $venvFound = "venv"
    Write-Host "Virtual environment created!" -ForegroundColor Green
}

# Step 3: Activate virtual environment
Write-Host "`nStep 3: Activating virtual environment..." -ForegroundColor Yellow
$activateScript = Join-Path $venvFound "Scripts\Activate.ps1"

if (Test-Path $activateScript) {
    Write-Host "Activating: $activateScript" -ForegroundColor White
    & $activateScript
    Write-Host "Virtual environment activated!" -ForegroundColor Green
} else {
    Write-Host "ERROR: Activation script not found at $activateScript" -ForegroundColor Red
    exit 1
}

# Step 4: Check Django installation
Write-Host "`nStep 4: Checking Django installation..." -ForegroundColor Yellow
$djangoInstalled = python -c "import django; print(django.get_version())" 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "Django is installed (version: $djangoInstalled)" -ForegroundColor Green
} else {
    Write-Host "Django not found. Installing requirements..." -ForegroundColor Yellow
    if (Test-Path "requirements.txt") {
        pip install -r requirements.txt
        Write-Host "Requirements installed!" -ForegroundColor Green
    } else {
        Write-Host "Installing Django..." -ForegroundColor White
        pip install django djangorestframework
        Write-Host "Django installed!" -ForegroundColor Green
    }
}

# Step 5: Create migrations for lab facilities
Write-Host "`nStep 5: Creating migrations for lab facilities..." -ForegroundColor Yellow
Write-Host "Running: python manage.py makemigrations patients" -ForegroundColor White
python manage.py makemigrations patients

if ($LASTEXITCODE -eq 0) {
    Write-Host "Migrations created successfully!" -ForegroundColor Green
} else {
    Write-Host "ERROR: Failed to create migrations" -ForegroundColor Red
    exit 1
}

# Step 6: Apply migrations
Write-Host "`nStep 6: Applying migrations..." -ForegroundColor Yellow
Write-Host "Running: python manage.py migrate" -ForegroundColor White
python manage.py migrate

if ($LASTEXITCODE -eq 0) {
    Write-Host "Migrations applied successfully!" -ForegroundColor Green
} else {
    Write-Host "ERROR: Failed to apply migrations" -ForegroundColor Red
    exit 1
}

# Step 7: Create sample lab facilities
Write-Host "`nStep 7: Creating sample lab facilities..." -ForegroundColor Yellow
Write-Host "Running: python manage.py shell < setup_lab_tests.py" -ForegroundColor White

if (Test-Path "setup_lab_tests.py") {
    Get-Content setup_lab_tests.py | python manage.py shell
    Write-Host "Sample lab tests created!" -ForegroundColor Green
} else {
    Write-Host "setup_lab_tests.py not found. Skipping..." -ForegroundColor Yellow
}

# Success!
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Run the development server:" -ForegroundColor White
Write-Host "   python manage.py runserver" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Access the portal:" -ForegroundColor White
Write-Host "   http://localhost:8000/patients/portal/" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Click 'Lab Facilities' tab to see the new feature!" -ForegroundColor White
Write-Host ""
