from importlib import import_module
from typing import Optional, Union, List

from django.conf import settings
from django.core.paginator import InvalidPage
from django.forms import modelform_factory
from django.http import JsonResponse, Http404
from django.utils.translation import gettext as _
from django.views.generic import CreateView as BaseCreateView, UpdateView as BaseUpdateView, \
    DetailView as BaseDetailView, ListView as BaseListView, DeleteView as BaseDeleteView
from django.views.generic.base import ContextMixin
from django.views.generic.edit import ModelFormMixin as BaseModelFormMixin

from django_auto_crud.utils.views import get_home_url, get_verbose_name, get_model_detail_view_url, \
    get_verbose_name_plural, \
    get_model_list_view_url, get_model_update_view_url, get_model_delete_view_url, get_model_create_view_url, \
    get_template_path


class ViewMixin(ContextMixin):
    """
    Mixin for views.
    """
    title: Optional[str] = None
    page_lang: Optional[str] = None
    page_title: Optional[str] = None
    template_base: Optional[str] = None
    breadcrumbs: Optional[dict] = None
    left_navbar_template: Optional[str] = None
    right_navbar_template: Optional[str] = None
    sidebar_itens_template: Optional[str] = None

    def get_page_lang(self) -> str:
        """
        Get page language.

        :return: Page language.
        """
        if self.page_lang is None:
            try:
                self.page_lang = settings.LANGUAGE_SITE
            except:
                self.page_lang = settings.LANGUAGE_CODE
        return self.page_lang

    def get_page_title(self) -> str:
        """
        Get page title.

        :return: Page title.
        """
        if self.page_title is None:
            self.page_title = ''
        return self.page_title

    def get_title(self) -> str:
        """
        Get title.

        :return: Title.
        """
        if self.title is None:
            self.title = self.get_page_title()
        return self.title

    def get_breadcrumbs(self) -> dict:
        """
        Get breadcrumbs.

        :return: Breadcrumbs.
        """
        if self.breadcrumbs is None:
            self.breadcrumbs = {
                'Home': get_home_url(),
            }
        return self.breadcrumbs

    def get_user_name(self):
        """
        Get name user.

        :return: Name user.
        """
        request = getattr(self, 'request', None)
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            return user.get_full_name()

    def get_left_navbar_template(self) -> str:
        """
        Get left navbar template.

        :return: Left navbar template.
        """
        if self.left_navbar_template is None:
            self.left_navbar_template = get_template_path('navbar_left')
        return self.left_navbar_template

    def get_right_navbar_template(self) -> str:
        """
        Get right navbar template.

        :return: Right navbar template.
        """
        if self.right_navbar_template is None:
            self.right_navbar_template = get_template_path('navbar_right')
        return self.right_navbar_template

    def get_sidebar_itens_template(self) -> str:
        """
        Get sidebar itens template.

        :return: Sidebar itens template.
        """
        if self.sidebar_itens_template is None:
            self.sidebar_itens_template = get_template_path('sidebar_itens')
        return self.sidebar_itens_template

    def get_context_data(self, **kwargs):
        """
        Get context data.

        :param kwargs:
        :return: Context data.
        """
        context = super().get_context_data(**kwargs)
        context['page_lang'] = self.get_page_lang()
        context['page_title'] = self.get_page_title()
        context['title'] = self.get_title()
        context['template_base'] = self.template_base if self.template_base else get_template_path('base')
        context['breadcrumbs'] = self.get_breadcrumbs()
        context['site_url'] = get_home_url()
        context['user_name'] = self.get_user_name()
        context['left_navbar_template'] = self.get_left_navbar_template()
        context['right_navbar_template'] = self.get_right_navbar_template()
        context['sidebar_itens_template'] = self.get_sidebar_itens_template()
        try:
            context['site_title'] = settings.SITE_NAME
        except:
            pass
        return context


