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
    'get_commands',
    'Commands',
]

import os

import dox.config.dox_yaml
import dox.config.tox_ini
import dox.config.travis_yaml


def get_commands():
    '''Examine the local environment and figure out what we should run.'''

    dox_yaml = dox.config.dox_yaml.get_dox_yaml()
    tox_ini = dox.config.tox_ini.get_tox_ini()
    travis_yaml = dox.config.travis_yaml.get_travis_yaml()

    for source in (dox_yaml, tox_ini, travis_yaml):
        if source.exists():
            return source
    raise Exception("dox cannot figure out what command to run")


class Commands(object):

    def __init__(self, extra_args=[]):
        self.source = get_commands()
        self.args = []
        self.extra_args = extra_args

    def _test_command_as_script(self, shell='/bin/sh'):
        """ Combine test command(s) into a master script file.

        The script, using the given shell, will be created in the .dox
        subdirectory of the current directory.
        """
        dox_dir = '.dox'
        master_script = os.path.join(dox_dir, 'master_script.sh')

        if not os.path.exists(dox_dir):
            os.mkdir(dox_dir, 0755)

        with open(master_script, "w") as f:
            f.write("#!" + shell + "\n")
            f.write("\n".join(self.source.get_commands(self.extra_args)))

        os.chmod(master_script, 0700)
        return master_script

    def test_command(self):
        """ Return the command to execute in the container.

        If there is more than one command, we combine them into a master
        script to execute. Otherwise, we just issue the command normally
        on the docker command line.
        """
        commands = self.source.get_commands(self.extra_args)

        if len(commands) > 1:
            return self._test_command_as_script()

        ret = commands[0] + ' ' + ' '.join(self.args)
        return ret.strip()

    def prep_commands(self):
        return self.source.get_prep_commands()

    def get_add_files(self):
        return self.source.get_add_files()

    def append(self, args):
        self.args = args
