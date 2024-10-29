from django.urls import path
from . import models, views
from sbadmin2.crud import generate_crud_urls

urlpatterns = [
    *generate_crud_urls('build', 'build', models.Build, create=False, update=False, view=True),
    *generate_crud_urls('request', 'request', models.BuildRequest),
    path('build/', views.Build.as_view())
]