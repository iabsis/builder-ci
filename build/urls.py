from django.urls import path
from . import models, views
from sbadmin2.crud import generate_crud_urls

urlpatterns = [
    *generate_crud_urls('', 'build', models.Build, create=False, update=False, view=True, show_filter=False),
    *generate_crud_urls('request', 'request', models.BuildRequest),
    path('request/trigger/<int:pk>/', views.TriggerBuildRequestView.as_view(), name="buildrequest_trigger"),
    path('run/<int:pk>/', views.RunBuildView.as_view(), name="build_run"),
]