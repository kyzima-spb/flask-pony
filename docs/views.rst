.. _views:

Pluggable Views
===============

``Flask-Pony`` has built-in views for simple CRUD-operations.

*CRUD: creating, editing, deleting and reading*

This views are based on classes. Names of classes and some properties are borrowed from the Django_ framework, but aren't copies and work separately.

All views use repository to work with entities.
Static property :py:attr:`~flask_pony.views.EntityMixin.repository_class`, which contains a reference to repository class, should be redefined.

Detailed description of each view is given below.

@route
------

If class-based views are used, then class should be converted in function by method :py:meth:`~flask.views.View.as_view`. 
Then new route should be added in application by method :py:meth:`~flask.Blueprint.add_url_rule`.

.. code-block:: python

    app.add_url_rule('/categories',
                     view_func=CategoryList.as_view('category_list'))

I create a decorator :py:func:`~flask_pony.decorators.route` for this task.
It can automatically generate the name for new route (entry point)/
If you have reasons to considering that it not workable in some cases, please write me.

Decorator takes 2 mandatory arguments: application reference (blueprint) and route:

.. code-block:: python

    from flask import MethodView
    from flask_pony.decorators import route

    from . import app

    @route(app, '/categories')
    class CategoryList(MethodView):
        pass


ListView
--------


The view is using for displaying entities as a list :py:class:`~flask_pony.views.ListView`.

.. code-block:: python

    from flask_pony.views import ListView
    from flask_pony.decorators import route

    from . import app
    from .repositories import CategoryRepository


    @route(app, '/categories')
    class CategoryList(ListView):
        repository_class = CategoryRepository


    # without a decorator
    # app.add_url_rule('/categories',
    #                  view_func=CategoryList.as_view('category_list'))

A variable ``entities`` (entity collection) will be passed into the template.

.. sourcecode:: html+jinja

    {# templates/category/list.html #}

    {% extends "layouts/base.html" %}

    {% block page_title %}Categories{% endblock %}

    {% block page_content %}
        {% for entity in entities %}
            <li>{{ entity.title }}</li>
        {% endfor %}
    {% endblock %}


ShowView
--------

For displaying a detailed description about one entity is using the view :py:class:`~flask_pony.views.ShowView`.
The route must contain one parameter ``id`` - entity identifier.

If an entity isn't found in the database then the code ``404`` will be returned.

.. code-block:: python

    from flask_pony.views import ShowView
    from flask_pony.decorators import route

    from . import app
    from .repositories import CategoryRepository


    @route(app, '/category/<int:id>')
    class CategoryShow(ShowView):
        repository_class = CategoryRepository


A variable ``entity`` will be passed into the template.

.. sourcecode:: html+jinja

    {# templates/category/show.html #}

    {% extends "layouts/base.html" %}

    {% block page_title %}{{ entity.title }}{% endblock %}


CreateView
----------

For creating a new entity is using the view :py:class:`~flask_pony.views.CreateView`.

If an entity successfully created, is necessary to do a mandatory redirecting.
It is necessary to protect from resending the form by pressing the key `` F5``.
Static property :py:attr:`~flask_pony.views.FormMixin.success_endpoint`, should be redefined for that.

.. code-block:: python

    from flask_pony.views import CreateView
    from flask_pony.decorators import route

    from . import app
    from .repositories import CategoryRepository


    @route(app, '/category/add')
    class CategoryCreate(CreateView):
        repository_class = CategoryRepository
        success_endpoint = 'category_update'

A variable ``form`` will be passed into the template.
You can display form manually or use third-party macros.
For instance, ``quick_form`` from Flask-Bootstrap_

.. sourcecode:: html+jinja

    {# templates/category/create.html #}

    {% extends "layouts/base.html" %}
    {% import "bootstrap/wtf.html" as wtf %}

    {% block page_title %}Add category{% endblock %}

    {% block page_content %}
        {{ wtf.quick_form(form) }}
    {% endblock %}


UpdateView
----------

For editing an entity is using the view :py:class:`~flask_pony.views.UpdateView`.
The properties are the same as for `` CreateView``, only the route must contain one parameter `` id`` - entity identifier.

If an entity isn't found in the database then the code ``404`` will be returned.

.. code-block:: python

    from flask_pony.views import UpdateView
    from flask_pony.decorators import route

    from . import app
    from .repositories import CategoryRepository


    @route(app, '/category/edit/<int:id>')
    class CategoryUpdate(UpdateView):
        repository_class = CategoryRepository
        success_endpoint = 'category_update'

Variables ``entity`` and ``form`` will be passed into the template.

.. sourcecode:: html+jinja

    {# templates/category/update.html #}

    {% extends "layouts/base.html" %}
    {% import "bootstrap/wtf.html" as wtf %}

    {% block page_title %}
        Change category {{ entity.title }}
    {% endblock %}

    {% block page_content %}
        {{ wtf.quick_form(form) }}
    {% endblock %}


DeleteView
----------

For deleting an entity is using the view :py:class:`~flask_pony.views.DeleteView`.
The properties are the same as for `` CreateView``, only the route must contain one parameter `` id`` - entity identifier.

.. code-block:: python

    from flask_pony.views import DeleteView
    from flask_pony.decorators import route

    from . import app
    from .repositories import CategoryRepository


    @route(app, '/category/delete/<int:id>')
    class CategoryDelete(DeleteView):
        repository_class = repositories.CategoryRepository
        success_endpoint = 'category_list'

This view is available only by ``POST`` method.


.. _Django: https://www.djangoproject.com
.. _Flask-Bootstrap: https://pythonhosted.org/Flask-Bootstrap/
