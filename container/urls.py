from . import models
from sbadmin2.crud import generate_crud_urls

urlpatterns = [
    *generate_crud_urls('container', 'container', models.Container),
]