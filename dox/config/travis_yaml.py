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
    'get_travis_yaml',
]

_travis_yaml = None


def get_travis_yaml():
    global _travis_yaml
    if _travis_yaml is None:
        _travis_yaml = TravisYaml()
    return _travis_yaml


class TravisYaml(base.ConfigBase):

    _yaml = None
    _travis_file = 'travis.yml'

    def _open_travis_yaml(self):
        if self._yaml is None:
            with open('travis.yml', 'r') as f:
                self._yaml = yaml.load(f)
        return self._yaml

    def source_name(self):
        return self._travis_file

    def exists(self):
        return os.path.exists(self._travis_file)

    def get_commands(self, command):
        return self._open_travis_yaml().get('script', command)

    def get_prep_commands(self):
        travis_yaml = self._open_travis_yaml()
        prep = []

        for key in ('before_install', 'install', 'before_script'):
            if key in travis_yaml:
                val = travis_yaml[key]
                if hasattr(val, 'append'):
                    prep.extend(val)
                else:
                    prep.append(val)
        return []

    # TODO(Shrews): Implement this
    def get_add_files(self):
        return []

    # TODO(Shrews): Implement this
    def get_images(self):
        return []
