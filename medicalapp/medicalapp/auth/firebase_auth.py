from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions

import firebase_service

User = get_user_model()


class FirebaseAuthentication(authentication.BaseAuthentication):
    """DRF authentication that accepts a Bearer Firebase ID token.

    Usage: add 'medicalapp.auth.firebase_auth.FirebaseAuthentication' to
    REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] or use it on a per-view basis.
    """

    keyword = 'Bearer'

    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).split()
        if not auth_header:
            return None

        if auth_header[0].decode().lower() != self.keyword.lower():
            return None

        if len(auth_header) == 1:
            raise exceptions.AuthenticationFailed('Invalid token header. No credentials provided.')
        if len(auth_header) > 2:
            raise exceptions.AuthenticationFailed('Invalid token header. Token string should not contain spaces.')

        id_token = auth_header[1].decode()
        try:
            decoded = firebase_service.verify_id_token(id_token)
        except Exception as exc:
            raise exceptions.AuthenticationFailed('Invalid Firebase ID token') from exc

        # firebase uid
        uid = decoded.get('uid') or decoded.get('user_id')
        if not uid:
            raise exceptions.AuthenticationFailed('Invalid token: uid missing')

        # Try finding a linked Django user by uid or by email
        firebase_uid_field = getattr(settings, 'FIREBASE_UID_FIELD', 'firebase_uid')

        user = None
        # If your user model has a firebase_uid field, try that
        if hasattr(User, firebase_uid_field):
            try:
                user = User.objects.get(**{firebase_uid_field: uid})
            except User.DoesNotExist:
                user = None

        # Next try to find by email
        email = decoded.get('email')
        if not user and email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = None

        # If still no user, create a minimal user (customize as needed). This will set username to uid.
        if not user:
            user = User.objects.create_user(username=uid, email=email or '', password=None)
            # if your model has firebase_uid field, set it
            if hasattr(user, firebase_uid_field):
                setattr(user, firebase_uid_field, uid)
                user.save()

        return (user, None)
