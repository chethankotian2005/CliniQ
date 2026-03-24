import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DJANGO_PROJECT_DIR = ROOT_DIR / "medicalapp" / "medicalapp"

# Ensure Django apps are importable in Vercel's Python runtime.
sys.path.insert(0, str(DJANGO_PROJECT_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartqueue.settings")

if os.getenv("VERCEL") and not os.getenv("DATABASE_URL"):
	# Serverless fallback for demos without external Postgres.
	import django
	from django.core.management import call_command

	django.setup()
	call_command("migrate", interactive=False, run_syncdb=True, verbosity=0)

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
