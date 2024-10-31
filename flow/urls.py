from . import models
from sbadmin2.crud import generate_crud_urls

urlpatterns = [
    *generate_crud_urls('flow', 'flow', models.Flow),
    *generate_crud_urls('method', 'method', models.Method),
    *generate_crud_urls('task', 'task', models.Task),
]