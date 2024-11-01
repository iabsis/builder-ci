from . import models, views
from sbadmin2.crud import generate_crud_urls
from django.urls import path

urlpatterns = [
    *generate_crud_urls('flow', 'flow', models.Flow, create=False, update=False),
    path('flow/create/', views.FlowCreateView.as_view(), name='flow_create'),
    path('flow/update/<int:pk>', views.FlowUpdateView.as_view(), name='flow_update'),
    *generate_crud_urls('method', 'method', models.Method),
    # *generate_crud_urls('task', 'task', models.Task),
]