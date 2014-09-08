# Copyright (c) 2014 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__all__ = [
    'get_dox_yaml',
]

import os

import yaml

_dox_yaml = None


def get_dox_yaml():
    global _dox_yaml
    if _dox_yaml is None:
        _dox_yaml = DoxYaml()
    return _dox_yaml


class DoxYaml(object):

    _yaml = None

    def _open_dox_yaml(self):
        if self._yaml is None:
            self._yaml = yaml.load(open('dox.yml', 'r'))
        return self._yaml

    def exists(self):
        return os.path.exists('dox.yml')

    def get_images(self):
        return self._open_dox_yaml().get('images', [])

    def get_commands(self, extra_args):
        return " ".join([self._open_dox_yaml().get('commands')] + extra_args)

    def get_prep_commands(self):
        return self._open_dox_yaml().get('prep', [])

    def get_add_files(self):
        return self._open_dox_yaml().get('add', [])
