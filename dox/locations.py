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


def get_location():
    '''Examine the local environment and figure out where we should run.'''

    # Set default image value
    if os.path.exists('Dockerfile'):
        image = None
    else:
        image = 'ubuntu'

    if os.path.exists('dox.yml'):
        dox_yaml = yaml.load(open('dox.yml', 'r'))
        image = dox_yaml.get('image', image)
    elif os.path.exists('tox.ini'):
        tox_ini = ConfigParser.ConfigParser()
        tox_ini.read('tox.ini')
        if tox_ini.has_option('docker', 'image'):
            image = tox_ini.get('docker', 'image')
    return Location(image=image)


class Location(object):

    def __init__(self, image):
        self.image = image

    def run(self, payload):
        print("Going to run {0} in {1}".format(
            payload.get_payload(), self.image))
