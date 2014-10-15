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

from six.moves.configparser import ConfigParser

import dox.config.base as base


__all__ = [
    'get_tox_ini',
]

_tox_ini = None


def get_tox_ini(options):
    global _tox_ini
    if _tox_ini is None:
        _tox_ini = ToxIni(options)
    return _tox_ini


class ToxIni(base.ConfigBase):

    _ini = None
    tox_ini_file = 'tox.ini'
    default_section = 'testenv'

    def _open_tox_ini(self):
        if self._ini is None:
            self._ini = ConfigParser()
            self._ini.read(self.tox_ini_file)
        return self._ini

    def source_name(self):
        return self.tox_ini_file

    def exists(self):
        return os.path.exists(self.tox_ini_file)

    def get_images(self):
        ini = self._open_tox_ini()
        if ini.has_option('docker', 'images'):
            return ini.get('docker', 'images').split(',')

    def get_commands(self, extra_args):
        """Get commands to run from the config file.

        If any of the commands contain the string '{posargs}', then this
        is replaced with the extra_args value.
        """
        section = self.options.get('section',
                                   self.default_section)

        if section == '_default':
            section = self.default_section

        ini = self._open_tox_ini()
        commands = ini.get(section, 'commands').split("\n")
        extra_args = " ".join(extra_args)

        scrubbed = []
        for cmd in commands:
            if '{posargs}' in cmd:
                scrubbed.append(cmd.replace('{posargs}', extra_args))
            else:
                scrubbed.append(cmd)
        return scrubbed

    def get_prep_commands(self):
        ini = self._open_tox_ini()
        deps = ""
        if ini.has_option('testenv', 'deps'):
            deps = ini.get('testenv', 'deps')
        deps = deps.replace('{toxinidir}', '/dox').replace('\n', ' ')
        if deps.strip() == '':
            return []
        install_command = "pip install -U"
        if ini.has_option('testenv', 'install_command'):
            install_command = ini.get('testenv', 'install_command')
        install_command = install_command.replace('{opts}', '')
        install_command = install_command.replace('{packages}', deps)
        return [install_command]

    def get_add_files(self):
        return [d for d in os.listdir('.') if d.endswith('requirements.txt')]
