from django.urls import re_path, path
from llm_chat_v1 import consumers
websocket_urlpatterns = [
    path("test_socket/", consumers.ChatConsumer.as_asgi())
]