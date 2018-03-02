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

from flask_pony.forms import EntityField
from .validators import EntityNotExists


class Factory(object):
    """A simple factory for functions and methods that generate form elements."""

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


class Form(FlaskForm):
    """Base class for all HTML forms that work with Pony entities."""

    _attr_names_ = {}

    @property
    def entity_kwargs(self):
        data = self.data
        return {name: data.get(name) for name in self._attr_names_}


class FormBuilder(object):
    field_constructor = Factory()

    def __init__(self, entity_class, base_class=None, excludes=None, skip_pk=True):
        self._fields = OrderedDict()
        self._buttons = OrderedDict()

        self._entity_class = entity_class
        self._base_class = base_class
        self._excludes = set(excludes or [])
        self._skip_pk = skip_pk

    def _field_numeric(self, attr, kwargs):
        miN = attr.kwargs.get('min', attr.kwargs.get('unsigned') and 0)
        maX = attr.kwargs.get('max')

        kwargs['validators'].append(wtf_validators.NumberRange(miN, maX))

    def _field_string(self, attr, kwargs):
        args = list(attr.args)
        max_len = args.pop() if args else attr.kwargs.get('max_len')
        if max_len:
            kwargs['validators'].append(wtf_validators.Length(max=max_len))

    def _get_field_method(self, tp):
        """Returns a reference to the form element's constructor method."""
        method = self.field_constructor.get(tp)
        if method and hasattr(self, method.__name__):
            return getattr(self, method.__name__)
        return method

    def _create_collection_field(self, attr, kwargs):
        """The form element for working with the collection of entities."""
        return None, kwargs

    def _create_relational_field(self, attr, kwargs):
        """The form element for working with entity relationships."""
        kwargs['entity_class'] = attr.py_type
        kwargs['allow_empty'] = not attr.is_required
        # kwargs['coerce'] = attr.py_type

        # if attr.is_unique:
        #     kwargs['validators'].append(EntityNotExists(attr.py_type))

        return EntityField, kwargs

    def _create_plain_field(self, attr, kwargs):
        def field_user_defined(attr, kwargs):
            # print(attr, attr.is_relation, attr.is_collection)
            return None, kwargs

        method = self._get_field_method(attr.py_type) or field_user_defined
        klass, kwargs = method(attr, kwargs)

        if attr.is_unique:
            kwargs['validators'].append(EntityNotExists(attr.entity))

        return klass, kwargs

    def add(self, attr, field_class=None, **options):
        """Adds an element to the form based on the entity attribute."""
        # print(attr.name, attr.py_type, getattr(attr, 'set', None))
        # print(dir(attr))
        # print(attr, attr.is_relation, attr.is_collection)
        # print(attr.is_pk, attr.auto, attr.is_unique, attr.is_part_of_unique_index, attr.composite_keys)

        if attr.is_pk and (attr.auto or self._skip_pk):
            return self

        kwargs = {
            'label': attr.name,
            'default': attr.default,
            'validators': [],
        }
        kwargs.update(options)

        # Если коллекция, то никаких предположений делать не нужно - пусть пользователь сам создает нужный элемент
        if attr.is_collection:
            klass, kwargs = self._create_collection_field(attr, kwargs)
            return self

        validator = wtf_validators.InputRequired() if attr.is_required and not attr.is_pk else wtf_validators.Optional()
        kwargs['validators'].insert(0, validator)

        if attr.is_relation:
            klass, kwargs = self._create_relational_field(attr, kwargs)
        else:
            klass, kwargs = self._create_plain_field(attr, kwargs)

        if klass:
            self._fields[attr.name] = field_class(**kwargs) if field_class else klass(**kwargs)

        return self

    def add_button(self, name, button_class=wtf_fields.SubmitField, **options):
        """Adds a button to the form."""
        self._buttons[name] = button_class(**options)

    def build_form(self):
        for attr in self._entity_class._attrs_:
            if attr.name not in self._excludes:
                self.add(attr)
        self.add_button('submit')

    def get_form(self):
        self.build_form()
        classname = '{}Form'.format(self._entity_class.__class__.__name__)
        base = self._base_class or Form
        props = OrderedDict()
        props.update(self._fields)
        props.update(self._buttons)
        form = type(classname, (base,), props)
        form._attr_names_ = self._fields.keys()
        return form

    @field_constructor(bool)
    def field_bool(self, attr, kwargs):
        return wtf_fields.BooleanField, kwargs

    @field_constructor(int)
    def field_int(self, attr, kwargs):
        self._field_numeric(attr, kwargs)
        return wtf_fields.IntegerField, kwargs

    @field_constructor(float)
    def field_float(self, attr, kwargs):
        self._field_numeric(attr, kwargs)
        return wtf_fields.FloatField, kwargs

    @field_constructor(ormtypes.Decimal)
    def field_decimal(self, attr, kwargs):
        self._field_numeric(attr, kwargs)
        kwargs.setdefault('places', None)
        return wtf_fields.DecimalField, kwargs

    @field_constructor(str, six.text_type)
    def field_string(self, attr, kwargs):
        self._field_string(attr, kwargs)
        return wtf_fields.StringField, kwargs

    @field_constructor(ormtypes.LongStr, ormtypes.LongUnicode)
    def field_textarea(self, attr, kwargs):
        self._field_string(attr, kwargs)
        return wtf_fields.TextAreaField, kwargs

    @field_constructor(date)
    def field_date(self, attr, kwargs):
        return wtf_fields.DateField, kwargs

    @field_constructor(datetime)
    def field_datetime(self, attr, kwargs):
        return wtf_fields.DateTimeField, kwargs

    @field_constructor(ormtypes.Json)
    def field_json(self, attr, kwargs):
        return wtf_fields.TextAreaField, kwargs

    @classmethod
    def get_instance(cls, entity_class, *args, **kwargs):
        return cls(entity_class, *args, **kwargs).get_form()
