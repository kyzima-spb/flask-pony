from pony.orm import Database
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

    def init_app(self, app):
        # app.config.setdefault('PONY_TYPE', 'sqlite')
        # app.config.setdefault('PONY_HOST', 'localhost')

        if hasattr(app, 'teardown_appcontext'):
            app.teardown_appcontext(self.teardown)
        else:
            app.teardown_request(self.teardown)

    def db(self):
        ctx = stack.top

        print('DEBUG MODE:', current_app.debug)

        if ctx is not None:
            if not hasattr(ctx, 'pony_orm'):
                ctx.pony_orm = Database()
            return ctx.pony_orm

    def teardown(self, exception):
        ctx = stack.top

        if hasattr(ctx, 'pony_orm'):
            pass
