import os
import logging
from typing import Optional

import firebase_admin
from firebase_admin import credentials, auth, messaging, firestore, db

logger = logging.getLogger(__name__)


def init_firebase(cred_path: Optional[str] = None, realtime_db_url: Optional[str] = None):
    """Initialize Firebase Admin SDK. Call once at startup (e.g., from manage.py or wsgi/asgi)."""
    if firebase_admin._apps:
        # already initialized
        return firebase_admin._apps

    cred_path = cred_path or os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') or os.environ.get('FIREBASE_CREDENTIALS_PATH')
    if not cred_path:
        raise RuntimeError('Firebase credentials path not set. Set GOOGLE_APPLICATION_CREDENTIALS or FIREBASE_CREDENTIALS_PATH')
    if not os.path.exists(cred_path):
        raise RuntimeError(f'Firebase credentials file not found: {cred_path}')

    cred = credentials.Certificate(cred_path)
    options = {}
    if realtime_db_url:
        options['databaseURL'] = realtime_db_url
    try:
        app = firebase_admin.initialize_app(cred, options=options)
        logger.info('Initialized Firebase app')
        return app
    except Exception as exc:
        logger.exception('Failed to initialize Firebase Admin SDK')
        raise


def verify_id_token(id_token: str):
    """Verify a Firebase ID token and return decoded token dict."""
    return auth.verify_id_token(id_token)


def send_fcm(device_token: str, title: str, body: str, data=None):
    """Send a simple FCM notification to a device token."""
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=device_token,
        data=data or {},
    )
    return messaging.send(message)


def get_firestore_client():
    return firestore.client()


def get_realtime_db():
    return db
