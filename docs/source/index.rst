.. Flask-Pony documentation master file, created by
   sphinx-quickstart on Sun Jun  3 13:23:25 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Что такое Flask-Pony?
=====================

|PyPI| |LICENCE| |STARS|

``Flask-Pony`` - это расширение к популярному микрофреймворку Flask_, которое позволяет использовать PonyORM_ совместно с ним.

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

``Flask-Pony`` использует библиотеку `pony-database-facade`_,
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

В момент вызова метод :py:meth:`Pony.connect` произойдет вызов методов :py:meth:`Database.bind` и :py:meth:`Database.generate_mapping`.


Описание сущностей
------------------

.. note::

    Здесь, и в других разделах документации, подразумевается,
    что у вас в модуле ``__init__.py`` создан объект приложения ``app`` и проинициализировано расширение ``Flask-Pony``,
    доступное через переменую ``pony``.

Все сущности будут находиться в модуле ``models.py``. Для описания сущностей необходим экземпляр класса :py:class:`Database`,
но его не нужно создавать явно, он доступен через свойство :py:attr:`Pony.db`:

.. code-block:: python

    # model.py

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


db_session
----------

``Flask-Pony`` автоматически запускает сессию перед началом запроса и завершает сессию после окончания запроса.
Вот комментарий одного из авторов PonyORM_:

   "В большинстве случаев, правильнее всего если :py:func:`db_session` будет охватывать обработку HTTP-запроса от начала и до конца,
   открываясь перед получением пользователя текущей сессии,
   и закрываясь после успешной генерации результата (HTML на базе шаблона или JSON, смотря что за приложение)"

   -- `Александр Козловский`_

Если вы хотите создать сущность, а затем получить ее идентификатор (первичный ключ),
то для этого можно воспользоваться методом :py:func:`flush`.
Например, вы обработали форму добавления сущности и хотите сделать редирект на страницу редактирования только что созданной сущности.

И еще парочка комментариев от автора PonyORM_:

   "Для того чтобы сохранить объект до завершени сессии нужно сделать либо :py:func:`flush`,
   в этом случае в базу пойдет ``INSERT``, но транзакция не будет завершена,
   и в дальнейшем всё еще можно сделать :py:func:`rollback`,
   либо :py:func:`commit`, если уже точно понятно, что объект надо сохранить в любом случае"

   <...>

   "Технически Pony позволяет внутри одной :py:func:`db_session` создавать другую,
   но вложенные сессии просто игнорируются. Поэтому вреда от них быть не должно"

   -- `Александр Козловский`_

Репозиторий
-----------

Скорее всего дальше вам нужно написать CRUD, поэтому первым шагом будет создать все необходимые репозитории.

Подробнее с примерами читайте в разделе: :ref:`repositories`.

Представления
-------------

``Flask-Pony`` использует представления, основанные на классах. Для стандартных CRUD операций уже есть готовые представления.

Подробнее с примерами читайте в разделе: :ref:`views`.

Формы
-----

``Flask-Pony`` автоматически создает классы HTML-форм для стандартных CRUD операций.
Но он не умеет работать со связями "многие ко многим", а так же, возможно, вам потребуется создать форму вручную.

Подробнее с примерами читайте в разделе: :ref:`forms`.

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
