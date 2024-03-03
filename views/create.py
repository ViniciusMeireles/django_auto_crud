from typing import Optional, Union, List

from django.views.generic import CreateView as BaseCreateView

from django_auto_crud.utils.views import get_verbose_name, get_template_path
from .mixins import ModelFormMixin


class CreateView(BaseCreateView, ModelFormMixin):
    """
    View for creating a new object, with a response rendered by a template.
    """
    template_name: Optional[str] = get_template_path('create')

    def get_success_url(self) -> str:
        return super().get_success_url()

    def get_submit_button_text(self) -> str:
        """
        Get submit button text. If not defined, return 'Submit' + verbose name of the model.

        :return: Submit button text.
        """
        if self.submit_button_text is None:
            self.submit_button_text = 'Create ' + get_verbose_name(self.model)
        return self.submit_button_text

    def get_page_title(self) -> str:
        """
        Get page title. If not defined, get verbose name of the model.

        :return: Page title.
        """
        if self.page_title is None:
            self.page_title = 'Create ' + get_verbose_name(self.model)
        return self.page_title


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
    Create view factory. Create a view class with the specified parameters.

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
