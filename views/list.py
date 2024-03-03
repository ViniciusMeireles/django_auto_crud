from typing import Optional, Union, List

from django.core.paginator import InvalidPage
from django.http import Http404
from django.utils.translation import gettext as _
from django.views.generic import ListView as BaseListView

from django_auto_crud.utils.views import get_verbose_name_plural, get_model_list_view_url, get_model_create_view_url, \
    get_template_path
from .mixins import ViewMixin


class ListView(BaseListView, ViewMixin):
    """
    View for displaying a list of objects, with a response rendered by a template.
    """
    template_name: Optional[str] = get_template_path('list')
    table_title: Optional[str] = None
    is_button_create: Optional[bool] = True
    create_url: Optional[str] = None
    fields: Optional[Union[str, List[str]]] = None
    actions: Optional[dict] = None
    paginate_by = 20

    def get_page_title(self) -> str:
        """
        Get page title. If not defined, get verbose name of the model.

        :return: Page title.
        """
        if self.page_title is None:
            self.page_title = 'List ' + get_verbose_name_plural(self.model)
        return self.page_title

    def get_table_title(self) -> str:
        """
        Get table title. If not defined, get verbose name plural of the model.

        :return: Table title.
        """
        if self.table_title is None:
            self.table_title = get_verbose_name_plural(self.model)
        return self.table_title

    def get_button_create(self) -> bool:
        """
        Get button create. If not defined, return True.

        :return: Button create.
        """
        if self.is_button_create is None:
            self.is_button_create = True
        return self.is_button_create

    def get_breadcrumbs(self) -> dict:
        """
        Get breadcrumbs.
        :return: Breadcrumbs.
        """
        if self.breadcrumbs is None:
            self.breadcrumbs = super().get_breadcrumbs()
            try:
                # Add the list view URL of the model to the breadcrumbs
                self.breadcrumbs[get_verbose_name_plural(self.model)] = get_model_list_view_url(self.model)
            except:
                pass

        return self.breadcrumbs

    def get_create_url(self) -> str:
        """
        Get create URL. If not defined, get the create view URL of the model.

        :return: Create URL.
        """
        if not self.is_button_create:
            return ''
        if self.create_url is None:
            # Get the create view URL of the model from the model name. Example: 'app_label:model_name_create'
            self.create_url = get_model_create_view_url(self.model)
        return self.create_url

    def get_fields(self) -> list:
        """
        Get fields. If not defined, return '__all__'.

        :return: Fields.
        """
        if self.fields is None:
            self.fields = '__all__'
        return self.fields

    def get_actions(self) -> dict:
        """
        Get actions. If not defined, return None.

        :return: Actions.
        """
        if self.actions is None:
            self.actions = {
                'detail_ajax': None,
                'update': None,
                'delete_ajax': None,
            }
        return self.actions

    def get_ordering(self):
        """
        Get ordering. If not defined, return ['pk'].

        :return: Ordering.
        """
        sort = self.request.GET.get('sort', None)
        order = self.request.GET.get('order', None)

        if order == 'desc':
            order = '-'
        elif order == 'asc':
            order = ''

        if order and sort:
            self.ordering = [f'{order}{sort}']
        if not self.ordering:
            self.ordering = ['pk']
        return super().get_ordering()

    def paginate_queryset(self, queryset, page_size):
        """
        Paginate queryset. If page number is greater than the number of pages, return the last page.

        :return: Paginate queryset.
        """
        try:
            return super().paginate_queryset(queryset, page_size)
        except Exception as e:
            # Get the page number from the request
            page_kwarg = self.page_kwarg
            page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
            try:
                # Try to convert the page number to an integer
                page_number = int(page)
            except ValueError:
                raise e

        # Get the paginator
        paginator = self.get_paginator(
            queryset,
            page_size,
            orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty(),
        )
        # If the page number is greater than the number of pages, return the last page
        if page_number > paginator.num_pages:
            page_number = paginator.num_pages

        try:
            # Get the page
            page = paginator.page(page_number)
            return paginator, page, page.object_list, page.has_other_pages()
        except InvalidPage as e:
            raise Http404(
                _("Invalid page (%(page_number)s): %(message)s")
                % {"page_number": page_number, "message": str(e)}
            )

    def get_context_data(self, **kwargs):
        """
        Get context data.

        :param kwargs:
        :return: Context data.
        """
        context = super().get_context_data(**kwargs)
        context['table_title'] = self.get_table_title()
        context['is_button_create'] = self.get_button_create()
        context['create_url'] = self.get_create_url()
        context['model'] = self.model
        context['fields'] = self.get_fields()
        context['sort'] = self.request.GET.get('sort', None)
        context['order'] = self.request.GET.get('order', None)
        context['actions'] = self.get_actions()
        return context


def list_view_factory(
        model,
        template_name: Optional[str] = get_template_path('list'),
        title: Optional[str] = None,
        page_lang: Optional[str] = None,
        page_title: Optional[str] = None,
        template_base: Optional[str] = None,
        breadcrumbs: Optional[dict] = None,
        table_title: Optional[str] = None,
        is_button_create: Optional[bool] = True,
        create_url: Optional[str] = None,
        fields: Optional[Union[str, List[str]]] = None,
        actions: Optional[dict] = None,
        view_class: type[ListView] = ListView,
        **kwargs,
):
    """
    List view factory. Create a view class with the specified parameters.

    :param model:
    :param template_name:
    :param title:
    :param page_lang:
    :param page_title:
    :param template_base:
    :param breadcrumbs:
    :param table_title:
    :param is_button_create:
    :param create_url:
    :param fields:
    :param actions:
    :param view_class:
    :param kwargs:
    :return: List view.
    """

    return type(
        f'{model.__name__}ListView',
        (view_class,),
        {
            'model': model,
            'template_name': template_name,
            'title': title,
            'page_lang': page_lang,
            'page_title': page_title,
            'template_base': template_base,
            'breadcrumbs': breadcrumbs,
            'table_title': table_title,
            'is_button_create': is_button_create,
            'create_url': create_url,
            'fields': fields,
            'actions': actions,
            **kwargs,
        }
    )
