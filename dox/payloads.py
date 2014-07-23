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

import ConfigParser
import os

import yaml


def get_payload():
    '''Examine the local environment and figure out what we should run.'''

    payload = None
    if os.path.exists('dox.yml'):
        dox_yml = yaml.load(open('dox.yml'))
        payload = dox_yml.get('commands', None)
    if payload is None and os.path.exists('tox.ini'):
        tox_ini = ConfigParser.ConfigParser()
        tox_ini.read('tox.ini')
        if tox_ini.has_option('testenv', 'commands'):
            payload = tox_ini.get('testenv', 'commands')
        else:
            payload = None
    if payload is None and os.path.exists('.travis.yml'):
        travis_yml = yaml.load(open('.travis.yml'))
        payload = travis_yml.get('script')
    return Payload(payload=payload)


class Payload(object):

    def __init__(self, payload):
        self.payload = payload

    def get_payload(self):
        if hasattr(self.payload, 'append'):
            return "\n".join(self.payload)
        return self.payload
