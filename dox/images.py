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
    'get_images',
]

import dox.config.dockerfile
import dox.config.dox_yaml
import dox.config.tox_ini


def get_images():
    '''Examine the local environment and figure out where we should run.'''

    dockerfile = dox.config.dockerfile.get_dockerfile()
    dox_yaml = dox.config.dox_yaml.get_dox_yaml()
    tox_ini = dox.config.tox_ini.get_tox_ini()

    if dockerfile.exists():
        default_images = []
    else:
        # NOTE(flaper87): We should probably raise
        # `RuntimeError` if no image was specified
        default_images = ['ubuntu']

    images = []
    if dox_yaml.exists():
        images = dox_yaml.get_images()
    elif tox_ini.exists():
        images = tox_ini.get_images()

    return images or default_images
