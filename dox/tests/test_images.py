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
test_images
--------------

Tests for `dox.images` module.
"""

import fixtures
import testscenarios

from dox import images
from dox.tests import base


def get_fake_image(value):
    if value is not None:
        def fake_value(self):
            return value
    else:
        def fake_value(self):
            return ['ubuntu']
    return fake_value


class TestImages(base.TestCase):

    scenarios = [
        ('have_dockerfile', dict(
            dockerfile=True, tox_ini=False, dox_yaml=False,
            tox_value=[], dox_value=[], images=[])),
        ('no_dockerfile', dict(
            dockerfile=False, tox_ini=False, dox_yaml=False,
            tox_value=[], dox_value=[], images=['ubuntu'])),
        ('tox_no_docker', dict(
            dockerfile=False, tox_ini=True, dox_yaml=False,
            tox_value=[], dox_value=[], images=['ubuntu'])),
        ('tox_docker', dict(
            dockerfile=False, tox_ini=True, dox_yaml=False,
            tox_value=['tox_docker'], dox_value=[], images=['tox_docker'])),
        ('dox_image', dict(
            dockerfile=False, tox_ini=False, dox_yaml=True,
            tox_value=[], dox_value=[], images=['ubuntu'])),
        ('dox_no_image', dict(
            dockerfile=False, tox_ini=False, dox_yaml=True,
            tox_value=[], dox_value=['dox_value'], images=['dox_value'])),
        ('both_dox_wins', dict(
            dockerfile=False, tox_ini=True, dox_yaml=True,
            tox_value=['tox_wins'], dox_value=['dox_wins'],
            images=['dox_wins'])),
        ('both_no_dox', dict(
            dockerfile=False, tox_ini=True, dox_yaml=True,
            tox_value=['tox_wins'], dox_value=[], images=['ubuntu'])),
        ('both_dockerfile_passthru', dict(
            dockerfile=True, tox_ini=True, dox_yaml=True,
            tox_value=[], dox_value=[], images=[])),
        ('all_dockerfile_dox_override', dict(
            dockerfile=True, tox_ini=True, dox_yaml=True,
            tox_value=[], dox_value=['dox_wins'], images=['dox_wins'])),
        ('all_dockerfile_tox_loses', dict(
            dockerfile=True, tox_ini=True, dox_yaml=True,
            tox_value=['tox_wins'], dox_value=[], images=[])),
    ]

    def setUp(self):
        super(TestImages, self).setUp()
        self.useFixture(fixtures.MonkeyPatch(
            'dox.config.dockerfile.Dockerfile.exists',
            base.bool_to_fake(self.dockerfile)))
        self.useFixture(fixtures.MonkeyPatch(
            'dox.config.dox_yaml.DoxYaml.exists',
            base.bool_to_fake(self.dox_yaml)))
        self.useFixture(fixtures.MonkeyPatch(
            'dox.config.tox_ini.ToxIni.exists',
            base.bool_to_fake(self.tox_ini)))
        self.useFixture(fixtures.MonkeyPatch(
            'dox.config.dox_yaml.DoxYaml.get_images',
            get_fake_image(self.dox_value)))
        self.useFixture(fixtures.MonkeyPatch(
            'dox.config.tox_ini.ToxIni.get_images',
            get_fake_image(self.tox_value)))

    def test_images(self):
        image = images.get_images({})
        self.assertEqual(image, self.images)


def load_tests(loader, in_tests, pattern):
    return testscenarios.load_tests_apply_scenarios(loader, in_tests, pattern)
