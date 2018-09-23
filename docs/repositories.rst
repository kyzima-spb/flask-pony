.. _repositories:

Repositories
============

``Flask-Pony`` implements a design pattern Repository_:

    **Repository** is a mediator between definition domain and data distribution levels,
    uses an interface similar to collections for access to objects in definition domain.

    **Definition domain** is the storage itself or the domain model.

    **Distribution area** - `Data Mapper`_.

    -- Martin Fowler

So far this is just simplest implementation of this template: :py:class:`~flask_pony.repositories.PonyRepository`

First of all, repositories are needed to work with HTML-forms.
Thanks to them, the forms can be processed automatically.

To create a repository, you must inherit from base class :py:class:`~flask_pony.repositories.PonyRepository`
and override the static property :py:attr:`~flask_pony.repositories.PonyRepository.entity_class`,
that contains a reference to the entity class.

.. code-block:: python

    # repositories.py

    from flask_pony.repositories import PonyRepository

    from .model import Category


    class CategoryRepository(PonyRepository):
        entity_class = Category


In repository, you can encapsulate complex queries for data sampling.
Repository can work with a different number of entity types, depending on your task.
Repository names don't have to be the same as entity names

In other words, you can extend basic repository of any logic you need
and then use it anywhere in your web application.

If entity has attributes with a type :py:class:`Set`,
then form builder does not make any assumptions about this field rendering.
User decides how and what form elements to create, and also whites the handler for these fields

.. _Repository: https://martinfowler.com/eaaCatalog/repository.html
.. _Data Mapper: https://martinfowler.com/eaaCatalog/dataMapper.html
