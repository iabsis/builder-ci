from . import views
from django.urls import path
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
]