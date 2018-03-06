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

from wtforms import SelectMultipleField, SelectFieldBase
from wtforms import widgets
from wtforms.compat import text_type


__all__ = (
    'EntityField',
)


class EntityField(SelectFieldBase):
    PK_SEPARATOR = ';'

    widget = widgets.Select()

    def __init__(self, entity_class, label=None, allow_empty=False, empty_text='', **kwargs):
        super().__init__(label, **kwargs)
        self.entity_class = entity_class
        self.allow_empty = allow_empty
        self.empty_text = empty_text

    def pk2str(self, entity):
        pk = (text_type(getattr(entity, attr.name)) for attr in entity._pk_attrs_)
        return self.PK_SEPARATOR.join(pk)

    def str2pk(self, s):
        attrs = self.entity_class._pk_attrs_
        values = s.split(self.PK_SEPARATOR)
        return tuple(attr.py_type(value) for attr, value in zip(attrs, values))

    def iter_choices(self):
        if self.allow_empty:
            yield ('', self.empty_text, self.data is None)

        for entity in self.entity_class.select():
            yield (self.pk2str(entity), text_type(entity), entity == self.data)

    def process_formdata(self, valuelist):
        if valuelist:
            pk = self.str2pk(valuelist[0])
            self.data = self.entity_class.__getitem__(pk)

    # def pre_validate(self, form):
    #     print('Pre validate')
    #     super().pre_validate(form)
