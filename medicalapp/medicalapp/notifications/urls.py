from django.urls import path
from . import api

urlpatterns = [
    path('api/test/fcm/', api.test_fcm, name='test_fcm'),
    path('api/test/firestore/', api.test_firestore, name='test_firestore'),
    path('api/status/', api.status, name='status'),
    path('api/create-user/', api.create_user, name='create_user'),
]
