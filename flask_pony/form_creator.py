# -*- coding: utf-8 -*-

from pony.orm import Database, Required, Optional, Set
from wtforms.fields import StringField
from flask import Flask


db = Database(provider='sqlite', filename=':memory:')


class Person(db.Entity):
    firstname = Required(str, 50)
    lastname = Optional(str, 50)
    age = Optional(int)
    is_developer = Optional(bool, default=False)
    account = Optional('Account')


class Account(db.Entity):
    users = Set('Person')


def converter(tp):
    def decorator(func):
        cls = lambda: FormCreator
        cls().add_converter(tp, func)
        return func
    return decorator


class FormCreator(object):
    """
    bool        - BooleanField
    int         - IntegerField
    float       - FloatField
    Decimal     - DecimalField
    str         - StringField
    unicode     - StringField
    date        - DateField
    datetime    - DateTimeField
    time        - нет
    timedelta   - нет
    buffer      - ? - used for binary data in Python 2 and 3
    bytes       - ? - used for binary data in Python 3
    LongStr     - TextAreaField - used for large strings
    LongUnicode - TextAreaField - used for large strings
    Json        - TextAreaField - used for mapping to native database JSON type
    UUID        -
    """

    entity_class = None

    __converters = {}

    @classmethod
    def add_converter(cls, tp, method):
        cls.__converters[tp] = method

    def get_coverter(self, tp):
        method = 'field_{}'.format(tp.__name__)
        return getattr(self, method, None)

    def fields(self):
        for attr in self.entity_class._attrs_:
            method = self.get_coverter(attr.py_type)
            if method:
                method(attr)
            else:
                print(attr.py_type)

    @converter(str)
    def field_str(self, attr):
        field = StringField(attr.name)
        print(field)


class PersonForm(FormCreator):
    entity_class = Person


db.generate_mapping(create_tables=True)


form = PersonForm()
form.fields()
