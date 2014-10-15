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

import os
import yaml

import dox.config.base as base


__all__ = [
    'get_dox_yaml',
]

_dox_yaml = None


class DoxYamlSectionNotFound(Exception):
    pass


def get_dox_yaml(options):
    global _dox_yaml
    if _dox_yaml is None:
        _dox_yaml = DoxYaml(options)
    return _dox_yaml


class DoxYaml(base.ConfigBase):

    _yaml = None
    dox_file = 'dox.yml'
    default_section = 'testing'
    default_keys_of_section = ['images', 'commands', 'add', 'prep']

    def get_section(self, yaml, section):
        if section == '_default':
            section = self.default_section

        # NOTE(chmou): This is for compatibility mode with dox.yml with no
        # sections, probably need to be removed in the future
        if (section is None and
           (all(i in yaml.keys() for i in self.default_keys_of_section)
               or all(i in self.default_keys_of_section
                      for i in yaml.keys()))):
            return yaml
        elif not section:
            if self.default_section in yaml.keys():
                return yaml.get(self.default_section)
            raise DoxYamlSectionNotFound("You need to specify a section.")
        elif section not in yaml.keys():
            raise DoxYamlSectionNotFound(section)
        elif section:
            return yaml.get(section)

    def _open_dox_yaml(self):
        if self._yaml is None:
            with open(self.dox_file, 'r') as f:
                self._yaml = yaml.load(f)
        return self.get_section(self._yaml,
                                self.options.get('section'))

    def source_name(self):
        return self.dox_file

    def exists(self):
        return os.path.exists(self.dox_file)

    def get_images(self):
        return self._open_dox_yaml().get('images', [])

    def get_commands(self, extra_args):
        return self._open_dox_yaml().get('commands', [])

    def get_prep_commands(self):
        return self._open_dox_yaml().get('prep', [])

    def get_add_files(self):
        return self._open_dox_yaml().get('add', [])