class ModelFormMixin(BaseModelFormMixin, ViewMixin):
    form_title: Optional[str] = None
    form_method: Optional[str] = 'POST'
    is_form_helper: Optional[bool] = None

    is_button_back: Optional[bool] = True
    back_url: Optional[str] = None
    submit_button_text: Optional[str] = None
    template_form_base: Optional[str] = get_template_path('form')

    def get_form_title(self) -> str:
        """
        Get form title.

        :return: Form title.
        """
        if self.form_title is None:
            self.form_title = get_verbose_name(self.model)
        return self.form_title

    def get_page_title(self) -> str:
        """
        Get page title.

        :return: Page title.
        """
        if self.page_title is None:
            self.page_title = get_verbose_name(self.model)
        return self.page_title

    def get_is_form_helper(self) -> bool:
        """
        Get is form helper.

        :return: Is form helper.
        """
        if self.is_form_helper is None:
            self.is_form_helper = hasattr(self.get_form_class(), 'helper')
        return self.is_form_helper

    def get_back_url(self) -> str:
        """
        Get back URL.
        :return: Back URL
        """
        if not self.is_button_back:
            return ''
        if self.back_url is None:
            try:
                self.back_url = get_model_detail_view_url(self.model, self.get_object().pk)
            except:
                self.back_url = get_model_list_view_url(self.model)
        return self.back_url

    def get_success_url(self) -> str:
        """
        Get success URL.

        :return: Success URL.
        """
        if not self.success_url:
            self.success_url = get_model_detail_view_url(self.model, self.object.pk)
        return super().get_success_url()

    def get_submit_button_text(self) -> str:
        """
        Get submit button text.

        :return: Submit button text.
        """
        if self.submit_button_text is None:
            self.submit_button_text = 'Submit ' + get_verbose_name(self.model)
        return self.submit_button_text

    def get_breadcrumbs(self) -> dict:
        """
        Get breadcrumbs.

        :return: Breadcrumbs.
        """
        if self.breadcrumbs is None:
            self.breadcrumbs = super().get_breadcrumbs()
            try:
                self.breadcrumbs[get_verbose_name_plural(self.model)] = get_model_list_view_url(self.model)
            except:
                pass

            try:
                self.breadcrumbs[self.get_object().pk] = get_model_detail_view_url(self.model, self.get_object().pk)
            except:
                pass

            request = getattr(self, 'request', None)
            request_path = getattr(request, 'path', None)
            if request_path:
                self.breadcrumbs[self.get_page_title()] = request_path

        return self.breadcrumbs

    def get_form_class(self):
        """
        Get form class.

        :return: Form class.
        """
        if self.form_class is None:
            model_module = self.model.__module__
            form_module_str = model_module.replace('models', 'forms')
            model_form_str = self.model.__name__ + 'Form'
            form_module = import_module(form_module_str)
            self.form_class = getattr(form_module, model_form_str, modelform_factory(self.model, fields='__all__'))

        return super().get_form_class()

    def get_context_data(self, **kwargs):
        """
        Get context data.

        :param kwargs:
        :return: Context data.
        """
        context = super().get_context_data(**kwargs)
        context['form_title'] = self.get_form_title()
        context['form_method'] = self.form_method
        context['is_form_helper'] = self.get_is_form_helper()
        context['is_button_back'] = self.is_button_back
        context['back_url'] = self.get_back_url()
        context['submit_button_text'] = self.get_submit_button_text()
        context['template_form_base'] = self.template_form_base
        return context


class CreateView(BaseCreateView, ModelFormMixin):
    """
    View for creating a new object, with a response rendered by a template.
    """
    template_name: Optional[str] = get_template_path('create')

    def get_success_url(self) -> str:
        return super().get_success_url()

    def get_submit_button_text(self) -> str:
        """
        Get submit button text.

        :return: Submit button text.
        """
        if self.submit_button_text is None:
            self.submit_button_text = 'Create ' + get_verbose_name(self.model)
        return self.submit_button_text

    def get_page_title(self) -> str:
        """
        Get page title.

        :return: Page title.
        """
        if self.page_title is None:
            self.page_title = 'Create ' + get_verbose_name(self.model)
        return self.page_title


