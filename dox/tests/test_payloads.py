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
test_payloads
----------------------------------

Tests for `dox.payloads` module.
"""

import fixtures
import testscenarios

from dox import payloads
from dox.tests import base


class TestPayloads(base.TestCase):

    scenarios = [
        ('dox_yaml', dict(
            dox_yaml=True, tox_ini=False, travis_yaml=False,
            dox_value="testr run", tox_value=None, travis_value=None,
            payload="testr run")),
        ('dox_yaml_ignore_others', dict(
            dox_yaml=True, tox_ini=True, travis_yaml=True,
            dox_value="testr run", tox_value="setup.py test",
            travis_value="gem test"
            , payload="testr run")),
        ('tox_ini', dict(
            dox_yaml=False, tox_ini=True, travis_yaml=False,
            dox_value=None, tox_value="setup.py test", travis_value=None,
            payload="setup.py test")),
        ('tox_ignore_others', dict(
            dox_yaml=True, tox_ini=True, travis_yaml=False,
            dox_value=None, tox_value="setup.py test", travis_value="ruby",
            payload="setup.py test")),
        ('travis_yaml', dict(
            dox_yaml=False, tox_ini=False, travis_yaml=True,
            dox_value="testr run", tox_value=None, travis_value="ruby",
            payload="ruby")),
        ('travis_fallthrough', dict(
            dox_yaml=True, tox_ini=True, travis_yaml=True,
            dox_value=None, tox_value=None, travis_value="ruby",
            payload="ruby")),
    ]

    def setUp(self):
        super(TestPayloads, self).setUp()
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
            'dox.config.dox_yaml.DoxYaml.get_payload',
            base.get_fake_value(self.dox_value)))
        self.useFixture(fixtures.MonkeyPatch(
            'dox.config.tox_ini.ToxIni.get_payload',
            base.get_fake_value(self.tox_value)))
        self.useFixture(fixtures.MonkeyPatch(
            'dox.config.travis_yaml.TravisYaml.get_payload',
            base.get_fake_value(self.travis_value)))

    def test_payload(self):
        p = payloads.Payload()
        self.assertEqual(p.payload, self.payload)


def load_tests(loader, in_tests, pattern):
    return testscenarios.load_tests_apply_scenarios(loader, in_tests, pattern)
