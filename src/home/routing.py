from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/log_entries/', consumers.LogEntryConsumer.as_asgi())
]