class UpdateView(BaseUpdateView, ModelFormMixin):
    """
    View for updating an object, with a response rendered by a template.
    """
    template_name: Optional[str] = get_template_path('update')

    def get_submit_button_text(self) -> str:
        """
        Get submit button text.

        :return: Submit button text.
        """
        if self.submit_button_text is None:
            self.submit_button_text = 'Update' + get_verbose_name(self.model)
        return self.submit_button_text

    def get_page_title(self) -> str:
        """
        Get page title.
        :return: Page title.
        """
        if self.page_title is None:
            self.page_title = 'Update ' + get_verbose_name(self.model)
        return self.page_title


class DetailView(BaseDetailView, ViewMixin):
    """
    View for displaying an object, with a response rendered by a template.
    """
    template_name: Optional[str] = None
    detail_card_title: Optional[str] = None
    is_button_back: Optional[bool] = True
    is_button_update: Optional[bool] = True
    is_button_delete: Optional[bool] = True
    back_url: Optional[str] = None
    update_url: Optional[str] = None
    delete_url: Optional[str] = None
    fields: Optional[Union[str, List[str]]] = None

    def get_template_name(self):
        """
        Get template name.

        :return: Template name.
        """
        if self.template_name is None:
            self.template_name = get_template_path('detail')
        return self.template_name

    def get_page_title(self) -> str:
        """
        Get page title.

        :return: Page title.
        """
        if self.page_title is None:
            self.page_title = 'Detail ' + get_verbose_name(self.model)
        return self.page_title

    def get_detail_card_title(self) -> str:
        """
        Get detail card title.

        :return: Detail card title.
        """
        if self.detail_card_title is None:
            self.detail_card_title = get_verbose_name(self.model)
        return self.detail_card_title

    def get_breadcrumbs(self) -> dict:
        """
        Get breadcrumbs.

        :return: Breadcrumbs.
        """
        if self.breadcrumbs is None:
            self.breadcrumbs = super().get_breadcrumbs()
            try:
                self.breadcrumbs[get_verbose_name_plural(self.model)] = get_model_list_view_url(self.model)
            except:
                pass

            try:
                self.breadcrumbs[self.get_object().pk] = get_model_detail_view_url(self.model, self.get_object().pk)
            except:
                pass

        return self.breadcrumbs

    def get_back_url(self) -> str:
        """
        Get back URL.

        :return: Back URL.
        """
        if not self.is_button_back:
            return ''
        if self.back_url is None:
            self.back_url = get_model_list_view_url(self.model)
        return self.back_url

    def get_update_url(self) -> str:
        """
        Get update URL.

        :return: Update URL.
        """
        if not self.is_button_update:
            return ''
        if self.update_url is None:
            self.update_url = get_model_update_view_url(self.model, self.get_object().pk)
        return self.update_url

    def get_delete_url(self) -> str:
        """
        Get delete URL.

        :return: Delete URL.
        """
        if not self.is_button_delete:
            return ''
        if self.delete_url is None:
            self.delete_url = get_model_delete_view_url(self.model, self.get_object().pk)
        return self.delete_url

    def get_fields(self) -> list:
        """
        Get fields.

        :return: Fields.
        """
        if self.fields is None:
            self.fields = '__all__'
        return self.fields

    def get_context_data(self, **kwargs):
        """
        Get context data.

        :param kwargs: kwargs.
        :return: Context data.
        """
        context = super().get_context_data(**kwargs)
        context['detail_card_title'] = self.get_detail_card_title()
        context['is_button_back'] = self.is_button_back
        context['is_button_update'] = self.is_button_update
        context['is_button_delete'] = self.is_button_delete
        context['back_url'] = self.get_back_url()
        context['update_url'] = self.get_update_url()
        context['delete_url'] = self.get_delete_url()
        context['fields'] = self.get_fields()
        return context

    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':

            setattr(self, 'object', self.get_object())
            context = {
                'object': self.object,
                'fields': self.get_fields(),
            }
            context_object_name = self.get_context_object_name(self.object)
            if context_object_name:
                context[context_object_name] = self.object
            if self.template_name is None:
                self.template_name = get_template_path('detail_ajax')
            return self.render_to_response(context)

        if self.template_name is None:
            self.template_name = get_template_path('detail')

        return super().get(request, *args, **kwargs)


