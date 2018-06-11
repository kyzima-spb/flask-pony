# coding: utf-8
#
# Copyright 2018 Kirill Vercetti
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask_wtf import FlaskForm
from pony.orm import ObjectNotFound
from pony.orm.core import Entity
from wtforms import SelectMultipleField, SelectFieldBase
from wtforms import widgets
from wtforms.compat import text_type
from wtforms.validators import ValidationError


__all__ = (
    'Form', 'EntityField',
)


class Form(FlaskForm):
    """Base class for all HTML forms that work with Pony entities."""

    _attr_names_ = {}

    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)
        entity = kwargs.get('obj')
        self._original_entity = entity if isinstance(entity, Entity) else None

    @property
    def original_entity(self):
        return self._original_entity

    @property
    def entity_kwargs(self):
        data = self.data
        return {name: data.get(name) for name in self._attr_names_}


class EntityField(SelectFieldBase):
    # __slots__ = ('__pk', '__entity')

    PK_SEPARATOR = ';'

    widget = widgets.Select()

    def __init__(self, entity_class, label=None, allow_empty=False, empty_text='', **kwargs):
        self.__pk = None
        self.__entity = None

        super(EntityField, self).__init__(label, **kwargs)
        self.entity_class = entity_class
        self.allow_empty = allow_empty
        self.empty_text = empty_text

    def pk2str(self, entity):
        pk = (text_type(getattr(entity, attr.name)) for attr in entity._pk_attrs_)
        return self.PK_SEPARATOR.join(pk)

    # def str2pk(self, s):
    #     attrs = self.entity_class._pk_attrs_
    #     values = s.split(self.PK_SEPARATOR)
    #     return tuple(attr.py_type(value) for attr, value in zip(attrs, values))

    @property
    def data(self):
        return self.__entity

    @data.setter
    def data(self, entity_or_pk):
        if entity_or_pk is None or entity_or_pk == '':
            del self.data
            return

        if isinstance(entity_or_pk, self.entity_class):
            self.__entity = entity_or_pk
            return

        self.pk = entity_or_pk

        try:
            self.__entity = self.entity_class.__getitem__(self.pk)
        except ObjectNotFound:
            del self.pk

    @data.deleter
    def data(self):
        self.__entity = None
        del self.pk

    @property
    def pk(self):
        if self.__pk is None:
            entity = self.__entity
            if entity:
                pk = tuple(getattr(entity, attr.name) for attr in self.entity_class._pk_attrs_)
                self.__pk = pk[0] if len(pk) == 1 else pk
        return self.__pk

    @pk.setter
    def pk(self, value):
        if isinstance(value, text_type):
            value = value.split(self.PK_SEPARATOR)
        elif not isinstance(value, (tuple, list)):
            value = (value,)

        attrs = self.entity_class._pk_attrs_

        if len(value) != len(attrs):
            raise ValidationError('Not a valid choice')

        self.__pk = tuple(attr.py_type(value) for attr, value in zip(attrs, value))

    @pk.deleter
    def pk(self):
        self.__pk = None

    def iter_choices(self):
        if self.allow_empty:
            yield ('', self.empty_text, self.data is None)

        for entity in self.entity_class.select():
            yield (self.pk2str(entity), text_type(entity), entity == self.data)

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[0]

    def pre_validate(self, form):
        if self.data is None and (self.pk or not self.allow_empty):
            raise ValidationError('Not a valid choice')
