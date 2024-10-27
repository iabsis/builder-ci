from django.urls import path

from . import views

urlpatterns = [
    path("", views.ContainerListView.as_view(), name="container"),
    path("<int:pk>/", views.ContainerUpdateView.as_view(), name="container"),
]