class DeleteView(BaseDeleteView, ViewMixin):
    """
    View for deleting an object, with a response rendered by a template.
    """
    template_name: Optional[str] = get_template_path('delete')
    delete_card_title: Optional[str] = None
    is_button_back: Optional[bool] = True
    back_url: Optional[str] = None
    submit_button_text: Optional[str] = None
    form_method: Optional[str] = 'POST'
    template_form_base: Optional[str] = get_template_path('form')
    message_delete: Optional[str] = None

    def get_page_title(self) -> str:
        """
        Get page title.

        :return: Page title.
        """
        if self.page_title is None:
            self.page_title = 'Delete ' + get_verbose_name(self.model)
        return self.page_title

    def get_delete_card_title(self) -> str:
        """
        Get delete card title.

        :return: Delete card title.
        """
        if self.delete_card_title is None:
            self.delete_card_title = get_verbose_name(self.model)
        return self.delete_card_title

    def get_breadcrumbs(self) -> dict:
        """
        Get breadcrumbs.

        :return: Breadcrumbs.
        """
        if self.breadcrumbs is None:
            self.breadcrumbs = super().get_breadcrumbs()
            try:
                self.breadcrumbs[get_verbose_name_plural(self.model)] = get_model_list_view_url(self.model)
            except:
                pass

            try:
                self.breadcrumbs[self.get_object().pk] = get_model_detail_view_url(self.model, self.get_object().pk)
            except:
                pass

            request = getattr(self, 'request', None)
            request_path = getattr(request, 'path', None)
            if request_path:
                self.breadcrumbs[self.get_page_title()] = request_path

        return self.breadcrumbs

    def get_back_url(self) -> str:
        """
        Get back URL.

        :return: Back URL.
        """
        if not self.is_button_back:
            return ''
        if self.back_url is None:
            try:
                self.back_url = get_model_detail_view_url(self.model, self.get_object().pk)
            except:
                self.back_url = get_model_list_view_url(self.model)
        return self.back_url

    def get_submit_button_text(self) -> str:
        """
        Get submit button text.

        :return: Submit button text.
        """
        if self.submit_button_text is None:
            self.submit_button_text = 'Delete' + get_verbose_name(self.model)
        return self.submit_button_text

    def get_message_delete(self) -> str:
        """
        Get message delete.

        :return: Message delete.
        """
        if self.message_delete is None:
            self.message_delete = f'Are you sure you want to delete {self.object}?'
        return self.message_delete

    def get_success_url(self):
        """
        Get success URL.

        :return: Success URL.
        """
        if not self.success_url:
            self.success_url = get_model_list_view_url(self.model)
        return super().get_success_url()

    def get_context_data(self, **kwargs):
        """
        Get context data.

        :param kwargs: kwargs.
        :return: Context data.
        """
        context = super().get_context_data(**kwargs)
        context['delete_card_title'] = self.get_delete_card_title()
        context['is_button_back'] = self.is_button_back
        context['back_url'] = self.get_back_url()
        context['submit_button_text'] = self.get_submit_button_text()
        context['form_method'] = self.form_method
        context['template_form_base'] = self.template_form_base
        context['message_delete'] = self.get_message_delete()
        return context

    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            setattr(self, 'object', self.get_object())
            data = {
                'title': self.get_page_title(),
                'message': self.get_message_delete(),
            }
            return JsonResponse(data)

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            setattr(self, 'object', self.get_object())
            form = self.get_form()
            if form.is_valid():
                self.object.delete()
                data = {
                    'message': 'Deleted successfully',
                }
                status = 200
            else:
                data = {
                    'message': 'Error deleting',
                }
                status = 400
            return JsonResponse(data, status=status)

        return super().post(request, *args, **kwargs)


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
        Get page title.

        :return: Page title.
        """
        if self.page_title is None:
            self.page_title = 'List ' + get_verbose_name_plural(self.model)
        return self.page_title

    def get_table_title(self) -> str:
        """
        Get table title.
        :return: Table title.
        """
        if self.table_title is None:
            self.table_title = get_verbose_name_plural(self.model)
        return self.table_title

    def get_button_create(self) -> bool:
        """
        Get button create.

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
                self.breadcrumbs[get_verbose_name_plural(self.model)] = get_model_list_view_url(self.model)
            except:
                pass

        return self.breadcrumbs

    def get_create_url(self) -> str:
        """
        Get create URL.

        :return: Create URL.
        """
        if not self.is_button_create:
            return ''
        if self.create_url is None:
            self.create_url = get_model_create_view_url(self.model)
        return self.create_url

    def get_fields(self) -> list:
        """
        Get fields.
        :return: Fields.
        """
        if self.fields is None:
            self.fields = '__all__'
        return self.fields

    def get_actions(self) -> dict:
        """
        Get actions.

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
        Get ordering.

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
        Paginate queryset.

        :return: Paginate queryset.
        """
        try:
            return super().paginate_queryset(queryset, page_size)
        except Exception as e:
            page_kwarg = self.page_kwarg
            page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
            try:
                page_number = int(page)
            except ValueError:
                raise e

        paginator = self.get_paginator(
            queryset,
            page_size,
            orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty(),
        )
        if page_number > paginator.num_pages:
            page_number = paginator.num_pages

        try:
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


