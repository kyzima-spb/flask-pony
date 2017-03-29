# coding: utf-8

from __future__ import print_function

from pony.orm import Database
from flask import current_app

__version__ = '1.0.1'


class Pony(object):
    def __init__(self, app=None):
        self.app = app

        if app is not None:
            self.init_app(app)

    def __get_app(self):
        if current_app:
            return current_app

        if self.app is not None:
            return self.app

        raise RuntimeError('Application not found!')

    def get_db(self):
        config = self.__get_app().config
        db_type = config['DB_TYPE']
        args = [db_type]
        kwargs = {}

        if db_type == 'sqlite':
            kwargs.update({
                'filename': config['DB_NAME'],
                'create_db': True
            })
        elif db_type == 'mysql':
            kwargs.update({
                'host': config['DB_HOST'],
                'port': config['DB_PORT'],
                'user': config['DB_USER'],
                'passwd': config['DB_PASSWORD'],
                'db': config['DB_NAME'],
                'charset': config['DB_CHARSET']
            })
        elif db_type == 'postgres':
            kwargs.update({
                'host': config['DB_HOST'],
                'port': config['DB_PORT'],
                'user': config['DB_USER'],
                'password': config['DB_PASSWORD'],
                'database': config['DB_NAME']
            })
        elif db_type == 'oracle':
            args.append('{user}/{password}@{host}:{port}/{dbname}'.format(
                user=config['DB_USER'],
                password=config['DB_PASSWORD'],
                host=config['DB_HOST'],
                port=config['DB_PORT'],
                dbname=config['DB_NAME']
            ))

        return Database(*args, **kwargs)

    def init_app(self, app):
        app.config.setdefault('DB_TYPE', 'sqlite')

        db_type = app.config['DB_TYPE']

        if db_type == 'sqlite':
            app.config.setdefault('DB_NAME', ':memory:')
        elif db_type == 'mysql':
            app.config.setdefault('DB_PORT', 3306)
        elif db_type == 'postgres':
            app.config.setdefault('DB_PORT', 5432)
        elif db_type == 'oracle':
            app.config.setdefault('DB_PORT', 1521)

        app.config.setdefault('DB_HOST', 'localhost')
        app.config.setdefault('DB_USER', None)
        app.config.setdefault('DB_PASSWORD', None)
        app.config.setdefault('DB_NAME', None)
        app.config.setdefault('DB_CHARSET', 'utf8')
