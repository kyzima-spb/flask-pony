What is Flask-Pony?
===================

|PyPI| |LICENCE| |STARS|

``Flask-Pony`` - is extension to the popular Flask_ microframe, which allows you to use PonyORM_ in conjunction with it.

Quick Start
===========

Installation
------------

.. code-block:: shell

    # Install the latest stable version
    pip install flask-pony

    # Install development version (bugs are possible, but it is the most recent)
    pip install https://github.com/kyzima-spb/flask-pony/archive/dev-master.zip


Configuring
-----------

``Flask-Pony`` uses the `pony-database-facade`_ library,
which allows you to encapsulate the names of parameters used in low-level modules.
In configuration file you have one option ``PONY`` - settings dictionary.
This is the difference from the traditional approach, where each setting is specified separately.
It seems more convenient to use dictionary, but if you have strong arguments in favor of the traditional approach, write to me on mail or GitHub.

An example of the configuration file ``settings.py`` using classes:

.. code-block:: python

    # settings.py

    class Config(object):
        PONY = {
            'provider': 'sqlite',
            'dbname': 'estore.sqlite'
        }


Initialization and connection
-----------------------------

.. code-block:: python

    # __init__.py

    from flask import Flask
    from flask_pony import Pony


    # Create an application object and load settings
    app = Flask(__name__)
    app.config.from_object('settings.Config')

    # Create an extension instance
    pony = Pony(app)

    # Import a Pony-entities module
    from . import models

    # Connect
    pony.connect()

When the :py:meth:`Pony.connect` method is called, the :py:meth:`Database.bind` and :py:meth:`Database.generate_mapping` methods are called at the same time.


Define entities
---------------

.. note::

    Here and in other sections of this guide means that your ``__init__.py`` module has an ``app`` variable
    that contains application instance and initialized ``Flask-Pony`` extension via the ``pony`` variable.

There are ``models.py`` module will contents all entities.
To define entities you need an instance of the :py:class:`Database` class and it is accessible through the :py:attr:`Pony.db` property.
So there is no need to create it explicitly:

.. code-block:: python

    # model.py

    from pony.orm import Required, Optional, Set

    # Import Flask-Pony instance from __init__.py module
    from . import pony


    # Get a reference to the base class of Pony entities
    db = pony.db


    class Category(db.Entity):
        title = Required(str, unique=True)
        parent = Optional('Category', reverse='children')
        children = Set('Category', reverse='parent')

        def __str__(self):
            return self.title


db_session
----------

``Flask-Pony`` automatically starts session before the beginning of the request and ends the session after the end of the request.
Here's a comment from one of the authors of PonyORM_:

    "In most cases, the best way is if :py:func:`db_session` covers the processing of the HTTP request from beginning to end,
    opening before the user of the current session, and closing after the successful result generation
    (HTML based on the template or JSON, depending on what application is)"

    -- `Александр Козловский`_

If you want to create an entity, and then get its ID (primary key), you can use the :py:func:`flush` method to do this.
For example, you have processed the form of adding an entity and want to redirect to the edit page of the newly created entity.

Some another comment from PonyORM_ author:

    "For saving the object until the end of the session, you need to do either :py:func:`flush`
    (in this case ``INSERT`` will go to the database, but the transaction will not be completed, and you can still do :py:func:`rollback`),
    or :py:func:`commit`, if is definitely known, that object should be saved in any case"

    <...>

    "Technically, Pony allows you to create another inside of one :py:func:`db_session`, but nested sessions are simply ignored.
    Therefore, there should be no harm from them"

    -- `Александр Козловский`_


Repository
----------

Most likely you need to write a CRUD, so the first step is to create all the necessary repositories.

For more details on the examples, see: :ref:`repositories`.


Views
-----

``Flask-Pony`` uses views based on classes. There are already ready-made views for standard CRUD operations.

For more details on the examples, see: :ref:`views`.


Forms
-----

``Flask-Pony`` automatically creates HTML form classes for standard CRUD operations,
but cannot work with many-to-many relationships. Perhaps, you also need to create a form manually.

For more details about the examples, see: :ref:`forms`.


.. |PyPI| image:: https://img.shields.io/pypi/v/flask-pony.svg
   :target: https://pypi.org/project/Flask-Pony/
   :alt: Latest Version

.. |LICENCE| image:: https://img.shields.io/github/license/kyzima-spb/flask-pony.svg
   :target: https://github.com/kyzima-spb/flask-pony/blob/master/LICENSE
   :alt: Apache 2.0

.. |STARS| image:: https://img.shields.io/github/stars/kyzima-spb/flask-pony.svg
   :target: https://github.com/kyzima-spb/flask-pony/stargazers

.. _PonyORM: https://ponyorm.com
.. _Flask: http://flask.pocoo.org
.. _pony-database-facade: https://github.com/kyzima-spb/pony-database-facade
.. _Александр Козловский: https://vk.com/metaprogrammer
