import os
from importlib import import_module
from typing import Optional, Union, List

from django import template
from django.apps import apps
from django.conf import settings
from django.db.models import Model
from django.templatetags.static import StaticNode
from django.urls import reverse_lazy, resolve, URLPattern
from django.utils.html import format_html
from django.utils.translation import gettext_lazy

from django_auto_crud.utils.views import (get_model_detail_view_url, get_model_update_view_url,
                                          get_model_delete_view_url, get_verbose_name, get_verbose_name_plural)

register = template.Library()


@register.simple_tag
def create_breadcrumbs(breadcrumbs_dict: dict, current_path: str = None) -> str:
    """
    Create breadcrumbs from dictionary.

    :param breadcrumbs_dict: dictionary with breadcrumbs.
    :param current_path: current path.
    :return: breadcrumbs html.
    """
    breadcrumbs = ['']
    for key, value in breadcrumbs_dict.items():
        if current_path and current_path == str(gettext_lazy(value)):
            breadcrumb_item = f'<li class="breadcrumb-item active">{key}</li>'
        else:
            breadcrumb_item = f'<li class="breadcrumb-item"><a href="{value}">{key}</a></li>'
        breadcrumbs.append(breadcrumb_item)
    return format_html(''.join(breadcrumbs))


@register.simple_tag
def create_left_navbar(left_navbar_links_dict: dict, current_path: str = None) -> str:
    """
    Create left navbar from dictionary.

    :param left_navbar_links_dict: dictionary with navbar.
    :param current_path: current path.
    :return: navbar html.
    """
    navbar = ['']
    for key, value in left_navbar_links_dict.items():
        if value == current_path:
            navbar_item = (f'<li class="nav-item d-none d-sm-inline-block">'
                           f'<a href="#" class="nav-link active">{key}</a></li>')
        else:
            navbar_item = (f'<li class="nav-item d-none d-sm-inline-block">'
                           f'<a href="{value}" class="nav-link">{key}</a></li>')
        navbar.append(navbar_item)
    return format_html(''.join(navbar))


@register.simple_tag
def create_details_object_fields(obj: Model, fields: Optional[Union[str, List[str]]] = None) -> str:
    """
    Create object details html.

    :param obj: object.
    :param fields: list of fields.
    :return: object details html.
    """
    details = ['']
    # If fields is None or '__all__' get all fields
    if not fields or fields == '__all__':
        fields = [field.name for field in obj._meta.get_fields()]
    elif not isinstance(fields, list):
        raise TypeError('fields must be a list of strings or "__all__"')

    # Create detail item for each field in fields list
    for field in fields:
        # Verify if object has a get_{field} method
        if hasattr(obj, f'get_{field}'):
            # Get value from get_{field} method
            field_value = getattr(obj, f'get_{field}')()
        else:
            # Get value from field
            field_value = getattr(obj, field)
        # Get field verbose name
        field_name = obj._meta.get_field(field).verbose_name
        # Create detail item
        details_item = (
            f'<li class="item"><div class="item-info">'
            f'<a href="javascript:void(0)" class="product-title">{field_name}</a>'
            f'<p>{field_value}</p></div></li>'
            f'<!-- /.item -->'
        )
        # Append detail item to details list
        details.append(details_item)

    # Return details list as html
    return format_html(''.join(details))


