from django.conf import settings
from django.db.models import Model
from django.urls import get_resolver, reverse_lazy, reverse


def get_home_url() -> str:
    """
    Get home URL. It uses HOME_PATH_NAME from settings.py.

    :return: Home URL. Default is 'home'.
    """
    try:
        home_path_name = settings.HOME_PATH_NAME
    except AttributeError:
        # If HOME_PATH_NAME is not defined, use app_name from urls.py or 'home' as default. The urls.py app_name is the
        # obtained from the ROOT_URLCONF.
        home_path_name = get_resolver().app_name + ':home' if get_resolver().app_name else 'home'

    try:
        return reverse(home_path_name)
    except:
        raise Exception('HOME_PATH_NAME is not defined in settings.py')


def get_verbose_name(model: type[Model]) -> str:
    """
    Get model verbose name.

    :param model: Model.
    :return: Model verbose name.
    """
    return model._meta.verbose_name.title()


def get_verbose_name_plural(model: type[Model]) -> str:
    """
    Get model verbose name plural.

    :param model: Model.
    :return: Model verbose name plural.
    """
    return model._meta.verbose_name_plural.title()


def get_model_path_partial_name(model: type[Model]) -> str:
    """
    Get model path name. Example: 'app_name:model_name'.

    :param model: Model.
    :return: Model path name.
    """
    return f'{model._meta.app_label}:{model._meta.model_name}'


def get_model_list_view_url(model: type[Model]) -> str:
    """
    Get model list URL. Example: URL for path_name 'app_name:model_name_list'.

    :param model: Model.
    :return: Model list URL.
    """
    return reverse_lazy(
        f'{get_model_path_partial_name(model=model)}_list'
    )


def get_model_create_view_url(model: type[Model]) -> str:
    """
    Get model create URL. Example: URL for path_name 'app_name:model_name_create'.

    :param model: Model.
    :return: Model create URL.
    """
    return reverse_lazy(
        f'{get_model_path_partial_name(model=model)}_create'
    )


def get_model_detail_view_url(model: type[Model], pk: int) -> str:
    """
    Get model detail URL. Example: URL for path_name 'app_name:model_name_detail'.

    :param model: Model.
    :param pk: Primary key.
    :return: Model detail URL.
    """
    return reverse_lazy(
        f'{get_model_path_partial_name(model=model)}_detail',
        kwargs={'pk': pk}
    )


def get_model_update_view_url(model: type[Model], pk: int) -> str:
    """
    Get model update URL. Example: URL for path_name 'app_name:model_name_update'.

    :param model: Model.
    :param pk: Primary key.
    :return: Model update URL.
    """
    return reverse_lazy(
        f'{get_model_path_partial_name(model=model)}_update',
        kwargs={'pk': pk}
    )


def get_model_delete_view_url(model: type[Model], pk: int) -> str:
    """
    Get model delete URL. Example: URL for path_name 'app_name:model_name_delete'.

    :param model: Model.
    :param pk: Primary key.
    :return: Model delete URL.
    """
    return reverse_lazy(
        f'{get_model_path_partial_name(model=model)}_delete',
        kwargs={'pk': pk}
    )


def get_template_path(template: str) -> str | None:
    """
    Get CRUD template. It uses TEMPLATE_PATHS from settings.py. If TEMPLATE_PATHS is not defined, it uses default

    :param template: Template name ('base', 'list', 'create', 'detail', 'update', 'delete', 'form').
    :return: CRUD template path.
    """
    try:
        return settings.TEMPLATE_PATHS[template]
    except (AttributeError, KeyError):
        return {
            'base': 'django_auto_crud/theme/base.html',
            'list': 'django_auto_crud/crud/list.html',
            'create': 'django_auto_crud/crud/create.html',
            'detail': 'django_auto_crud/crud/detail.html',
            'detail_ajax': 'django_auto_crud/crud/detail_ajax.html',
            'update': 'django_auto_crud/crud/update.html',
            'delete': 'django_auto_crud/crud/delete.html',
            'form': 'django_auto_crud/crud/form.html',
            'navbar_left': None,
            'navbar_right': None,
            'sidebar_itens': None,
        }.get(template)
