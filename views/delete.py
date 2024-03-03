from typing import Optional

from django.http import JsonResponse
from django.views.generic import DeleteView as BaseDeleteView

from django_auto_crud.utils.views import get_verbose_name, get_model_detail_view_url, \
    get_verbose_name_plural, get_model_list_view_url, get_template_path
from .mixins import ViewMixin


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
        Get page title. If not defined, get verbose name of the model.

        :return: Page title.
        """
        if self.page_title is None:
            self.page_title = 'Delete ' + get_verbose_name(self.model)
        return self.page_title

    def get_delete_card_title(self) -> str:
        """
        Get delete card title. If not defined, get verbose name of the model.

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
                # Add the list view URL of the model to the breadcrumbs
                self.breadcrumbs[get_verbose_name_plural(self.model)] = get_model_list_view_url(self.model)
            except:
                pass

            try:
                # Add the detail view URL of the object to the breadcrumbs
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
        Get back URL. If not defined, get the detail view URL of the object.

        :return: Back URL.
        """
        if not self.is_button_back:
            # If the back button is not enabled, return an empty string
            return ''
        if self.back_url is None:
            try:
                # Try to get the detail view URL of the object
                self.back_url = get_model_detail_view_url(self.model, self.get_object().pk)
            except:
                # If the object does not exist, get the list view URL of the model
                self.back_url = get_model_list_view_url(self.model)
        return self.back_url

    def get_submit_button_text(self) -> str:
        """
        Get submit button text. If not defined, return 'Delete' + verbose name of the model.

        :return: Submit button text.
        """
        if self.submit_button_text is None:
            self.submit_button_text = 'Delete' + get_verbose_name(self.model)
        return self.submit_button_text

    def get_message_delete(self) -> str:
        """
        Get message delete. If not defined, return 'Are you sure you want to delete {object}?'.

        :return: Message delete.
        """
        if self.message_delete is None:
            self.message_delete = f'Are you sure you want to delete {self.object}?'
        return self.message_delete

    def get_success_url(self):
        """
        Get success URL. If not defined, get the list view URL of the model.

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
        """
        Get method. If the request is AJAX, return a JSON response. Otherwise, return the default response.
        """
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            setattr(self, 'object', self.get_object())
            data = {
                'title': self.get_page_title(),
                'message': self.get_message_delete(),
            }
            return JsonResponse(data)

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Post method. If the request is AJAX, return a JSON response. Otherwise, return the default response.
        """
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
    Delete view factory. Create a view class with the specified parameters.

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
