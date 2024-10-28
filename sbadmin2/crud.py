from . import views
from django.urls import path


def generate_crud_urls(root_path, root_name, model, list=True, create=True, update=True, delete=True):
    urls = []

    if list:
        urls.append(
            path(
                f"{root_path}/", views.GenericViewList.as_view(model=model), name=root_name)
        )

    if update:
        urls.append(
            path(
                f"{root_path}/<int:pk>/", views.GenericViewFormUpdate.as_view(model=model),
                            name=f"{root_name}_update")
        )
    
    if create:
        urls.append(
            path(
                f"{root_path}/create/", views.GenericViewFormCreate.as_view(model=model),
                            name=f"{root_name}_create")
        )
    
    if delete:
        urls.append(
            path(
                f"{root_path}/delete/<int:pk>/", views.GenericViewDelete.as_view(model=model),
                            name=f"{root_name}_delete")
        )

    print(urls)

    return urls