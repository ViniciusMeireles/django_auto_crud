
# Django AdminLTE

Django AdminLTE is a library that simplifies the development of systems in Django by utilizing the AdminLTE theme to customize generic views such as CreateView, UpdateView, DeleteView, DetailView, and ListView.


## Install

Currently, Django AdminLTE is in the early stages of development and is not available on PyPI for installation via pip. However, you can follow the steps below to incorporate the library into your project:

1. Clone this repository to the desired directory on your system:

```bash
git clone https://github.com/ViniciusMeireles/django_adminlte.git
```

2. Copy the "django_adminlte" folder to the root directory of your Django project.
3. In your Django settings, add 'django_adminlte' to the INSTALLED_APPS:

```python
# settings.py

INSTALLED_APPS = [
    # ... other installed apps
    'django_adminlte',
]
```

4. Add all the apps from your project to the LOCAL_APPS list and append it to INSTALLED_APPS, as shown in the example below:

```python
# settings.py

INSTALLED_APPS = [
    # ... other installed apps
    'django_adminlte',
]

LOCAL_APPS = [
    'your_app1',
    'your_app2',
    # ... add other local apps
]

INSTALLED_APPS += LOCAL_APPS
``` 

5. Next, set the path name for the home page. For example, 'home' or 'myapp:home':

```python
# settings.py

HOME_PATH_NAME = 'myapp:home'  # Replace 'myapp:home' with your desired home page path
```

6. Here are some other optional configurations you may want to consider:

```python
# settings.py

# Django AdminLTE Optional Settings
# The language for the site.
LANGUAGE_SITE = 'en'
# Directory where the theme is located.
STATIC_THEME = 'django_adminlte/adminlte_3_2_0/'
# Directory where the logo is located.
STATIC_LOGO = 'django_adminlte/images/Django AdminLTE Logo.png'
# Directory where the favicon is located.
STATIC_FAVICON = 'django_adminlte/images/favicon.webp'
# Name of the site.
SITE_NAME = "Django AdminLTE"
# Directories where each template is located.
TEMPLATE_PATHS = {
    'base': 'django_adminlte/theme/base.html',
    'list': 'django_adminlte/crud/list.html',
    'create': 'django_adminlte/crud/create.html',
    'detail': 'django_adminlte/crud/detail.html',
    'detail_ajax': 'django_adminlte/crud/detail_ajax.html',
    'update': 'django_adminlte/crud/update.html',
    'delete': 'django_adminlte/crud/delete.html',
    'form': 'django_adminlte/crud/form.html',
    'navbar_left': None,
    'navbar_right': None,
    'sidebar_itens': None,
}
```
## Usage/Examples

1. Create your app

```bash
python manage.py startapp myapp
```

2. Open the models.py file in your app directory (myapp/models.py) and define your models. For example:

```python
from django.db import models


class Person(models.Model):
    """
    Person model.
    """
    name = models.CharField(max_length=50, verbose_name='Full name')
    age = models.PositiveIntegerField(verbose_name='Age')
    phone = models.CharField(max_length=50, verbose_name='Phone number')
    email = models.EmailField(max_length=50, verbose_name='Email address')
    job_title = models.CharField(max_length=50, verbose_name='Job title')
    date_created = models.DateTimeField(auto_now_add=True, verbose_name='Date created')

    def __str__(self):
        return self.name

```

3. Open the settings.py file in your project directory (project_name/settings.py) and add your app's name to the LOCAL_APPS list:

```python
# settings.py

LOCAL_APPS = [
    'myapp',
    # ... add other local apps
]
```

4. Run the following commands to create migrations and apply them to the database:

```bash
python manage.py makemigrations
python manage.py migrate
```

5. Open the views.py file in your app directory (myapp/views.py) and define the home function. For example:

```python
# views.py

from django.shortcuts import render

from django_adminlte.utils.views import get_template_path


def home(request):
    return render(request=request, template_name=get_template_path('base'))
```

6. Create a new file named urls.py in your app directory (myapp/urls.py) and define the URL patterns for your app:

```python
from django.urls import path

from django_adminlte.utils.urls import generate_crud_urlpatterns
from . import views
from .models import Person

app_name = 'myapp'

urlpatterns = [
    path('', views.home, name='home'),
]

# CRUD URLs form Models
urlpatterns += generate_crud_urlpatterns([Person])

```

7. Open the urls.py file in your project's main directory (project_name/urls.py) and include the URL patterns from myapp.urls:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django Admin URLs
    path('admin/', admin.site.urls),

    # Local App URLs
    path('', include('myapp.urls')),
    # ... other URL patterns ...
]

```

8. Open the settings.py file in your project directory (project_name/settings.py) and add your home's name to the HOME_PATH_NAME:

```python
# settings.py

HOME_PATH_NAME = 'myapp:home'  # Replace 'myapp:home' with your desired home page path
```

9. Run the development server:
```bash
python manage.py runserver 8000
```
## Contribution

Contributions are always welcome!

If you would like to contribute to this project, follow these steps:

1. Fork the repository.
2. Create a branch for your changes: git checkout -b feature/new-feature.
3. Commit your changes: git commit -m "Add new feature".
4. Push to your branch: git push origin feature/new-feature.
5. Open a Pull Request.
