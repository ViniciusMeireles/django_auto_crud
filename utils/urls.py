from functools import partial
from typing import List, Optional

from django.db.models import Model
from django.urls import path

from django_auto_crud.views.create import create_view_factory
from django_auto_crud.views.delete import delete_view_factory
from django_auto_crud.views.detail import detail_view_factory
from django_auto_crud.views.list import list_view_factory
from django_auto_crud.views.update import update_view_factory


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
    Generate CRUD template. Generate a list, create, detail, update and delete views for a model.
    Example return: [path('/', view, name='model_list'), path('/create/', view, name='model_create'), ...]

    :param model: Model class to generate views for it.
    :param path_route: Path route, default is model name.
    :param is_list: Has list view.
    :param is_create: Has creation view.
    :param is_detail: Has detail view.
    :param is_update: Has update view.
    :param is_delete: Has deletion view.
    :return: CRUD template. List, create, detail, update and delete views in a list of urlpatterns.
    """
    # Add trailing slash to path_route
    if not path_route.endswith('/'):
        path_route = f'{path_route}/'

    url_patterns = []
    if is_list:
        # Add actions to list view if it is enabled
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
                view=list_view_factory(
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
                view=create_view_factory(
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
                view=detail_view_factory(
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
                view=update_view_factory(
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
                view=delete_view_factory(
                    model=model,
                    is_button_back=is_detail or is_list,
                ).as_view(),
                name=f'{model._meta.model_name}_delete'
            )
        )
    return url_patterns


def generate_crud_urlpatterns(models: List[type[Model]]) -> List[partial]:
    """
    Generate urlpatterns. Generate a list, create, detail, update and delete views for a list of models.
    Exemple return: [
        path('model1/', view, name='model1_list'), path('model1/create/', view, name='model1_create'), ...
        path('model2/', view, name='model2_list'), path('model2/create/', view, name='model2_create'), ...
    ...]

    :param models: List of models to generate views for them. [Model1, Model2, ...]
    :return: urlpatterns. List, create, detail, update and delete views in a list of urlpatterns.
    """
    urlpatterns = []
    for model in models:
        urlpatterns += generate_crud_templates(model=model, path_route=f'{model._meta.model_name}/')
    return urlpatterns
