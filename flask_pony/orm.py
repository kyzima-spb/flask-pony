# coding: utf-8

"""
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

from pony.orm import ormtypes
import six
import wtforms.fields as wtf_fields
import wtforms.validators as wtf_validators

from .forms import Form, EntityField
from .validators import UniqueEntityValidator


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


class FormBuilder(object):
    field_constructor = Factory()

    def __init__(self, entity_class, base_class=None, excludes=None, skip_pk=True):
        self._fields = OrderedDict()
        self._buttons = OrderedDict()

        self._entity_class = entity_class
        self._base_class = base_class
        self._excludes = set(excludes or [])
        self._skip_pk = skip_pk

    def _field_numeric(self, attr, options):
        miN = attr.kwargs.get('min', attr.kwargs.get('unsigned') and 0)
        maX = attr.kwargs.get('max')

        options['validators'].append(wtf_validators.NumberRange(miN, maX))

    def _field_string(self, attr, options):
        args = list(attr.args)
        max_len = args.pop() if args else attr.kwargs.get('max_len')
        if max_len:
            options['validators'].append(wtf_validators.Length(max=max_len))

    def _get_field_method(self, tp):
        """Returns a reference to the form element's constructor method."""
        method = self.field_constructor.get(tp)
        if method and hasattr(self, method.__name__):
            return getattr(self, method.__name__)
        return method

    def _create_collection_field(self, attr, options):
        """Creates the form element for working with the collection of entities."""
        return None, options

    def _create_plain_field(self, attr, options):
        """Creates the form element."""
        method = self._get_field_method(attr.py_type) or self._create_other_field
        klass, options = method(attr, options)

        if attr.is_unique:
            options['validators'].append(UniqueEntityValidator(attr.entity))

        return klass, options

    def _create_pk_field(self, attr, options):
        """Creates the form element for working with primary key."""
        if attr.auto or self._skip_pk:
            return None, options

    def _create_relational_field(self, attr, options):
        """Creates the form element for working with entity relationships."""
        options['entity_class'] = attr.py_type
        options['allow_empty'] = not attr.is_required
        return EntityField, options

    def _create_other_field(self, attr, options):
        """Creates a custom form element. Called when the element was not found."""
        return None, options

    def add(self, attr, field_class=None, **options):
        """Adds an element to the form based on the entity attribute."""
        # print(attr.name, attr.py_type, getattr(attr, 'set', None))
        # print(dir(attr))
        # print(attr, attr.is_relation, attr.is_collection)
        # print(attr.is_pk, attr.auto, attr.is_unique, attr.is_part_of_unique_index, attr.composite_keys)

        def add(klass, options):
            if klass:
                self._fields[attr.name] = field_class(**options) if field_class else klass(**options)
            return self

        kwargs = {
            'label': attr.name,
            'default': attr.default,
            'validators': [],
        }
        kwargs.update(options)

        if attr.is_pk:
            return add(*self._create_pk_field(attr, kwargs))

        # Если коллекция, то никаких предположений делать не нужно - пусть пользователь сам создает нужный элемент
        if attr.is_collection:
            return add(*self._create_collection_field(attr, kwargs))

        validator = wtf_validators.InputRequired() if attr.is_required and not attr.is_pk else wtf_validators.Optional()
        kwargs['validators'].insert(0, validator)

        if attr.is_relation:
            return add(*self._create_relational_field(attr, kwargs))

        return add(*self._create_plain_field(attr, kwargs))

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
    def field_bool(self, attr, options):
        return wtf_fields.BooleanField, options

    @field_constructor(int)
    def field_int(self, attr, options):
        self._field_numeric(attr, options)
        return wtf_fields.IntegerField, options

    @field_constructor(float)
    def field_float(self, attr, options):
        self._field_numeric(attr, options)
        return wtf_fields.FloatField, options

    @field_constructor(ormtypes.Decimal)
    def field_decimal(self, attr, options):
        self._field_numeric(attr, options)
        options.setdefault('places', None)
        return wtf_fields.DecimalField, options

    @field_constructor(str, six.text_type)
    def field_string(self, attr, options):
        self._field_string(attr, options)
        return wtf_fields.StringField, options

    @field_constructor(ormtypes.LongStr, ormtypes.LongUnicode)
    def field_textarea(self, attr, options):
        self._field_string(attr, options)
        return wtf_fields.TextAreaField, options

    @field_constructor(date)
    def field_date(self, attr, options):
        return wtf_fields.DateField, options

    @field_constructor(datetime)
    def field_datetime(self, attr, options):
        return wtf_fields.DateTimeField, options

    @field_constructor(ormtypes.Json)
    def field_json(self, attr, options):
        return wtf_fields.TextAreaField, options

    @classmethod
    def get_instance(cls, entity_class, *args, **kwargs):
        return cls(entity_class, *args, **kwargs).get_form()
