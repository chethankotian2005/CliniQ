#!/usr/bin/env python
"""
Environment Diagnostic Script
Run this to see what's wrong with your Python environment
"""
import sys
import os

print("=" * 60)
print("PYTHON ENVIRONMENT DIAGNOSTIC")
print("=" * 60)

# Check Python version
print(f"\n1. Python Version: {sys.version}")
print(f"   Python Executable: {sys.executable}")

# Check if in virtual environment
print(f"\n2. Virtual Environment Status:")
if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
    print("   ✅ ACTIVATED - Virtual environment is active")
    print(f"   Virtual env path: {sys.prefix}")
else:
    print("   ❌ NOT ACTIVATED - No virtual environment active")
    print("   You're using system Python")

# Check Django availability
print(f"\n3. Django Status:")
try:
    import django
    print(f"   ✅ FOUND - Django version {django.get_version()}")
    print(f"   Django location: {django.__file__}")
except ImportError:
    print("   ❌ NOT FOUND - Django is not installed in current Python environment")
    print("   This is why 'python manage.py' commands fail!")

# Check sys.path
print(f"\n4. Python Module Search Paths:")
for i, path in enumerate(sys.path[:5], 1):
    print(f"   {i}. {path}")
if len(sys.path) > 5:
    print(f"   ... and {len(sys.path) - 5} more paths")

# Check for virtual environment folders
print(f"\n5. Virtual Environment Folders in Current Directory:")
venv_names = ['smartqueue_env', 'venv', 'env', '.venv']
current_dir = os.getcwd()
print(f"   Searching in: {current_dir}")
found_venvs = []
for venv_name in venv_names:
    venv_path = os.path.join(current_dir, venv_name)
    if os.path.exists(venv_path):
        print(f"   ✅ Found: {venv_name}")
        found_venvs.append(venv_name)
        # Check if Django is in this venv
        django_path = os.path.join(venv_path, 'Lib', 'site-packages', 'django')
        if os.path.exists(django_path):
            print(f"      └─ Django IS installed in this venv")
        else:
            print(f"      └─ Django NOT found in this venv")
    else:
        print(f"   ❌ Not found: {venv_name}")

print("\n" + "=" * 60)
print("DIAGNOSIS SUMMARY")
print("=" * 60)

if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
    try:
        import django
        print("✅ Everything is fine! Virtual env is active and Django is available.")
        print("   You can run: python manage.py makemigrations")
    except ImportError:
        print("⚠️  Virtual env is active but Django is missing.")
        print("   Solution: pip install -r requirements.txt")
else:
    if found_venvs:
        print(f"❌ Problem: Virtual environment exists but NOT activated!")
        print(f"   Found venv(s): {', '.join(found_venvs)}")
        print(f"\n   SOLUTION - Run this command:")
        print(f"   .\\{found_venvs[0]}\\Scripts\\Activate.ps1")
    else:
        print("❌ Problem: No virtual environment found!")
        print("   SOLUTION - Create one:")
        print("   python -m venv venv")
        print("   .\\venv\\Scripts\\Activate.ps1")
        print("   pip install -r requirements.txt")

print("=" * 60)
