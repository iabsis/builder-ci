from django.urls import path

from . import views

urlpatterns = [
    path("", views.FlowListView.as_view(), name="flow"),
    path("<int:pk>/", views.FlowUpdateView.as_view(), name="flow_update"),
]