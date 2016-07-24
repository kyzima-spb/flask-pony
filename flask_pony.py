from pony.orm import Database, sql_debug
from flask import current_app
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack


class Pony(object):
    def __init__(self, app=None):
        self.app = app

        if app is not None:
            self.init_app(app)

    def create(self):
        config = current_app.config
        db_type = config('PONY_TYPE')
        args = [db_type]
        kwargs = {}

        if db_type == 'sqlite':
            args.append(config['PONY_DBNAME'] or ':memory:')
        elif db_type == 'mysql':
            #3306
            kwargs.update({
                host: config['PONY_HOST'],
                port: config['PONY_PORT'],
                user: config['PONY_USER'],
                passwd: config['PONY_PASSWORD'],
                db: config['PONY_DBNAME']
            })
        elif db_type == 'postgres':
            #5432
            kwargs.update({
                host: config['PONY_HOST'],
                port: config['PONY_PORT'],
                user: config['PONY_USER'],
                password: config['PONY_PASSWORD'],
                database: config['PONY_DBNAME']
            })
        elif db_type == 'oracle':
            #1521
            args.append('{user}/{password}@{host}:{port}/{dbname}'.format(
                user=config['PONY_USER'],
                password=config['PONY_PASSWORD'],
                host=config['PONY_HOST'],
                port=config['PONY_PORT'],
                dbname=config['PONY_DBNAME']
            ))

        return Database(*args, **kwargs)

    def init_app(self, app):
        # app.config.setdefault('PONY_TYPE', 'sqlite')
        app.config.setdefault('PONY_HOST', 'localhost')

        print(app.config['PONY_TYPE'])

        if hasattr(app, 'teardown_appcontext'):
            app.teardown_appcontext(self.teardown)
        else:
            app.teardown_request(self.teardown)

    def db(self):
        sql_debug(current_app.debug)

        ctx = stack.top

        if ctx is not None:
            if not hasattr(ctx, 'pony_orm'):
                ctx.pony_orm = self.create()
            return ctx.pony_orm

    def teardown(self, exception):
        ctx = stack.top

        if hasattr(ctx, 'pony_orm'):
            pass
