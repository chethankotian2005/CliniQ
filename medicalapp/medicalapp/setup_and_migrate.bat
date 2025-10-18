@echo off
REM CliniQ Lab Facilities Setup - Windows Batch File
REM Double-click this file to run setup

echo ========================================
echo CliniQ Lab Facilities Setup
echo ========================================
echo.

REM Step 1: Check virtual environment
echo [1/6] Checking virtual environment...

if exist "smartqueue_env" (
    echo Found: smartqueue_env
    call smartqueue_env\Scripts\activate.bat
    goto :migrate
)

if exist "venv" (
    echo Found: venv
    call venv\Scripts\activate.bat
    goto :migrate
)

if exist "env" (
    echo Found: env
    call env\Scripts\activate.bat
    goto :migrate
)

REM No venv found, create one
echo No virtual environment found. Creating one...
python -m venv venv
call venv\Scripts\activate.bat

REM Install requirements
echo [2/6] Installing requirements...
if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    echo Installing Django...
    pip install django djangorestframework
)

:migrate
REM Create migrations
echo.
echo [3/6] Creating migrations...
python manage.py makemigrations patients

if %errorlevel% neq 0 (
    echo ERROR: Failed to create migrations
    pause
    exit /b 1
)

REM Apply migrations
echo.
echo [4/6] Applying migrations...
python manage.py migrate

if %errorlevel% neq 0 (
    echo ERROR: Failed to apply migrations
    pause
    exit /b 1
)

REM Create sample data
echo.
echo [5/6] Creating sample lab tests...
if exist "setup_lab_tests.py" (
    python manage.py shell < setup_lab_tests.py
) else (
    echo setup_lab_tests.py not found. Skipping...
)

REM Success
echo.
echo [6/6] Setup complete!
echo.
echo ========================================
echo SUCCESS!
echo ========================================
echo.
echo Next steps:
echo 1. Run server: python manage.py runserver
echo 2. Open: http://localhost:8000/patients/portal/
echo 3. Click "Lab Facilities" tab
echo.
pause
