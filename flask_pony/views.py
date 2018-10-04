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

from flask import render_template, request, abort, redirect, url_for, flash
from flask.views import MethodView
from pony.orm import ObjectNotFound

from .orm import FormBuilder
from .utils import get_route_param_names, camel_to_list


class FormMixin(object):
    """
    Mixin to work with HTML-forms.

    Attributes:
        form_class (:py:class:`~flask_wtf.FlaskForm`): A reference to the base class of the form.
        success_endpoint (:obj:`str`): The endpoint to which to go if the form was processed successfully.
    """

    form_class = None
    success_endpoint = None

    def get_form_class(self):
        """
        Returns:
             :py:class:`~flask_wtf.FlaskForm`: A reference to the base class of the form.
        """
        if self.form_class is None:
            raise AttributeError('You must assign the value of the attribute "form_class".')
        return self.form_class

    def get_form(self, *args, **kwargs):
        """
        Returns:
            :py:class:`~flask_wtf.FlaskForm`: An instance of the form class.
        """
        if 'obj' not in kwargs:
            kwargs['obj'] = self.get_object()
        return self.get_form_class()(*args, **kwargs)

    def get_object(self):
        return getattr(self, '_object', None)

    def set_object(self, obj):
        self._object = obj

    def get_success_url(self, obj=None):
        """
        Args:
            obj (object): The object whose property values are used to build the URL.

        Returns:
            str: The URL to which to go if the form was processed successfully.
        """
        if self.success_endpoint is None:
            raise AttributeError('You must assign the value of the attribute "success_endpoint".')

        if obj:
            kwargs = {p: getattr(obj, p) for p in get_route_param_names(self.success_endpoint)}
        else:
            kwargs = {}

        return url_for(self.success_endpoint, **kwargs)

    def form_valid(self, form):
        """Runs if the form is processed successfully."""
        raise NotImplementedError

    def form_invalid(self, form):
        """Runs if errors occurred while processing the form."""
        raise NotImplementedError


class EntityMixin(object):
    """
    Mixin to work with Pony entities.

    Attributes:
        repository_class (:py:class:`~flask_pony.repositories.PonyRepository`): A reference to the class of the repository.
    """

    repository_class = None

    def get_repository_class(self):
        """
        Returns:
            :py:class:`~flask_pony.repositories.PonyRepository`: A reference to the class of the repository.
        """
        if self.repository_class is None:
            raise AttributeError('You must assign the value of the attribute "repository_class".')
        return self.repository_class

    def get_repository(self, *args, **kwargs):
        """
        Returns:
            :py:class:`~flask_pony.repositories.PonyRepository`: An instance of the repository class.
        """
        return self.get_repository_class()(*args, **kwargs)

    def get_entity_or_abort(self, *pk):
        """
        Arguments:
            pk: primary key.

        Returns:
            :py:attr:`~Database.Entity`: An entity instance selected by its primary key.

        Raises:
            :py:exc:`HTTPException`: If there is no such object.
        """
        try:
            return self.get_repository().get(*pk)
        except ObjectNotFound:
            abort(404)


class BaseView(MethodView):
    """
    Arguments:
        template_name (:obj:`str`):
            The name of the template, can be passed to the :py:meth:`~flask.views.View.as_view` method.

    Attributes:
        template_name (:obj:`str`): The name of the template.
    """

    template_name = None

    def __init__(self, template_name=None):
        if template_name:
            self.template_name = template_name

    def get_template_name(self):
        """
        Returns the name of the template.

        If the template_name property is not set, the value will be generated automatically based on the class name.

        Example:
            >>> class MyEntityAction(BaseView): pass
            >>> view = MyEntityAction()
            >>> view.get_template_name()
            "my_entity/action.html"

        """
        if self.template_name is None:
            name = camel_to_list(self.__class__.__name__, lower=True)
            self.template_name = '{1}/{0}.html'.format(name.pop(), '_'.join(name))
        return self.template_name

    def render_template(self, **context):
        """Render a template with passed context."""
        return render_template(self.get_template_name(), **context)


class EntityView(BaseView, EntityMixin):
    """Base view for working with entities."""


class ProcessFormView(EntityView, FormMixin):
    """Render a form on GET and processes it on POST."""

    form_builder = None
    form_class = None

    def get_form_builder(self):
        if self.form_builder is None:
            self.form_builder = FormBuilder()

        entity_class = self.get_repository().get_entity_class()
        self.form_builder.set_entity_class(entity_class)

        return self.form_builder

    def get_form_class(self):
        if self.form_class is None:
            return self.get_form_builder().get_form()
        return super(ProcessFormView, self).get_form_class()

    def get_entity_or_abort(self, *pk):
        entity = super(ProcessFormView, self).get_entity_or_abort(*pk)
        self.set_object(entity)
        return entity

    def post(self, *args, **kwargs):
        form = self.get_form()

        if form.validate_on_submit():
            return self.form_valid(form)

        return self.form_invalid(form)


class ListView(EntityView):
    """View for listing an entities retrieved using the repository."""

    def get(self):
        entities = self.get_repository().get_all()
        return self.render_template(entities=entities)


class ShowView(EntityView):
    """View for displaying an entity instance selected by its primary key."""

    def get(self, id):
        entity = self.get_entity_or_abort(id)
        return self.render_template(entity=entity)


class CreateView(ProcessFormView):
    """View for creating a new entity."""

    def get(self):
        return self.render_template(form=self.get_form())

    def form_valid(self, form):
        kwargs = form.entity_kwargs
        entity = self.get_repository().create(**kwargs)
        self.set_object(entity)
        return redirect(self.get_success_url(entity))

    def form_invalid(self, form):
        return self.render_template(form=form)


class UpdateView(ProcessFormView):
    """View for updating an entity."""

    def get(self, id):
        entity = self.get_entity_or_abort(id)
        form = self.get_form()
        return self.render_template(form=form, entity=entity)

    def form_valid(self, form):
        entity = self.get_object()
        kwargs = form.entity_kwargs
        self.get_repository().update(entity, **kwargs)
        return redirect(self.get_success_url(entity))

    def form_invalid(self, form):
        return self.render_template(form=form, entity=self.get_object())

    def post(self, id):
        self.get_entity_or_abort(id)
        return super(UpdateView, self).post()


class DeleteView(ProcessFormView):
    """View for deleting an entity."""

    def form_valid(self, form):
        entity = self.get_object()
        entity.delete()
        return redirect(self.get_success_url())

    # def form_invalid(self, form):
    #     flash('Could not delete entity.', 'error')
    #     return redirect(self.get_success_url())

    def post(self, id):
        return self.delete(id)

    def delete(self, id):
        self.get_entity_or_abort(id)
        return self.form_valid(None)


__all__ = (
    'ListView', 'ShowView', 'CreateView', 'UpdateView', 'DeleteView'
)
