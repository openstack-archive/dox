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
    'get_travis_yaml',
]

import os

import yaml

_travis_yaml = None


def get_travis_yaml():
    global _travis_yaml
    if _travis_yaml is None:
        _travis_yaml = TravisYaml()
    return _travis_yaml


class TravisYaml(object):

    _yaml = None

    def _open_travis_yaml(self):
        if self._yaml is None:
            self._yaml = yaml.load(open('travis.yml', 'r'))
        return self._yaml

    def exists(self):
        return os.path.exists('travis.yml')

    def get_payload(self, payload):
        return self._open_travis_yaml().get('script', payload)
