import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DJANGO_PROJECT_DIR = ROOT_DIR / "medicalapp" / "medicalapp"

# Ensure Django apps are importable in Vercel's Python runtime.
sys.path.insert(0, str(DJANGO_PROJECT_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartqueue.settings")

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