@register.simple_tag
def create_header_table(
        model: type[Model],
        fields: Optional[Union[str, List[str]]] = None,
        sort: Optional[str] = None,
        order: Optional[str] = None,
        actions: Optional[List[str]] = None
) -> str:
    """
    Create header table html for list view of a model.

    :param model: Model.
    :param fields: list of fields, '__all__' to get all fields.
    :param sort: Sort field name.
    :param order: Order of sort, 'asc' or 'desc'.
    :param actions: list of actions, 'detail', 'update', 'delete'.
    :return: header table html.
    """
    header = ['']
    if not fields or fields == '__all__':
        fields = [field.name for field in model._meta.get_fields()]
    elif not isinstance(fields, list):
        raise TypeError('fields must be a list of strings or "__all__"')

    # Create header item for each field in fields list
    for field in fields:
        # Get field verbose name
        field_name = model._meta.get_field(field).verbose_name
        # Create header item with sort and order
        if sort == field and order == 'asc':
            header_item = (
                f'<th><a href="?sort={field}&order=desc">'
                f'{field_name}'
                f'<i class="fas fa-sort-up"></i>'
                f'</a></th>'
            )
        elif sort == field and order == 'desc':
            header_item = (
                f'<th><a href="?sort={field}&order=asc">'
                f'{field_name}'
                f'<i class="fas fa-sort-down"></i>'
                f'</a></th>'
            )
        else:
            header_item = (
                f'<th><a href="?sort={field}&order=asc">'
                f'{field_name}'
                f'</a></th>'
            )
        header.append(header_item)

    # Add actions header item
    if actions:
        header_item = '<th>Actions</th>'
        header.append(header_item)

    # Return header list as html
    return format_html(''.join(header))


def get_column_actions(obj: Model, actions: Optional[dict] = None) -> str:
    """
    Get actions column for row in table of list view of a model. Detail, update, delete.

    :param obj: object.
    :param actions: actions dictionary. {'detail': 'path_name', 'update': 'path_name', 'delete': 'path_name'}
    :return: column actions html.
    """
    if not actions:
        return ''

    # Add opening tag for actions column
    column_actions = ['<td class="text-center">']
    # Create action button for each action in actions dictionary
    for action, path_name in actions.items():
        button_action = None

        if action == 'detail' or action == 'detail_ajax':
            # Get URL for object detail view
            if path_name:
                url = reverse_lazy(path_name, kwargs={'pk': obj.pk})
            else:
                url = get_model_detail_view_url(obj.__class__, obj.pk)
            # If action is detail_ajax create ajax button
            if action == 'detail':
                button_action = (
                    f'<a href="{url}" class="btn btn-info btn-sm m-1"><i class="fas fa-eye"></i></a>'
                )
            else:
                button_action = (
                    f'<a data-url="{url}" class="btn btn-info btn-sm m-1 detail-ajax"><i class="fas fa-eye"></i></a>'
                )
        elif action == 'update':
            # Get URL for object update view
            if path_name:
                url = reverse_lazy(path_name, kwargs={'pk': obj.pk})
            else:
                url = get_model_update_view_url(obj.__class__, obj.pk)
            # Button for object update
            button_action = (
                f'<a href="{url}" class="btn btn-warning btn-sm m-1"><i class="fas fa-edit"></i></a>'
            )
        elif action == 'delete' or action == 'delete_ajax':
            # Get URL for object delete view
            if path_name:
                url = reverse_lazy(path_name, kwargs={'pk': obj.pk})
            else:
                url = get_model_delete_view_url(model=obj.__class__, pk=obj.pk)
            # If action is delete_ajax create ajax button
            if action == 'delete':
                button_action = (
                    f'<a href="{url}" class="btn btn-danger btn-sm m-1"><i class="fas fa-trash"></i></a>'
                )
            else:
                button_action = (
                    f'<a data-url="{url}" class="btn btn-danger btn-sm m-1 delete-ajax">'
                    f'<i class="fas fa-trash"></i></a>'
                )

        # Append button action to column actions
        if button_action:
            column_actions.append(button_action)

    # Add closing tag for actions column
    column_actions.append('</td>')
    # Return column actions as html
    return ''.join(column_actions)


