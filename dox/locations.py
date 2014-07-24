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
    'get_image',
]

import dox.config.dockerfile
import dox.config.dox_yaml
import dox.config.tox_ini


def get_image():
    '''Examine the local environment and figure out where we should run.'''

    dockerfile = dox.config.dockerfile.get_dockerfile()
    dox_yaml = dox.config.dox_yaml.get_dox_yaml()
    tox_ini = dox.config.tox_ini.get_tox_ini()

    # Set default image value
    if dockerfile.exists():
        image = None
    else:
        image = 'ubuntu'

    if dox_yaml.exists():
        image = dox_yaml.get_image(image)
    elif tox_ini.exists():
        image = tox_ini.get_image(image)
    return image
