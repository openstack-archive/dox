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
test_locations
----------------------------------

Tests for `dox location` module.
"""

import fixtures
import testscenarios

from dox import locations
from dox.tests import base


def fake_does_exist(self):
    return True


def fake_does_not_exist(self):
    return False


def get_fake_value(value):
    if value:
        def fake_value(self, image):
            return value
    else:
        def fake_value(self, image):
            return image
    return fake_value


def bool_to_fake(val):
    if val:
        return fake_does_exist
    else:
        return fake_does_not_exist


class TestLocations(base.TestCase):

    scenarios = [
        ('have_dockerfile', dict(
            dockerfile=True, tox_ini=False, dox_yaml=False,
            tox_value=None,  dox_value=None, image=None)),
        ('no_dockerfile', dict(
            dockerfile=False, tox_ini=False, dox_yaml=False,
            tox_value=None,  dox_value=None, image='ubuntu')),
        ('tox_no_docker', dict(
            dockerfile=False, tox_ini=True, dox_yaml=False,
            tox_value=None,  dox_value=None, image='ubuntu')),
        ('tox_docker', dict(
            dockerfile=False, tox_ini=True, dox_yaml=False,
            tox_value='tox_docker',  dox_value=None, image='tox_docker')),
        ('dox_image', dict(
            dockerfile=False, tox_ini=False, dox_yaml=True,
            tox_value=None,  dox_value=None, image='ubuntu')),
        ('dox_no_image', dict(
            dockerfile=False, tox_ini=False, dox_yaml=True,
            tox_value=None,  dox_value='dox_value', image='dox_value')),
        ('both_dox_wins', dict(
            dockerfile=False, tox_ini=True, dox_yaml=True,
            tox_value='tox_wins',  dox_value='dox_wins', image='dox_wins')),
        ('both_no_dox', dict(
            dockerfile=False, tox_ini=True, dox_yaml=True,
            tox_value='tox_wins',  dox_value=None, image='ubuntu')),
        ('both_dockerfile_passthru', dict(
            dockerfile=True, tox_ini=True, dox_yaml=True,
            tox_value=None,  dox_value=None, image=None)),
        ('all_dockerfile_dox_override', dict(
            dockerfile=True, tox_ini=True, dox_yaml=True,
            tox_value=None,  dox_value='dox_wins', image='dox_wins')),
        ('all_dockerfile_tox_loses', dict(
            dockerfile=True, tox_ini=True, dox_yaml=True,
            tox_value='tox_wins',  dox_value=None, image=None)),
    ]

    def setUp(self):
        super(TestLocations, self).setUp()
        self.useFixture(fixtures.MonkeyPatch(
            'dox.config.dockerfile.Dockerfile.exists',
            bool_to_fake(self.dockerfile)))
        self.useFixture(fixtures.MonkeyPatch(
            'dox.config.dox_yaml.DoxYaml.exists',
            bool_to_fake(self.dox_yaml)))
        self.useFixture(fixtures.MonkeyPatch(
            'dox.config.tox_ini.ToxIni.exists',
            bool_to_fake(self.tox_ini)))
        self.useFixture(fixtures.MonkeyPatch(
            'dox.config.dox_yaml.DoxYaml.get_image',
            get_fake_value(self.dox_value)))
        self.useFixture(fixtures.MonkeyPatch(
            'dox.config.tox_ini.ToxIni.get_image',
            get_fake_value(self.tox_value)))

    def test_location(self):
        l = locations.Location()
        self.assertEqual(l.image, self.image)


def load_tests(loader, in_tests, pattern):
    return testscenarios.load_tests_apply_scenarios(loader, in_tests, pattern)
