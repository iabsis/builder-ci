"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='build')),
    path('admin/', admin.site.urls),
    # path('accounts/', include("sbadmin2.urls")),
    path('accounts/', include('allauth.urls')),
    path('container/', include("container.urls")),
    path('flow/', include("flow.urls")),
    path('build/', include("build.urls")),
    path('secret/', include("secret.urls")),
    path('api/', include("api.urls")),
]
