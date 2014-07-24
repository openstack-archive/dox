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
    'get_payload',
    'Payload',
]

import dox.config.dox_yaml
import dox.config.tox_ini
import dox.config.travis_yaml


def get_payload():
    '''Examine the local environment and figure out what we should run.'''

    dox_yaml = dox.config.dox_yaml.get_dox_yaml()
    tox_ini = dox.config.tox_ini.get_tox_ini()
    travis_yaml = dox.config.travis_yaml.get_travis_yaml()

    payload = None
    for source in (dox_yaml, tox_ini, travis_yaml):
        if payload is None and source.exists():
            payload = source.get_payload(payload)
    return payload


class Payload(object):

    def __init__(self):
        self.payload = get_payload()
        self.args = []

    def __str__(self):
        if hasattr(self.payload, 'append'):
            return "\n".join(self.payload)
        return self.payload + ' ' + ' '.join(self.args)

    def append(self, args):
        self.args = args
