import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DJANGO_PROJECT_DIR = ROOT_DIR / "medicalapp" / "medicalapp"

_MIGRATIONS_APPLIED = False

# Ensure Django apps are importable in Vercel's Python runtime.
sys.path.insert(0, str(DJANGO_PROJECT_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartqueue.settings")

if os.getenv("VERCEL") and not _MIGRATIONS_APPLIED:
	# Keep serverless DB schema in sync across deployments/environments.
	import django
	from django.core.management import call_command
	from django.db import connections

	django.setup()

	try:
		connection = connections["default"]
		existing_tables = set(connection.introspection.table_names())
		required_tables = {"django_migrations", "patients_department"}

		if not required_tables.issubset(existing_tables):
			call_command("migrate", interactive=False, run_syncdb=True, verbosity=0)
	except Exception:
		# If introspection fails, attempt migration as a safe fallback.
		call_command("migrate", interactive=False, run_syncdb=True, verbosity=0)

	_MIGRATIONS_APPLIED = True

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
