from django.urls import path
from app.consumers import ChatConsumer
from . import consumers

websocket_urlpatterns=[
    path('ws/chat/<int:job_id>/',consumers.ChatConsumer.as_asgi()),
]