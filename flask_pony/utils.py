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

from flask import current_app


__all__ = (
    'camelcase2list', 'get_route_param_names'
)


def camelcase2list(s, lower=False):
    """Converts a camelcase string to a list."""
    s = re.findall(r'([A-Z][a-z0-9]+)', s)
    return [w.lower() for w in s] if lower else s


def get_route_param_names(endpoint):
    """Returns parameter names from the route."""
    try:
        g = current_app.url_map.iter_rules(endpoint)
        return next(g).arguments
    except KeyError:
        return {}


def camel_to_snake(name):
    result = []

    for i, c in enumerate(name):
        if c.isupper() and i:
            result.append(name[:i])
            name = name[i:]

    result.append(name)

    return '_'.join(result).lower()


def snake_to_camel(name):
    return ''.join(name.title().split('_'))
