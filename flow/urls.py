from . import models, views
from sbadmin2.crud import generate_crud_urls
from django.urls import path

urlpatterns = [
    *generate_crud_urls('', 'flow', models.Flow, create=False, update=False),
    path('create/', views.FlowCreateView.as_view(), name='flow_create'),
    path('test/<int:pk>/', views.FlowTestView.as_view(), name='flow_test'),
    path('update/<int:pk>/', views.FlowUpdateView.as_view(), name='flow_update'),
    *generate_crud_urls('method', 'method', models.Method),
    # *generate_crud_urls('task', 'task', models.Task),
]