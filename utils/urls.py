from functools import partial
from typing import List, Optional

from django.db.models import Model
from django.urls import path

from django_adminlte import views


def generate_crud_templates(
        model: type[Model],
        path_route: Optional[str] = '',
        is_list: bool = True,
        is_create: bool = True,
        is_detail: bool = True,
        is_update: bool = True,
        is_delete: bool = True,
) -> List[partial]:
    """
    Generate CRUD template.

    :param model: Model.
    :param path_route: Path.
    :param is_list: List view.
    :param is_create: Create view.
    :param is_detail: Detail view.
    :param is_update: Update view.
    :param is_delete: Delete view.
    :return: CRUD template.
    """
    if not path_route.endswith('/'):
        path_route = f'{path_route}/'

    url_patterns = []
    if is_list:
        actions = {}
        if is_detail:
            actions['detail_ajax'] = None
        if is_update:
            actions['update'] = None
        if is_delete:
            actions['delete_ajax'] = None
        url_patterns.append(
            path(
                route=f'{path_route}',
                view=views.list_view_factory(
                    model=model,
                    is_button_create=is_create,
                    actions=actions,
                ).as_view(),
                name=f'{model._meta.model_name}_list'
            )
        )
    if is_create:
        url_patterns.append(
            path(
                route=f'{path_route}create/',
                view=views.create_view_factory(
                    model=model,
                    is_button_back=is_list,
                ).as_view(),
                name=f'{model._meta.model_name}_create'
            )
        )
    if is_detail:
        url_patterns.append(
            path(
                route=f'{path_route}<int:pk>/',
                view=views.detail_view_factory(
                    model=model,
                    is_button_back=is_list,
                    is_button_update=is_update,
                    is_button_delete=is_delete,
                ).as_view(),
                name=f'{model._meta.model_name}_detail'
            )
        )
    if is_update:
        url_patterns.append(
            path(
                route=f'{path_route}<int:pk>/update/',
                view=views.update_view_factory(
                    model=model,
                    is_button_back=is_detail or is_list,
                ).as_view(),
                name=f'{model._meta.model_name}_update'
            )
        )
    if is_delete:
        url_patterns.append(
            path(
                route=f'{path_route}<int:pk>/delete/',
                view=views.delete_view_factory(
                    model=model,
                    is_button_back=is_detail or is_list,
                ).as_view(),
                name=f'{model._meta.model_name}_delete'
            )
        )
    return url_patterns


def generate_crud_urlpatterns(models: List[type[Model]]) -> List[partial]:
    """
    Generate urlpatterns.

    :param models: Models.
    :return: urlpatterns.
    """
    urlpatterns = []
    for model in models:
        urlpatterns += generate_crud_templates(model=model, path_route=f'{model._meta.model_name}/')
    return urlpatterns
