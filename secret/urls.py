from . import models, views
from sbadmin2.crud import generate_crud_urls
from django.urls import path

urlpatterns = [
    *generate_crud_urls('', 'secret', models.Secret),
]