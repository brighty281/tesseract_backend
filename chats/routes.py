from django.urls import path
from .consumers import ChatConsumer,PersonalChatConsumers

websocket_urlpatterns=[
    
    path("ws/chat/<str:room_name>/<int:id>/",ChatConsumer.as_asgi()),
    path("ws/chat/personal/<int:student_id>/<int:course_id>/<int:sender_id>/",PersonalChatConsumers.as_asgi())
]

