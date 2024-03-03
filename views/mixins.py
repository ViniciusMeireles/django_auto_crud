from importlib import import_module
from typing import Optional

from django.conf import settings
from django.forms import modelform_factory
from django.views.generic.base import ContextMixin
from django.views.generic.edit import ModelFormMixin as BaseModelFormMixin

from django_auto_crud.utils.views import get_home_url, get_verbose_name, get_model_detail_view_url, \
    get_verbose_name_plural, get_model_list_view_url, get_template_path


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
        Get page language on settings or default language code.

        :return: Page language | en, pt-BR.
        """
        if self.page_lang is None:
            try:
                self.page_lang = settings.LANGUAGE_SITE
            except:
                self.page_lang = settings.LANGUAGE_CODE
        return self.page_lang

    def get_page_title(self) -> str:
        """
        Get page title. If not defined, return empty string.

        :return: Page title or empty string.
        """
        if self.page_title is None:
            self.page_title = ''
        return self.page_title

    def get_title(self) -> str:
        """
        Get title. If not defined, get page title.

        :return: Title or page title.
        """
        if self.title is None:
            self.title = self.get_page_title()
        return self.title

    def get_breadcrumbs(self) -> dict:
        """
        Get breadcrumbs. If not defined, return home URL.

        :return: Breadcrumbs.
        """
        if self.breadcrumbs is None:
            self.breadcrumbs = {
                'Home': get_home_url(),
            }
        return self.breadcrumbs

    def get_user_name(self):
        """
        Get name user. If not authenticated, return '[Anonymous]'.

        :return: Name user.
        """
        request = getattr(self, 'request', None)
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            return user.get_full_name()
        return '[Anonymous]'

    def get_left_navbar_template(self) -> str:
        """
        Get left navbar template on settings.

        :return: Left navbar template.
        """
        if self.left_navbar_template is None:
            self.left_navbar_template = get_template_path('navbar_left')
        return self.left_navbar_template

    def get_right_navbar_template(self) -> str:
        """
        Get right navbar template on settings.

        :return: Right navbar template.
        """
        if self.right_navbar_template is None:
            self.right_navbar_template = get_template_path('navbar_right')
        return self.right_navbar_template

    def get_sidebar_itens_template(self) -> str:
        """
        Get sidebar itens template on settings.

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
        context.update({
            'page_lang': self.get_page_lang(),
            'page_title': self.get_page_title(),
            'title': self.get_title(),
            'template_base': self.template_base if self.template_base else get_template_path('base'),
            'breadcrumbs': self.get_breadcrumbs(),
            'site_url': get_home_url(),
            'user_name': self.get_user_name(),
            'left_navbar_template': self.get_left_navbar_template(),
            'right_navbar_template': self.get_right_navbar_template(),
            'sidebar_itens_template': self.get_sidebar_itens_template(),
        })
        try:
            context['site_title'] = settings.SITE_NAME
        except:
            pass
        return context


class ModelFormMixin(BaseModelFormMixin, ViewMixin):
    """
    Mixin for model form.
    """
    form_title: Optional[str] = None
    form_method: Optional[str] = 'POST'
    is_form_helper: Optional[bool] = None

    is_button_back: Optional[bool] = True
    back_url: Optional[str] = None
    submit_button_text: Optional[str] = None
    template_form_base: Optional[str] = get_template_path('form')

    def get_form_title(self) -> str:
        """
        Get form title. If not defined, get verbose name of the model.

        :return: Form title.
        """
        if self.form_title is None:
            self.form_title = get_verbose_name(self.model)
        return self.form_title

    def get_page_title(self) -> str:
        """
        Get page title. If not defined, get verbose name of the model.

        :return: Page title.
        """
        if self.page_title is None:
            self.page_title = get_verbose_name(self.model)
        return self.page_title

    def get_is_form_helper(self) -> bool:
        """
        Get is form helper. If not defined, check if form class has helper attribute.

        :return: Is form helper.
        """
        if self.is_form_helper is None:
            self.is_form_helper = hasattr(self.get_form_class(), 'helper')
        return self.is_form_helper

    def get_back_url(self) -> str:
        """
        Get back URL. If not defined, try to get the detail view URL of the object.

        :return: Back URL
        """
        if not self.is_button_back:
            return ''
        if self.back_url is None:
            try:
                # Try to get the detail view URL of the object
                self.back_url = get_model_detail_view_url(self.model, self.get_object().pk)
            except:
                # If the object does not exist, get the list view URL of the model
                self.back_url = get_model_list_view_url(self.model)
        return self.back_url

    def get_success_url(self) -> str:
        """
        Get success URL. If not defined, get the detail view URL of the object.

        :return: Success URL.
        """
        if not self.success_url:
            self.success_url = get_model_detail_view_url(self.model, self.object.pk)
        return super().get_success_url()

    def get_submit_button_text(self) -> str:
        """
        Get submit button text. If not defined, return 'Submit' + verbose name of the model.

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
                # Add model list view URL to breadcrumbs
                self.breadcrumbs[get_verbose_name_plural(self.model)] = get_model_list_view_url(self.model)
            except:
                pass

            try:
                # Add model detail view URL to breadcrumbs
                self.breadcrumbs[self.get_object().pk] = get_model_detail_view_url(self.model, self.get_object().pk)
            except:
                pass

            # Get current request path and add to breadcrumbs
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
            # Module of the form class based on the module of the model
            form_module_str = model_module.replace('models', 'forms')
            # Name of the form class is the name of the model + 'Form'
            model_form_str = self.model.__name__ + 'Form'
            try:
                form_module = import_module(form_module_str)
            except:
                # If form module does not exist, create a form class with all fields
                self.form_class = modelform_factory(self.model, fields='__all__')
            else:
                # Get the form class from the form module or create a form class with all fields
                self.form_class = getattr(form_module, model_form_str, modelform_factory(self.model, fields='__all__'))

        return super().get_form_class()

    def get_context_data(self, **kwargs):
        """
        Get context data.

        :param kwargs:
        :return: Context data.
        """
        context = super().get_context_data(**kwargs)
        context.update({
            'form_title': self.get_form_title(),
            'form_method': self.form_method,
            'is_form_helper': self.get_is_form_helper(),
            'is_button_back': self.is_button_back,
            'back_url': self.get_back_url(),
            'submit_button_text': self.get_submit_button_text(),
            'template_form_base': self.template_form_base,
        })
        return context
