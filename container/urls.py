from django.urls import path

from . import views

urlpatterns = [
    path("", views.ContainerListView.as_view(), name="container"),
    path("create/", views.ContainerCreateView.as_view(), name="container_create"),
    path("<int:pk>/", views.ContainerUpdateView.as_view(), name="container_update"),
    path("delete/<int:pk>/", views.ContainerDeleteView.as_view(), name="container_delete")
]