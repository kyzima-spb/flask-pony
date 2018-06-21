.. _views:

Сменные представления
=====================

В ``Flask-Pony`` встроены представления для простых CRUD-операций.
Если вы не знаете, что такое CRUD, то поясню, это операции: создания, редактирования, удаления и чтения.

Эти представления, основанны на классах.
Имена классов и некоторых свойств заимствованы из фреймворка Django_, но не являются копией и работают по своему.

Все представления используют репозиторий, для работы с сущностями.
Необходимо переопределить статическое свойство :py:attr:`~views.EntityView.repository_class`, которое содержит ссылку на класс репозиторий.

Смотрите примеры ниже, для более подробного описания каждого конкретного представления.

@route
------

Если вы используете представления, базирующиеся на классах,
то должны знать, что класс, нужно сконвертировать в функцию с помощью метода :py:meth:`~flask.views.View.as_view`,
а далее с помощью метода :py:meth:`~flask.Blueprint.add_url_rule` добавить новый маршрут в ваше приложение.

.. code-block:: python

    app.add_url_rule('/categories',
                     view_func=CategoryList.as_view('category_list'))

Я решил создать для этой задачи декоратор :py:func:`~decorators.route`.
Он может автоматически сгенерировать имя нового маршрута (точки входа).
Если у вас есть причины считать, что это не будет работать в некоторых случаях, то напишите мне.

Декоратор принимает два обязательных аргумента: ссылка на приложение (blueprint) и маршрут:

.. code-block:: python

    from flask import MethodView
    from flask_pony.decorators import route

    from . import app

    @route(app, '/categories')
    class CategoryList(MethodView):
        pass


ListView
--------

Для вывода сущностей в виде списка, используется представление :py:class:`views.ListView`.

.. code-block:: python

    from flask_pony.views import ListView
    from flask_pony.decorators import route

    from . import app
    from .repositories import CategoryRepository


    @route(app, '/categories')
    class CategoryList(ListView):
        repository_class = CategoryRepository


    # если без декоратора
    # app.add_url_rule('/categories',
    #                  view_func=CategoryList.as_view('category_list'))

В шаблон будет передана переменная ``entities`` - коллекция сущностей.

.. sourcecode:: html+jinja

    {# templates/category/list.html #}

    {% extends "layouts/base.html" %}

    {% block page_title %}Категории{% endblock %}

    {% block page_content %}
        {% for entity in entities %}
            <li>{{ entity.title }}</li>
        {% endfor %}
    {% endblock %}


ShowView
--------

Для вывода подробной информации об одной сущности, используется представление :py:class:`views.ShowView`.
Маршрут должен содержать один параметр ``id`` - идентификатор сущности.

В том случае, если сущность не найдена в базе данных, будет возвращен код ``404``.

.. code-block:: python

    from flask_pony.views import ShowView
    from flask_pony.decorators import route

    from . import app
    from .repositories import CategoryRepository


    @route(app, '/category/<int:id>')
    class CategoryShow(ShowView):
        repository_class = CategoryRepository


В шаблон будет передана переменная ``entity``.

.. sourcecode:: html+jinja

    {# templates/category/show.html #}

    {% extends "layouts/base.html" %}

    {% block page_title %}{{ entity.title }}{% endblock %}


CreateView
----------

Для создания (добавления) новой сущности, используется представление :py:class:`views.CreateView`.

После успешного создания сущности, необходимо сделать обязательный редирект.
Он необходим для защиты от повторной отправки формы клавишей ``F5``.
Для этого необходимо переопределить статическое свойство :py:attr:`~views.ProcessFormView.success_endpoint`.

.. code-block:: python

    from flask_pony.views import CreateView
    from flask_pony.decorators import route

    from . import app
    from .repositories import CategoryRepository


    @route(app, '/category/add')
    class CategoryCreate(CreateView):
        repository_class = CategoryRepository
        success_endpoint = 'category_update'

В шаблон будет передана переменная ``form``. Вы можете отрисовать форму вручную или воспользоваться сторонними макросами.
Например, ``quick_form`` из Flask-Bootstrap_

.. sourcecode:: html+jinja

    {# templates/category/create.html #}

    {% extends "layouts/base.html" %}
    {% import "bootstrap/wtf.html" as wtf %}

    {% block page_title %}Добавить категорию{% endblock %}

    {% block page_content %}
        {{ wtf.quick_form(form) }}
    {% endblock %}


UpdateView
----------

Для редактирования сущности, используется представление :py:class:`views.UpdateView`.
Свойства такие же, как у ``CreateView``, только маршрут должен содержать один параметр ``id`` - идентификатор сущности.

В том случае, если сущность не найдена в базе данных, будет возвращен код ``404``.

.. code-block:: python

    from flask_pony.views import UpdateView
    from flask_pony.decorators import route

    from . import app
    from .repositories import CategoryRepository


    @route(app, '/category/edit/<int:id>')
    class CategoryUpdate(UpdateView):
        repository_class = CategoryRepository
        success_endpoint = 'category_update'

В шаблон будут переданы переменные ``entity`` и ``form``.

.. sourcecode:: html+jinja

    {# templates/category/update.html #}

    {% extends "layouts/base.html" %}
    {% import "bootstrap/wtf.html" as wtf %}

    {% block page_title %}
        Изменить категорию {{ entity.title }}
    {% endblock %}

    {% block page_content %}
        {{ wtf.quick_form(form) }}
    {% endblock %}


DeleteView
----------

Для удаления сущности, используется представление :py:class:`views.DeleteView`.
Свойства такие же, как у ``CreateView``, только маршрут должен содержать один параметр ``id`` - идентификатор сущности.

.. code-block:: python

    from flask_pony.views import DeleteView
    from flask_pony.decorators import route

    from . import app
    from .repositories import CategoryRepository


    @route(app, '/category/delete/<int:id>')
    class CategoryDelete(DeleteView):
        repository_class = repositories.CategoryRepository
        success_endpoint = 'category_list'

Это представление доступно только методом ``POST``.


.. _Django: https://www.djangoproject.com
.. _Flask-Bootstrap: https://pythonhosted.org/Flask-Bootstrap/
