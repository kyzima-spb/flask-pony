# coding: utf-8

from pony.orm import db_session
from wtforms.validators import StopValidation

from .forms import EntityField


class Validator(object):
    def __init__(self, message=None):
        self.message = message


class EntityExists(Validator):
    def __init__(self, entity_class=None, message=None):
        super().__init__(message)

        self.__entity_class = entity_class
        self.field = None

    def __call__(self, form, field):
        self.field = field

        with db_session:
            try:
                if not self.entity_class.exists(id=field.data):
                    msg = self.message or 'Entity not exists'
                    raise StopValidation(msg)
            finally:
                self.field = None

    @property
    def entity_class(self):
        if isinstance(self.field, EntityField):
            return self.field.entity_class

        if self.__entity_class:
            return self.__entity_class

        raise RuntimeError('You must set the entity class')
