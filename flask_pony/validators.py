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

from wtforms.validators import StopValidation


__all__ = ('UniqueEntityValidator',)


class Validator(object):
    def __init__(self, message=None):
        self.message = message


class EntityValidator(Validator):
    def __init__(self, entity_class, message=None):
        super().__init__(message)
        self.__entity_class = entity_class

    @property
    def entity_class(self):
        if self.__entity_class:
            return self.__entity_class

        raise RuntimeError('You must set the entity class')


class UniqueEntityValidator(EntityValidator):
    def __call__(self, form, field):
        original_entity = form.original_entity

        if original_entity:
            if getattr(original_entity, field.name, None) == field.data:
                return True

        kwargs = {
            field.name: field.data
        }

        if self.entity_class.exists(**kwargs):
            msg = self.message or 'This value is already used.'
            raise StopValidation(msg)
