Flask-Pony
==========

|PyPI| |LICENCE| |STARS|

PonyORM for your Flask application.


Installation
------------

::

    # Install the latest stable version
    pip install flask-pony

    # Install the development version
    pip install https://github.com/kyzima-spb/flask-pony/archive/dev-master.zip


Quick start
-----------

Read the documentation for the `pony-database-facade`_ package.

.. code:: python

    # app.py

    from flask import Flask

    from flask_pony import Pony


    app = Flask(__name__)
    app.config.from_object('configmodule.Config')

    pony = Pony(app)

    from . import models

    pony.connect()


.. code:: python

    # models.py

    from pony.orm import Required

    from . import pony


    db = pony.db


    class Person(db.Entity):
        username = Required(str, 50)


.. code:: python

    # configmodule.py

    class Config(object):
        PONY = {
            'provider': 'mysql',
            'user': 'anyone',
            'password': 'anykey',
            'dbname': 'blog'
        }


.. |PyPI| image:: https://img.shields.io/pypi/v/flask-pony.svg
   :target: https://pypi.python.org/pypi/flask-pony/
   :alt: Latest Version

.. |LICENCE| image:: https://img.shields.io/github/license/kyzima-spb/flask-pony.svg
   :target: https://github.com/kyzima-spb/flask-pony/blob/master/LICENSE
   :alt: Apache 2.0

.. |STARS| image:: https://img.shields.io/github/stars/kyzima-spb/flask-pony.svg
   :target: https://github.com/kyzima-spb/flask-pony/stargazers

.. _Русская документация: docs/RU.rst
.. _pony-database-facade: https://github.com/kyzima-spb/pony-database-facade
