# coding: utf-8

from pony.orm import db_session
from wtforms import SelectField, SelectMultipleField


class EntityField(SelectField):
    def __init__(self, entity_class, label=None, allow_empty=False, empty_text='', coerce=int, **kwargs):
        super().__init__(label, coerce=coerce, **kwargs)

        self.entity_class = entity_class

        with db_session:
            self.choices = [(c.id, c) for c in entity_class.select()]

        if allow_empty:
            empty_value = 0 if self.coerce is int else ''
            self.choices.insert(0, (empty_value, empty_text))


__all__ = (
    'EntityField',
)
