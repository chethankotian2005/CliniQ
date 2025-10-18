from django.urls import path
from . import views

urlpatterns = [
    path('proxy/', views.proxy_message, name='chat-proxy'),
]
