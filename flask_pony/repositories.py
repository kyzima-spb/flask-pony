# coding: utf-8
#
# Copyright 2017 Kirill Vercetti
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

from abc import ABCMeta, abstractmethod
import pickle

from pony.orm import ObjectNotFound, flush
from six import with_metaclass


class Repository(with_metaclass(ABCMeta)):
    """
    Abstract repository, implementation of the design template
    `Repository <https://martinfowler.com/eaaCatalog/repository.html>`_.
    """

    @abstractmethod
    def create(self, **attributes):
        """
        Creates a new entity and saves it to the database.

        Arguments:
            attributes (dict): Entity attributes.
        """

    @abstractmethod
    def delete(self, entity):
        """
        Removes the entity from the database.

        Arguments:
            entity (object): The entity instance.
        """

    @abstractmethod
    def get(self, *pk):
        """Returns an entity instance selected by its primary key."""

    @abstractmethod
    def get_all(self):
        """Returns all entities from the database."""

    @abstractmethod
    def get_one(self, **condition):
        """Returns one entity from the database using the condition."""

    @abstractmethod
    def update(self, entity, attributes):
        """
        Updates the entity with the values of the passed attributes.

        Arguments:
            entity (object): The entity instance.
            attributes (dict): Entity attributes with new values.
        """


class PonyRepository(Repository):
    """
    Repository for working with Pony entities.

    Attributes:
        entity_class (:py:class:`~Database.Entity`): A reference to the entity class.
    """

    entity_class = None

    def get_entity_class(self):
        """
        Returns:
            :py:class:`~Database.Entity`: A reference to the entity class.
        """
        if self.entity_class is None:
            raise AttributeError('You must assign the value of the attribute "entity_class".')
        return self.entity_class

    def create(self, **attributes):
        entity = self.entity_class(**attributes)
        flush()
        return entity

    def delete(self, entity):
        assert isinstance(entity, self.entity_class)
        entity.delete()
        flush()

    def get(self, *pk):
        """
        Return an entity instance selected by its primary key.
        Raises the ObjectNotFound exception if there is no such object.
        """
        return self.entity_class.__getitem__(pk)

    def get_all(self):
        return self.entity_class.select()[:]

    def get_one(self, **kwargs):
        return self.entity_class.get(**kwargs)

    def update(self, entity, **attributes):
        assert isinstance(entity, self.entity_class)

        entity = pickle.loads(pickle.dumps(entity))

        for attr, value in attributes.items():
            setattr(entity, attr, value)

        flush()


__all__ = ('Repository', 'PonyRepository')
