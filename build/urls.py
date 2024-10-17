from django.urls import path
from django.views.decorators.cache import cache_page

from . import views

urlpatterns = [
    path("build", views.Build.as_view(), name="build"),
]