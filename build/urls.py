from . import models
from sbadmin2.crud import generate_crud_urls

urlpatterns = [
    *generate_crud_urls('build', 'build', models.Build),
    *generate_crud_urls('request', 'request', models.BuildRequest),
]