@register.simple_tag
def create_body_table(
        objects: List[Model],
        fields: Optional[Union[str, List[str]]] = None,
        actions: Optional[dict] = None
) -> str:
    """
    Create table body html. Rows and columns for list view of a model.

    :param objects: list of objects.
    :param fields: list of fields. '__all__' to get all fields.
    :param actions: list of actions. 'detail', 'update', 'delete'.
    :return: body table html.
    """
    body = ['']
    if not objects:
        # If objects is empty create a row with no data available
        body.append('<tr><td colspan="100%">No data available</td></tr>')
    else:
        # If fields is None or '__all__' get all fields
        if not fields or fields == '__all__':
            fields = [field.name for field in objects[0]._meta.get_fields()]
        elif not isinstance(fields, list):
            raise TypeError('fields must be a list of strings or "__all__"')

    # Create row for each object in objects list
    for obj in objects:
        # Add opening tag for row
        body_item = ['<tr>']
        # Create column for each field in fields list
        for field in fields:
            if hasattr(obj, f'get_{field}'):
                # Get value from get_{field} method
                field_value = getattr(obj, f'get_{field}')()
            else:
                # Get value from field
                field_value = getattr(obj, field)
            # Append column to row
            body_item.append(f'<td>{field_value}</td>')

        # Append actions column to row
        body_item.append(get_column_actions(obj, actions))

        # Add closing tag for row
        body_item.append('</tr>')
        # Append row to body
        body_item = ''.join(body_item)
        body.append(body_item)

    # Return body list as html
    return format_html(''.join(body))


@register.tag('static_theme')
def static_theme(parser, token):
    """
    Get files for static theme. If STATIC_THEME is not defined, use default theme.
    """
    bits = token.split_contents()

    if len(bits) < 2:
        raise template.TemplateSyntaxError(
            "'%s' takes at least one argument (path to file)" % bits[0]
        )

    path = parser.compile_filter(bits[1])

    try:
        static_theme_path = os.path.join(settings.STATIC_THEME)
        if not static_theme_path.endswith('/'):
            static_theme_path += '/'
        path.var = static_theme_path + path.var
    except AttributeError:
        path.var = 'django_auto_crud/adminlte_3_2_0/' + path.var

    if len(bits) >= 2 and bits[-2] == "as":
        varname = bits[3]
    else:
        varname = None

    return StaticNode(varname, path)


@register.tag('static_logo')
def static_logo(*args):
    """
    Get static logo.

    :param args: Arguments.
    :return: Static logo.
    """
    parser = args[0]
    bit_default = "'django_auto_crud/images/Django Auto Crud Logo.png'"

    try:
        bit = "'" + str(os.path.join(settings.STATIC_LOGO)) + "'"
    except AttributeError:
        bit = bit_default

    path = parser.compile_filter(bit)

    return StaticNode(path=path)


@register.tag('static_favicon')
def static_favicon(*args):
    """
    Get static favicon.

    :param args: Arguments.
    :return: Static favicon.
    """
    parser = args[0]
    bit_default = "'django_auto_crud/images/favicon.webp'"

    try:
        bit = "'" + str(os.path.join(settings.STATIC_FAVICON)) + "'"
    except AttributeError:
        bit = bit_default

    path = parser.compile_filter(bit)

    return StaticNode(path=path)


def check_active_item(current_url: str, model_name: str, crud_names: [List[str]]) -> bool:
    """
    Check if item is active.

    :param current_url: current url.
    :param model_name: model name.
    :param crud_names: list of crud names.
    :return: True if item is active.
    """
    match = resolve(current_url)
    for crud_name in crud_names:
        if match.url_name == f'{model_name}_{crud_name}':
            return True
    return False


