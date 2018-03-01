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

import re

from flask import render_template, request, abort, redirect, url_for
from flask.views import MethodView
from pony.orm import db_session, ObjectNotFound


class FormMixin(object):
    form_class = None
    success_endpoint = None
    success_endpoint_args = ('id',)

    def get_form(self, *args, **kwargs):
        if self.form_class is None:
            raise AttributeError('You must assign the value of the attribute "form_class".')
        return self.form_class(*args, **kwargs)

    def get_success_url(self, entity):
        if self.success_endpoint is None:
            raise AttributeError('You must assign the value of the attribute "success_endpoint".')

        kwargs = {}

        for attr in self.success_endpoint_args:
            kwargs[attr] = getattr(entity, attr)

        return url_for(self.success_endpoint, **kwargs)


class EntityView(MethodView):
    camel_patern = re.compile(r'([A-Z][a-z]+)')
    repository_class = None

    def __init__(self, template_name=None):
        self.__template_name = template_name

    @property
    def template_name(self):
        if self.__template_name is None:
            name = self.camel_patern.findall(self.__class__.__name__)
            name = '{}/{}.html'.format(name.pop(0), '_'.join(name))
            self.__template_name = name.lower()
        return self.__template_name

    def render_template(self, **context):
        return render_template(self.template_name, **context)

    def get_repository(self):
        return self.repository_class()

    def get_entity_or_abort(self, *pk):
        try:
            return self.get_repository().get(*pk)
        except ObjectNotFound:
            abort(404)


class ListView(EntityView):
    def get(self):
        entities = self.get_repository().get_all()
        return self.render_template(entities=entities)


class ShowView(EntityView):
    def get(self, id):
        task = self.get_entity_or_abort(id)
        return self.render_template(entity=task)


class CreateView(EntityView, FormMixin):
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


class UpdateView(EntityView, FormMixin):
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


class DeleteView(EntityView):
    pass


__all__ = (
    'ListView', 'ShowView', 'CreateView', 'UpdateView', 'DeleteView'
)
