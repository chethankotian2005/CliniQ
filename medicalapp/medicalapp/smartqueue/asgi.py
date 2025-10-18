"""
ASGI config for smartqueue project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartqueue.settings')

django_asgi_app = get_asgi_application()

from notifications import routing

# Initialize Firebase Admin SDK if credentials are present. This is safe: it will not
# prevent the application from starting if credentials are missing or invalid.
try:
    import firebase_service
    import os

    cred = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') or os.environ.get('FIREBASE_CREDENTIALS_PATH')
    realtime_db = os.environ.get('FIREBASE_REALTIME_DB_URL')
    if cred:
        try:
            firebase_service.init_firebase(cred_path=cred, realtime_db_url=realtime_db)
        except Exception:
            # don't crash the app if Firebase initialization fails; log and continue
            import logging
            logging.getLogger(__name__).exception('Firebase initialization failed, continuing without Firebase')
    else:
        # no credentials set; skip Firebase init
        pass
except Exception:
    # if import fails for any reason, don't block ASGI app startup
    import logging
    logging.getLogger(__name__).exception('Failed to import firebase_service; skipping Firebase initialization')

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})
