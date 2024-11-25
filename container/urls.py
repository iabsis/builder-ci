from django.urls import path
from . import models, views
from sbadmin2.crud import generate_crud_urls

urlpatterns = [
    *generate_crud_urls('', 'configcontainer', models.Container),
    *generate_crud_urls('builtcontainer', 'builtcontainer',
                        models.BuiltContainer, create=False, update=False, view=True),
                        path('builtcontainer/run/<int:pk>/', views.ReBuildContainer.as_view(), name="builtconainer_rebuild"),
]