@register.simple_tag()
def sidebar_items(current_url: str) -> str:
    """
    Convert urlpatterns to left navbar items.

    :param current_url: current URL.
    :return: Left navbar items HTML.
    """

    local_app_names = settings.LOCAL_APPS
    left_navbar_links = ['']

    for local_app_name in local_app_names:
        # Go through all the apps and look for all the urls to put in the sidebar
        app_config = apps.get_app_config(local_app_name)
        urls_module_str = app_config.module.__name__ + '.urls'

        try:
            urls_module = import_module(urls_module_str)
        except ImportError:
            continue

        urlpatterns = urls_module.urlpatterns

        try:
            app_name = urls_module.app_name
        except AttributeError:
            app_name = local_app_name

        left_navbar_links.append(f'<li class="nav-header">{app_name.title()}</li>')

        crud_groups = group_urls_by_model(urlpatterns)

        is_active_found = False

        for model_name, crud_names in crud_groups.items():
            active = False if is_active_found else check_active_item(current_url, model_name, crud_names)

            if len(crud_names) > 1:
                left_navbar_links.extend(
                    create_group_navbar_items(current_url, app_name, model_name, crud_names, active)
                )
            elif crud_names[0] not in ['detail', 'update', 'delete']:
                if crud_names[0] is None:
                    url = reverse_lazy(f'{app_name}:{model_name}')
                    left_navbar_links.append(create_navbar_item(url, model_name.title(), active))
                else:
                    url = reverse_lazy(f'{app_name}:{model_name}_{crud_names[0]}')
                    left_navbar_links.append(create_navbar_item(url, crud_names[0].title(), active))

            is_active_found = is_active_found or active

    return format_html(''.join(left_navbar_links))


def group_urls_by_model(urlpatterns: List[URLPattern]) -> dict:
    """
    Groups URLs by model.

    :param urlpatterns: List of URL patterns.
    :return: Dictionary with model names as keys and lists of CRUD names as values.
    """
    crud_groups = {}
    for url in urlpatterns:
        path_name = url.name.split('_', 1)
        model_name = path_name[0]
        if len(path_name) == 1:
            crud_name = None
        else:
            crud_name = path_name[1]
        crud_groups[model_name] = crud_groups.get(model_name, []) + [crud_name]

    return crud_groups


def create_navbar_item(url: str, title: str, active: bool) -> str:
    """
    Creates a single navbar item.

    :param url: URL for the item.
    :param title: Title of the item.
    :param active: Whether the item is active.
    :return: HTML string for the navbar item.
    """
    return (
        f'<li class="nav-item">'
        f'<a href="{url}" class="nav-link {"active" if active else ""}">'
        f'<i class="far fa-circle nav-icon"></i>'
        f'<p>{title}</p></a></li>'
    )


def create_group_navbar_items(
        current_url: str,
        app_name: str,
        model_name: str,
        crud_names: List[str],
        active: bool,
) -> List[str]:
    """
    Creates a group of navbar items for a model with multiple CRUD operations.

    :param current_url: Current URL.
    :param app_name: Name of the Django app.
    :param model_name: Name of the Django model.
    :param crud_names: List of CRUD operation names.
    :param active: Whether the group is active.
    :return: List of HTML strings for the group of navbar items.
    """
    model_class = apps.get_model(app_name, model_name)
    model_title = get_verbose_name(model_class)

    if 'list' in crud_names:
        return [
            f'<li class="nav-item {"menu-open" if active else ""}"">'
            f'<a href="#" class="nav-link {"active" if active else ""}">'
            f'<i class="nav-icon fas fa-table"></i>'
            f'<p>{model_title}<i class="fas fa-angle-left right"></i></p></a>'
            f'<ul class="nav nav-treeview">',
            create_navbar_item(reverse_lazy(f'{app_name}:{model_name}_list'), get_verbose_name_plural(model_class),
                               active),
            '</ul></li>'
        ]
    else:
        group_navbar_items = []
        group_active = False
        valid_crud_names = [crud_name for crud_name in crud_names if crud_name not in ['detail', 'update', 'delete']]
        is_active_found = False
        for crud_name in valid_crud_names:
            active = False if is_active_found else check_active_item(current_url, model_name, crud_names)
            group_active = group_active or active
            url = reverse_lazy(f'{app_name}:{model_name}_{crud_name}')
            group_navbar_items.append(create_navbar_item(url, crud_name.title(), active))

        return [
            f'<li class="nav-item {"menu-open" if group_active else ""}">'
            f'<a href="#" class="nav-link {"active" if group_active else ""}">'
            f'<i class="nav-icon fas fa-table"></i>'
            f'<p>{model_title}<i class="fas fa-angle-left right"></i></p></a>'
            f'<ul class="nav nav-treeview">',
            *group_navbar_items,
            '</ul></li>'
        ]