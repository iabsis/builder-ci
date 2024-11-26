from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/logs/(?P<build_pk>\w+)/$", consumers.LogsConsumer.as_asgi()),
]
