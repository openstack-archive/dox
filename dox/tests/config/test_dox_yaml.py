# -*- coding: utf-8 -*-

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

import os

import dox.config.base as cfg_base

from dox.config import dox_yaml
from dox.tests import base


class TestDoxYaml(base.TestCase):

    def setUp(self):
        super(TestDoxYaml, self).setUp()
        self.doxyaml = dox_yaml.DoxYaml({})
        self.doxyaml.dox_file = os.path.join(base.SAMPLEDIR,
                                             'dox.yaml')

    def test_base_class(self):
        self.assertIsInstance(self.doxyaml, cfg_base.ConfigBase)

    def test_dox_yaml_old_parsing(self):
        self.doxyaml = dox_yaml.DoxYaml({})
        self.doxyaml.dox_file = os.path.join(base.SAMPLEDIR,
                                             'dox-old.yaml')
        self.assertEqual(
            self.doxyaml.default_keys_of_section,
            self.doxyaml._open_dox_yaml().keys())

    def test_dox_yaml_not_finding_section(self):
        self.doxyaml = dox_yaml.DoxYaml({'section': 'foobar'})
        self.doxyaml.dox_file = os.path.join(base.SAMPLEDIR,
                                             'dox.yaml')
        self.assertRaises(
            dox_yaml.DoxYamlSectionNotFound,
            self.doxyaml._open_dox_yaml)

    def test_dox_yaml_with_default_session(self):
        self.doxyaml = dox_yaml.DoxYaml({})
        self.doxyaml.dox_file = os.path.join(base.SAMPLEDIR,
                                             'dox.yaml')
        self.assertEqual(
            self.doxyaml.default_keys_of_section,
            self.doxyaml._open_dox_yaml().keys())

    def test_dox_yaml_new_parsing(self):
        self.assertEqual(
            self.doxyaml.default_keys_of_section,
            self.doxyaml._open_dox_yaml().keys())

    # TOOD(chmou): Finish tests of dox_yaml.py
