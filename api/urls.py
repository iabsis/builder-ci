from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'build', views.BuildRequestViewSet)


urlpatterns = [
    path('build',
        views.BuildRequestViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('', include(router.urls)),
]

