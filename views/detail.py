
from typing import Optional, Union, List

from django.views.generic import DetailView as BaseDetailView

from django_auto_crud.utils.views import get_verbose_name, get_model_detail_view_url, \
    get_verbose_name_plural, \
    get_model_list_view_url, get_model_update_view_url, get_model_delete_view_url, get_template_path
from .mixins import ViewMixin


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
        Get template name. If not defined, get it from settings in TEMPLATE_PATHS['detail'].

        :return: Template name.
        """
        if self.template_name is None:
            self.template_name = get_template_path('detail')
        return self.template_name

    def get_page_title(self) -> str:
        """
        Get page title. If not defined, get verbose name of the model.

        :return: Page title.
        """
        if self.page_title is None:
            self.page_title = 'Detail ' + get_verbose_name(self.model)
        return self.page_title

    def get_detail_card_title(self) -> str:
        """
        Get detail card title. If not defined, get verbose name of the model.

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
                # Add model list view URL to breadcrumbs
                self.breadcrumbs[get_verbose_name_plural(self.model)] = get_model_list_view_url(self.model)
            except:
                pass

            try:
                # Add model detail view URL to breadcrumbs
                self.breadcrumbs[self.get_object().pk] = get_model_detail_view_url(self.model, self.get_object().pk)
            except:
                pass

        return self.breadcrumbs

    def get_back_url(self) -> str:
        """
        Get back URL. If not defined, get the list view URL of the model.

        :return: Back URL.
        """
        if not self.is_button_back:
            # If the back button is not enabled, return an empty string
            return ''
        if self.back_url is None:
            self.back_url = get_model_list_view_url(self.model)
        return self.back_url

    def get_update_url(self) -> str:
        """
        Get update URL. If not defined, get the update view URL of the object.

        :return: Update URL.
        """
        if not self.is_button_update:
            # If the update button is not enabled, return an empty string
            return ''
        if self.update_url is None:
            self.update_url = get_model_update_view_url(self.model, self.get_object().pk)
        return self.update_url

    def get_delete_url(self) -> str:
        """
        Get delete URL. If not defined, get the delete view URL of the object.

        :return: Delete URL.
        """
        if not self.is_button_delete:
            # If the delete button is not enabled, return an empty string
            return ''
        if self.delete_url is None:
            self.delete_url = get_model_delete_view_url(self.model, self.get_object().pk)
        return self.delete_url

    def get_fields(self) -> list:
        """
        Get fields. If not defined, return '__all__'.

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
        """
        Get method. If the request is an AJAX request, return a JSON response with the object data.
        """
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
    Detail view factory. Create a view class with the specified parameters.

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
