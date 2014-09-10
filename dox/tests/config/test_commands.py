# -*- coding: utf-8 -*-

# Copyright (c) 2014 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
test_commands
----------------------------------

Tests for `dox.commands` module.
"""

import fixtures
import testscenarios

from dox import commands
from dox.tests import base


def get_fake_command(value):
    def fake_value(self, args):
        return value
    return fake_value


class TestCommands(base.TestCase):

    scenarios = [
        ('dox_yaml', dict(
            dox_yaml=True, tox_ini=False, travis_yaml=False,
            dox_value=["testr run"], tox_value=None, travis_value=None,
            commands="testr run")),
        ('dox_yaml_ignore_others', dict(
            dox_yaml=True, tox_ini=True, travis_yaml=True,
            dox_value=["testr run"], tox_value=["setup.py test"],
            travis_value=["gem test"],
            commands="testr run")),
        ('tox_ini', dict(
            dox_yaml=False, tox_ini=True, travis_yaml=False,
            dox_value=None, tox_value=["setup.py test"], travis_value=None,
            commands="setup.py test")),
        ('travis_yaml', dict(
            dox_yaml=False, tox_ini=False, travis_yaml=True,
            dox_value=["testr run"], tox_value=None, travis_value=["ruby"],
            commands="ruby")),
    ]

    def setUp(self):
        super(TestCommands, self).setUp()
        self.useFixture(fixtures.MonkeyPatch(
            'dox.config.dox_yaml.DoxYaml.exists',
            base.bool_to_fake(self.dox_yaml)))
        self.useFixture(fixtures.MonkeyPatch(
            'dox.config.tox_ini.ToxIni.exists',
            base.bool_to_fake(self.tox_ini)))
        self.useFixture(fixtures.MonkeyPatch(
            'dox.config.travis_yaml.TravisYaml.exists',
            base.bool_to_fake(self.travis_yaml)))
        self.useFixture(fixtures.MonkeyPatch(
            'dox.config.dox_yaml.DoxYaml.get_commands',
            get_fake_command(self.dox_value)))
        self.useFixture(fixtures.MonkeyPatch(
            'dox.config.tox_ini.ToxIni.get_commands',
            get_fake_command(self.tox_value)))
        self.useFixture(fixtures.MonkeyPatch(
            'dox.config.travis_yaml.TravisYaml.get_commands',
            get_fake_command(self.travis_value)))

    def test_commands(self):
        p = commands.Commands()
        self.assertEqual(p.test_command(), self.commands)


def load_tests(loader, in_tests, pattern):
    return testscenarios.load_tests_apply_scenarios(loader, in_tests, pattern)
