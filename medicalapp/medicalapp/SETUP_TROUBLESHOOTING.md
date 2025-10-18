# 🚀 Quick Setup Guide - Lab Facilities Feature

## ❌ Error You're Seeing

```
ModuleNotFoundError: No module named 'django'
ImportError: Couldn't import Django. Are you sure it's installed?
Did you forget to activate a virtual environment?
```

## ✅ Solution: Activate Virtual Environment

### Step 1: Navigate to Project Directory

```powershell
cd C:\Users\Sudeep\Downloads\medicalapp\medicalapp
```

### Step 2: Activate Virtual Environment

The project should have a virtual environment folder. Look for one of these:

```powershell
# If you have smartqueue_env folder:
.\smartqueue_env\Scripts\Activate.ps1

# OR if you have venv folder:
.\venv\Scripts\Activate.ps1

# OR if you have env folder:
.\env\Scripts\Activate.ps1
```

**You'll know it worked when you see** `(venv)` or `(smartqueue_env)` at the start of your prompt:

```powershell
(smartqueue_env) PS C:\Users\Sudeep\Downloads\medicalapp\medicalapp>
```

### Step 3: Verify Django is Installed

```powershell
python -c "import django; print(django.get_version())"
```

**Expected output**: Should show Django version (e.g., `5.2.7`)

### Step 4: Create Migrations

```powershell
python manage.py makemigrations patients
```

**Expected output**:
```
Migrations for 'patients':
  patients/migrations/0003_auto_XXXXXXXXX.py
    - Create model LabFacility
    - Create model LabFacilityImage
    - Create model LabFacilityReview
    - Create model LabFacilityTestPrice
```

### Step 5: Apply Migrations

```powershell
python manage.py migrate
```

**Expected output**:
```
Running migrations:
  Applying patients.0003_auto_XXXXXXXXX... OK
```

### Step 6: Create Sample Data (Optional)

```powershell
python manage.py shell < setup_lab_tests.py
```

### Step 7: Run Server

```powershell
python manage.py runserver
```

### Step 8: Access Portal

Open browser:
```
http://localhost:8000/patients/portal/
```

Click **"Lab Facilities"** tab to see the new feature!

---

## 🛠️ Troubleshooting

### Problem 1: No Virtual Environment Folder

**Create a new one:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Problem 2: Execution Policy Error

```
cannot be loaded because running scripts is disabled on this system
```

**Solution:**

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating again.

### Problem 3: Django Not Installed (Even After Activation)

**Install Django:**

```powershell
pip install django djangorestframework
```

### Problem 4: Requirements.txt Missing

**Install core packages:**

```powershell
pip install django==5.2.7 djangorestframework django-cors-headers celery redis twilio google-generativeai qrcode pillow geopy
```

---

## 📋 Complete Command Sequence

**Copy and paste these commands one by one:**

```powershell
# 1. Go to project directory
cd C:\Users\Sudeep\Downloads\medicalapp\medicalapp

# 2. Activate virtual environment (try each until one works)
.\smartqueue_env\Scripts\Activate.ps1
# OR
.\venv\Scripts\Activate.ps1

# 3. Verify Django
python -c "import django; print('Django installed:', django.get_version())"

# 4. Create migrations
python manage.py makemigrations patients

# 5. Apply migrations
python manage.py migrate

# 6. Create sample lab tests
python manage.py shell < setup_lab_tests.py

# 7. Run server
python manage.py runserver

# 8. Open browser to:
# http://localhost:8000/patients/portal/
```

---

## ✅ Success Indicators

You'll know everything is working when:

1. ✅ Virtual environment activates (shows prefix in prompt)
2. ✅ Migrations create without errors
3. ✅ Server starts: `Starting development server at http://127.0.0.1:8000/`
4. ✅ Portal loads with "Lab Facilities" tab visible
5. ✅ Clicking tab shows 3 sample labs

---

## 🆘 Still Having Issues?

### Option A: Use PowerShell Script

```powershell
.\setup_and_migrate.ps1
```

This automated script will:
- Find or create virtual environment
- Activate it
- Install dependencies
- Run migrations
- Create sample data

### Option B: Check Virtual Environment Location

```powershell
# List all folders in current directory
Get-ChildItem -Directory

# Look for folders like:
# - smartqueue_env
# - venv
# - env
# - .venv
```

### Option C: Fresh Virtual Environment

```powershell
# Create new virtual environment
python -m venv new_venv

# Activate it
.\new_venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations patients
python manage.py migrate
```

---

## 📞 Quick Help Commands

```powershell
# Check Python version
python --version

# Check pip version
pip --version

# List installed packages
pip list

# Check if Django is installed
python -c "import django"

# Check current directory
Get-Location

# List files in current directory
Get-ChildItem
```

---

## 🎯 What to Expect After Setup

Once migrations complete, you'll have:

1. **New Database Tables:**
   - `patients_labfacility`
   - `patients_labfacilityimage`
   - `patients_labfacilityreview`
   - `patients_labfacilitytestprice`

2. **New Portal Tab:**
   - "Lab Facilities" (next to "Hospitals")

3. **Sample Data:**
   - 3 diagnostic labs (Dr. Lal PathLabs, SRL, Thyrocare)
   - 27 lab tests (if setup_lab_tests.py runs)

4. **Admin Panel:**
   - Lab Facilities management
   - Custom pricing
   - Reviews

---

**Remember**: Always activate the virtual environment before running Django commands!

**Good luck!** 🚀
