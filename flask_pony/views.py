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

from flask import render_template, request, abort, redirect, url_for
from flask.views import MethodView
from pony.orm import ObjectNotFound

from .orm import FormBuilder
from .utils import get_route_param_names, camelcase2list


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
        return self.get_form_class()(*args, **kwargs)

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
            name = camelcase2list(self.__class__.__name__)
            name = '{}/{}.html'.format(name.pop(0), '_'.join(name))
            self.template_name = name.lower()
        return self.template_name

    def render_template(self, **context):
        """Render a template with passed context."""
        return render_template(self.get_template_name(), **context)


class EntityView(BaseView, EntityMixin):
    """Base view for working with entities."""


class ProcessFormView(EntityView, FormMixin):
    """Render a form on GET and processes it on POST."""

    form_class = FormBuilder

    def get_form_class(self):
        if issubclass(self.form_class, FormBuilder):
            self.form_class = self.form_class.get_instance(self.get_repository().get_entity_class())
        return super(ProcessFormView, self).get_form_class()

    # def process_form(self, form):
    #     """"""
    #     raise NotImplementedError
    #
    # def form_valid(selfself, form, entity):
    #     """Runs if the form is processed successfully."""
    #
    # def form_invalid(self, form, entity):
    #     """Runs if errors occurred while processing the form."""


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

    def _create_entity(self, form):
        kwargs = form.entity_kwargs
        return self.get_repository().create(**kwargs)

    def get(self):
        return self.render_template(form=self.get_form())

    def post(self):
        form = self.get_form(request.form)

        if form.validate_on_submit():
            entity = self._create_entity(form)
            return redirect(self.get_success_url(entity))

        return self.render_template(form=form)


class UpdateView(ProcessFormView):
    """View for updating an entity."""

    def _update_entity(self, entity, form):
        kwargs = form.entity_kwargs
        self.get_repository().update(entity, **kwargs)

    def get(self, id):
        entity = self.get_entity_or_abort(id)
        form = self.get_form(obj=entity)
        return self.render_template(form=form, entity=entity)

    def post(self, id):
        entity = self.get_entity_or_abort(id)
        form = self.get_form(request.form, obj=entity)

        if form.validate_on_submit():
            self._update_entity(entity, form)
            return redirect(self.get_success_url(entity))

        return self.render_template(form=form, entity=entity)


class DeleteView(ProcessFormView):
    """View for deleting an entity."""

    def post(self, id):
        entity = self.get_entity_or_abort(id)
        entity.delete()
        return redirect(self.get_success_url())


__all__ = (
    'ListView', 'ShowView', 'CreateView', 'UpdateView', 'DeleteView'
)
