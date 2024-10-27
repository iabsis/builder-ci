from . import models
from sbadmin2.crud import generate_crud_urls

from . import views

urlpatterns = [
    *generate_crud_urls('request', 'request', models.BuildRequest)
]