def create_view_factory(
        model,
        form_class: Optional[Union[str, List[str]]] = None,
        success_url: Optional[str] = None,
        title: Optional[str] = None,
        page_lang: Optional[str] = None,
        page_title: Optional[str] = None,
        template_base: Optional[str] = None,
        breadcrumbs: Optional[dict] = None,
        form_title: Optional[str] = None,
        is_form_helper: Optional[bool] = None,
        is_button_back: Optional[bool] = True,
        back_url: Optional[str] = None,
        submit_button_text: Optional[str] = None,
        template_form_base: Optional[str] = get_template_path('form'),
        template_name: Optional[str] = get_template_path('create'),
        view_class: type[CreateView] = CreateView,
        **kwargs
):
    """
    Create view factory.

    :param model: Model.
    :param form_class: Form class.
    :param success_url: Success URL.
    :param title: Title.
    :param page_lang: Page language.
    :param page_title: Page title.
    :param template_base: Template base.
    :param breadcrumbs: Breadcrumbs.
    :param form_title: Form title.
    :param is_form_helper: Is form helper.
    :param is_button_back: Is button back.
    :param back_url: Back URL.
    :param submit_button_text: Submit button text.
    :param template_form_base: Template form base.
    :param template_name: Template name.
    :param view_class: View class.
    :param kwargs:
    :return: Create view.
    """

    return type(
        f'{model.__name__}CreateView',
        (view_class,),
        {
            'model': model,
            'form_class': form_class,
            'success_url': success_url,
            'title': title,
            'page_lang': page_lang,
            'page_title': page_title,
            'template_base': template_base,
            'breadcrumbs': breadcrumbs,
            'form_title': form_title,
            'is_form_helper': is_form_helper,
            'is_button_back': is_button_back,
            'back_url': back_url,
            'submit_button_text': submit_button_text,
            'template_form_base': template_form_base,
            'template_name': template_name,
            **kwargs
        }
    )


def update_view_factory(
        model,
        form_class: Optional[Union[str, List[str]]] = None,
        success_url: Optional[str] = None,
        title: Optional[str] = None,
        page_lang: Optional[str] = None,
        page_title: Optional[str] = None,
        template_base: Optional[str] = None,
        breadcrumbs: Optional[dict] = None,
        form_title: Optional[str] = None,
        is_form_helper: Optional[bool] = None,
        is_button_back: Optional[bool] = True,
        back_url: Optional[str] = None,
        submit_button_text: Optional[str] = None,
        template_form_base: Optional[str] = get_template_path('form'),
        template_name: Optional[str] = get_template_path('update'),
        view_class: type[UpdateView] = UpdateView,
        **kwargs
):
    """
    Update view factory.

    :param model: Model.
    :param form_class: Form class.
    :param success_url: Success URL.
    :param title: Title.
    :param page_lang: Page language.
    :param page_title: Page title.
    :param template_base: Template base.
    :param breadcrumbs: Breadcrumbs.
    :param form_title: Form title.
    :param is_form_helper: Is form helper.
    :param is_button_back: Is button back.
    :param back_url: Back URL.
    :param submit_button_text: Submit button text.
    :param template_form_base: Template form base.
    :param template_name: Template name.
    :param view_class: View class.
    :param kwargs:
    :return: Update view.
    """

    return type(
        f'{model.__name__}UpdateView',
        (view_class,),
        {
            'model': model,
            'form_class': form_class,
            'success_url': success_url,
            'title': title,
            'page_lang': page_lang,
            'page_title': page_title,
            'template_base': template_base,
            'breadcrumbs': breadcrumbs,
            'form_title': form_title,
            'is_form_helper': is_form_helper,
            'is_button_back': is_button_back,
            'back_url': back_url,
            'submit_button_text': submit_button_text,
            'template_form_base': template_form_base,
            'template_name': template_name,
            **kwargs,
        }
    )


