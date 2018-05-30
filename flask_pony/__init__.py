# coding: utf-8
#
# Copyright 2017 Kirill Vercetti
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function, unicode_literals

from flask import current_app, has_app_context, has_request_context
from pony.orm import db_session
from pony.orm.core import local
from pony_database_facade import DatabaseFacade

__version__ = '3.0.1'


def has_db_session():
    """Returns True if db_session exists"""
    return local.db_context_counter > 0


def start_db_session():
    """Starts a new db_session if it does not exists"""
    # print('==> Start session')

    if has_db_session():
        return

    if not has_app_context() or not has_request_context():
        raise RuntimeError('You need app_context or request_context')

    db_session.__enter__()


def stop_db_session(exc=None):
    """Stops the last db_session"""
    # print('==> Stop session', type(exc))

    if has_db_session():
        exc_type = None
        tb = None

        if exc:
            exc_type, tb = type(exc), exc.__traceback__

        db_session.__exit__(exc_type, exc, tb)


class Pony(object):
    __slots__ = ('__facade', 'app')

    def __init__(self, app=None):
        self.__facade = DatabaseFacade()

        self.app = app

        if app is not None:
            self.init_app(app)

    def __get_app(self):
        if current_app:
            return current_app

        if self.app is not None:
            return self.app

        raise RuntimeError('Application not found!')

    @property
    def db(self):
        return self.__facade.original

    def connect(self):
        config = self.__get_app().config

        facade = self.__facade
        facade.bind(**config['PONY'])
        facade.connect()

    def init_app(self, app):
        self.app = app
        app.config.setdefault('PONY', {})

        app.before_request(start_db_session)

        @app.teardown_appcontext
        def shutdown_session(response_or_exc):
            stop_db_session(response_or_exc)
            return response_or_exc
