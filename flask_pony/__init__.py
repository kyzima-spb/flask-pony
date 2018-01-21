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

__version__ = '3.0.1'


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