def detail_view_factory(
        model,
        template_name: Optional[str] = None,
        title: Optional[str] = None,
        page_lang: Optional[str] = None,
        page_title: Optional[str] = None,
        template_base: Optional[str] = None,
        breadcrumbs: Optional[dict] = None,
        detail_card_title: Optional[str] = None,
        is_button_back: Optional[bool] = True,
        is_button_update: Optional[bool] = True,
        is_button_delete: Optional[bool] = True,
        back_url: Optional[str] = None,
        update_url: Optional[str] = None,
        delete_url: Optional[str] = None,
        fields: Optional[Union[str, List[str]]] = None,
        view_class: type[DetailView] = DetailView,
        **kwargs,
):
    """
    Detail view factory.

    :param model:
    :param template_name:
    :param title:
    :param page_lang:
    :param page_title:
    :param template_base:
    :param breadcrumbs:
    :param detail_card_title:
    :param is_button_back:
    :param is_button_update:
    :param is_button_delete:
    :param back_url:
    :param update_url:
    :param delete_url:
    :param fields:
    :param view_class:
    :param kwargs:
    :return: Detail view.
    """

    return type(
        f'{model.__name__}DetailView',
        (view_class,),
        {
            'model': model,
            'template_name': template_name,
            'title': title,
            'page_lang': page_lang,
            'page_title': page_title,
            'template_base': template_base,
            'breadcrumbs': breadcrumbs,
            'detail_card_title': detail_card_title,
            'is_button_back': is_button_back,
            'is_button_update': is_button_update,
            'is_button_delete': is_button_delete,
            'back_url': back_url,
            'update_url': update_url,
            'delete_url': delete_url,
            'fields': fields,
            **kwargs,
        }
    )


def delete_view_factory(
        model,
        template_name: Optional[str] = get_template_path('delete'),
        title: Optional[str] = None,
        page_lang: Optional[str] = None,
        page_title: Optional[str] = None,
        template_base: Optional[str] = None,
        breadcrumbs: Optional[dict] = None,
        delete_card_title: Optional[str] = None,
        is_button_back: Optional[bool] = True,
        back_url: Optional[str] = None,
        submit_button_text: Optional[str] = None,
        form_method: Optional[str] = 'POST',
        template_form_base: Optional[str] = get_template_path('form'),
        message_delete: Optional[str] = None,
        view_class: type[DeleteView] = DeleteView,
        **kwargs,
):
    """
    Delete view factory.

    :param model:
    :param template_name:
    :param title:
    :param page_lang:
    :param page_title:
    :param template_base:
    :param breadcrumbs:
    :param delete_card_title:
    :param is_button_back:
    :param back_url:
    :param submit_button_text:
    :param form_method:
    :param template_form_base:
    :param message_delete:
    :param view_class:
    :param kwargs:
    :return: Delete view.
    """

    return type(
        f'{model.__name__}DeleteView',
        (view_class,),
        {
            'model': model,
            'template_name': template_name,
            'title': title,
            'page_lang': page_lang,
            'page_title': page_title,
            'template_base': template_base,
            'breadcrumbs': breadcrumbs,
            'delete_card_title': delete_card_title,
            'is_button_back': is_button_back,
            'back_url': back_url,
            'submit_button_text': submit_button_text,
            'form_method': form_method,
            'template_form_base': template_form_base,
            'message_delete': message_delete,
            **kwargs,
        }
    )


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
    List view factory.

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
