import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET

import firebase_service
import os


@require_GET
def status(request):
    """Return simple status about Firebase initialization and credential file."""
    initialized = False
    cred_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') or os.environ.get('FIREBASE_CREDENTIALS_PATH')
    try:
        firebase_service.get_firestore_client()
        initialized = True
    except Exception:
        initialized = False

    return JsonResponse({'firebase_initialized': initialized, 'credentials_path': cred_path or ''})


@require_POST
def test_fcm(request):
    """Send a test FCM message. Expects JSON body: {"token":"...","title":"...","body":"..."}

    Returns 503 if Firebase is not initialized or credentials missing.
    """
    try:
        # check firebase initialized
        firebase_service.get_firestore_client()
    except Exception:
        return JsonResponse({'error': 'Firebase not initialized or credentials missing'}, status=503)

    try:
        payload = json.loads(request.body.decode() or '{}')
        token = payload.get('token')
        title = payload.get('title', 'Test')
        body = payload.get('body', 'Test message')
        if not token:
            return JsonResponse({'error': 'token required in body'}, status=400)

        res = firebase_service.send_fcm(token, title, body, data=payload.get('data'))
        return JsonResponse({'message_id': res})
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=500)


@require_POST
def test_firestore(request):
    """Write a test document to Firestore. Expects JSON body: {"collection":"test","doc":"docid","data":{...}}

    Returns 503 if Firebase not initialized.
    """
    try:
        client = firebase_service.get_firestore_client()
    except Exception:
        return JsonResponse({'error': 'Firebase not initialized or credentials missing'}, status=503)

    try:
        payload = json.loads(request.body.decode() or '{}')
        collection = payload.get('collection', 'test')
        doc = payload.get('doc')
        data = payload.get('data', {'hello': 'world'})
        if doc:
            ref = client.collection(collection).document(doc)
            ref.set(data)
            return JsonResponse({'status': 'ok', 'doc': doc})
        else:
            ref = client.collection(collection).add(data)
            return JsonResponse({'status': 'ok', 'doc': ref[1].id})
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=500)


@require_POST
def create_user(request):
    """Create a Firebase Auth user via Admin SDK. Expects JSON body: {"email":"...","password":"..."}

    Returns 503 if Firebase not initialized.
    """
    try:
        # ensure firebase initialized
        client = firebase_service.get_firestore_client()
    except Exception:
        return JsonResponse({'error': 'Firebase not initialized or credentials missing'}, status=503)

    try:
        payload = json.loads(request.body.decode() or '{}')
        email = payload.get('email')
        password = payload.get('password')
        if not email or not password:
            return JsonResponse({'error': 'email and password are required'}, status=400)

        from firebase_admin import auth as firebase_auth
        user = firebase_auth.create_user(email=email, password=password)
        return JsonResponse({'uid': user.uid, 'email': user.email})
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=500)
