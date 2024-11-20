from . import models, views
from sbadmin2.crud import generate_crud_urls
from django.urls import path

urlpatterns = [
    *generate_crud_urls('', 'secret', models.Secret, update=False),
    path('update/<int:pk>/', views.SecretUpdateView.as_view(), name='secret_update'),
]