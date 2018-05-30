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

from .utils import camel_to_snake


def route(obj, rule, *args, **kwargs):
    """Decorator for the View classes."""
    def decorator(cls):
        endpoint = kwargs.get('endpoint', camel_to_snake(cls.__name__))
        kwargs['view_func'] = cls.as_view(endpoint)
        obj.add_url_rule(rule, *args, **kwargs)
        return cls
    return decorator
