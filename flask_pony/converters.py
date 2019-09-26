from flask import current_app
from werkzeug.routing import BaseConverter, IntegerConverter, ValidationError

from . import start_db_session


class EntityConverter(BaseConverter):
    """
    Конвертер с именем "pk", который возвращает сущность из БД по первичному ключу.
    """

    def __init__(self, map, entity_classname):
        super().__init__(map)
        self.entity_classname = entity_classname

    def to_python(self, value):
        pony = current_app.extensions['flask_pony']
        cls = getattr(pony.db, self.entity_classname, None)

        if cls is None:
            raise LookupError(f'the entity {self.entity_classname} does not exist')

        start_db_session()

        entity = cls.get(id=value)

        if entity is None:
            raise ValidationError()

        return entity

    def to_url(self, entity):
        # '_pk_', '_pk_attrs_', '_pk_columns_', '_pk_converters_'
        # print(dir(entity))
        return super().to_url(entity._pk_)
