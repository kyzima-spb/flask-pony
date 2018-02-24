"""
coding: utf-8

bool        - BooleanField
int         - IntegerField
float       - FloatField
Decimal     - DecimalField
str         - StringField
unicode     - StringField
LongStr     - TextAreaField
LongUnicode - TextAreaField
date        - DateField
datetime    - DateTimeField
Json        - TextAreaField

time        - нет
timedelta   - нет
buffer      - ? - used for binary data in Python 2 and 3
bytes       - ? - used for binary data in Python 3
UUID        -
"""

from collections import OrderedDict
from datetime import date, datetime, time

from flask_wtf import FlaskForm
from pony.orm import ormtypes
import six
import wtforms.fields as wtf_fields
import wtforms.validators as wtf_validators

from pony.orm import Database, Required, Optional, Set, PrimaryKey


class Factory(object):
    def __init__(self):
        self.__types = {}

    def get(self, tp):
        return self.__types.get(tp)

    def __call__(self, *types):
        def decorator(func):
            for tp in types:
                self.__types[tp] = func
            return func
        return decorator


class FormBuilder(object):
    field_factory = Factory()

    def __init__(self, entity_class, base_class=None, excludes=None):
        self._fields = OrderedDict()

        self._entity_class = entity_class
        self._base_class = base_class
        self._excludes = set(excludes or [])

    def _field_numeric(self, attr, kwargs):
        miN = attr.kwargs.get('min', attr.kwargs.get('unsigned') and 0)
        maX = attr.kwargs.get('max')

        kwargs['validators'].append(wtf_validators.NumberRange(miN, maX))

    def _field_string(self, attr, kwargs):
        args = list(attr.args)
        max_len = args.pop() if args else attr.kwargs.get('max_len')
        if max_len:
            kwargs['validators'].append(wtf_validators.Length(max=max_len))

    def add(self, attr, field_class=None, **options):
        print(attr.py_type, attr.name)
        def field_user_defined(attr, kwargs):
            return field_class, kwargs

        kwargs = {
            'label': attr.name,
            'default': attr.default,
            'validators': [
                wtf_validators.InputRequired() if attr.is_required and not attr.is_pk else wtf_validators.Optional()
            ],
        }

        method = self.field_factory.get(attr.py_type) or field_user_defined

        klass, kwargs = method(self, attr, kwargs) if hasattr(self, method.__name__) else method(attr, kwargs)

        if klass:
            kwargs['validators'] += options.pop('validators', [])
            kwargs.update(options)
            self._fields[attr.name] = field_class(**kwargs) if field_class else klass(**kwargs)

        return self

    def build_form(self):
        for attr in self._entity_class._attrs_:
            if attr.name not in self._excludes:
                self.add(attr)

    def get_form(self):
        self.build_form()
        classname = '{}Form'.format(self._entity_class.__class__.__name__)
        base = self._base_class or FlaskForm
        return type(classname, (base,), self._fields)

    @field_factory(bool)
    def field_bool(self, attr, kwargs):
        return wtf_fields.BooleanField, kwargs

    @field_factory(int)
    def field_int(self, attr, kwargs):
        # print(dir(attr))
        # print(attr.is_pk, attr.auto, attr.is_part_of_unique_index, attr.composite_keys, attr.is_unique)

        if attr.is_pk:
            field_class = wtf_fields.HiddenField
        else:
            field_class = wtf_fields.IntegerField

        self._field_numeric(attr, kwargs)
        return field_class, kwargs

    @field_factory(float)
    def field_float(self, attr, kwargs):
        self._field_numeric(attr, kwargs)
        return wtf_fields.FloatField, kwargs

    @field_factory(ormtypes.Decimal)
    def field_decimal(self, attr, kwargs):
        self._field_numeric(attr, kwargs)
        kwargs.setdefault('places', None)
        return wtf_fields.DecimalField, kwargs

    @field_factory(str, six.text_type)
    def field_string(self, attr, kwargs):
        self._field_string(attr, kwargs)
        return wtf_fields.StringField, kwargs

    @field_factory(ormtypes.LongStr, ormtypes.LongUnicode)
    def field_textarea(self, attr, kwargs):
        self._field_string(attr, kwargs)
        return wtf_fields.TextAreaField, kwargs

    @field_factory(date)
    def field_date(self, attr, kwargs):
        return wtf_fields.DateField, kwargs

    @field_factory(datetime)
    def field_datetime(self, attr, kwargs):
        return wtf_fields.DateTimeField, kwargs

    @field_factory(ormtypes.Json)
    def field_json(self, attr, kwargs):
        return wtf_fields.TextAreaField, kwargs

    def field_pk(self, attr, kwargs):
        pass

    @classmethod
    def get_instance(cls, entity_class, *args, **kwargs):
        return cls(entity_class, *args, **kwargs).get_form()
