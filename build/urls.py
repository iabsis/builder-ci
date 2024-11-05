from django.urls import path
from . import models, views
from sbadmin2.crud import generate_crud_urls

urlpatterns = [
    *generate_crud_urls('build', 'build', models.Build, create=False, update=False, view=True, show_filter=False),
    *generate_crud_urls('request', 'request', models.BuildRequest, show_filter=False),
    path('request/trigger/<int:pk>/', views.TiggerBuildRequestView.as_view(), name="buildrequest_trigger"),
    path('build/run/<int:pk>/', views.RunBuildView.as_view(), name="build_run"),
]