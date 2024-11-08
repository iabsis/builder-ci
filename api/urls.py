from django.urls import path
from . import views

urlpatterns = [
    path('build/', views.BuildView.as_view()),
    path('build', views.BuildView.as_view())
]

