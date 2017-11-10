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

from __future__ import print_function

from flask import current_app
from pony_database_facade import DatabaseFacade

__version__ = '2.0.0'


class Pony(object):
    __slots__ = ('__facade', 'app')

    def __init__(self, app=None):
        self.__facade = None

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
        if self.__facade is not None:
            return self.__facade.db

    def connect(self, module_with_entities):
        if self.__facade is None:
            config = self.__get_app().config
            facade = DatabaseFacade(module_with_entities, **config['DB'])
            facade.connect()
            self.__facade = facade

    def init_app(self, app):
        app.config.setdefault('DB', {})
