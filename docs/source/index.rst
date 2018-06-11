.. Flask-Pony documentation master file, created by
   sphinx-quickstart on Sun Jun  3 13:23:25 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Что такое Flask-Pony?
=====================

|PyPI| |LICENCE| |STARS|

Flask-Pony - это расширение к популярному микрофреймворку Flask_, которое позволяет использовать PonyORM_ совместно с ним.

Быстрый старт
=============

Установка
---------

.. code-block:: shell

    # Установить последнюю стабильную версию
    pip install flask-pony

    # Установить версию в разработке (возможны баги, но она самая свежая)
    pip install https://github.com/kyzima-spb/flask-pony/archive/dev-master.zip


Настройка
---------

Flask-Pony использует библиотеку `pony-database-facade`_,
которая позволяет инкапсулировать имена параметров, используемых в низкоуровневых модулях.
В конфигурационном файле вам доступна одна опция ``PONY`` - это словарь настроек.
Это отличается от традиционного подхода, когда каждая настройка задачается отдельно.
Мне кажется использовать словарь удобнее, но если у вас есть весомые доводы в пользу традициооного подхода, напишите мне на почту или GitHub.

Пример конфигурационного файла ``settings.py`` с использованием классов:

.. code-block:: python

    # settings.py

    class Config(object):
        PONY = {
            'provider': 'sqlite',
            'dbname': 'estore.sqlite'
        }


Инициализация и подключение
---------------------------

.. code-block:: python

    # __init__.py

    from flask import Flask
    from flask_pony import Pony


    # Создаем объект приложения и загружаем настройки
    app = Flask(__name__)
    app.config.from_object('settings.Config')

    # Создаем экземпляр расширения
    pony = Pony(app)

    # Импортируем модуль с сущностями Pony
    from . import models

    # Устанавливаем соединение
    pony.connect()

В момент вызова метод ``connect()`` произойдет вызов методов ``bind`` и ``generate_mapping``.


Описание сущностей
------------------

.. note::

    Здесь, и в других разделах документации, подразумевается,
    что у вас в модуле ``__init__.py`` создан объект приложения ``app`` и проинициализировано расширение ``Flask-Pony``,
    доступное через переменую ``pony``.

Все сущности будут находиться в модуле ``models.py``. Для описания сущностей необходим экземпляр класса ``Database``,
но его не нужно создавать явно, он доступен через свойство ``db``:

.. code-block:: python

    # models.py

    from pony.orm import Required, Optional, Set

    # из модуля __init__.py импортируем экземпляр Flask-Pony
    from . import pony


    # Получаем ссылку на базовый класс сущностей Pony.
    db = pony.db


    class Category(db.Entity):
        title = Required(str, unique=True)
        parent = Optional('Category', reverse='children')
        children = Set('Category', reverse='parent')

        def __str__(self):
            return self.title


.. |PyPI| image:: https://img.shields.io/pypi/v/flask-pony.svg
   :target: https://pypi.python.org/pypi/flask-pony/
   :alt: Latest Version

.. |LICENCE| image:: https://img.shields.io/github/license/kyzima-spb/flask-pony.svg
   :target: https://github.com/kyzima-spb/flask-pony/blob/master/LICENSE
   :alt: Apache 2.0

.. |STARS| image:: https://img.shields.io/github/stars/kyzima-spb/flask-pony.svg
   :target: https://github.com/kyzima-spb/flask-pony/stargazers

.. _PonyORM: https://ponyorm.com
.. _Flask: http://flask.pocoo.org
.. _pony-database-facade: https://github.com/kyzima-spb/pony-database-facade
