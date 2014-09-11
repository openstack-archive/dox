# -*- coding: utf-8 -*-
# Author: Chmouel Boudjnah <chmouel@enovance.com>
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
import mock
import os

from dox.config import tox_ini
from dox.tests import base


class TestImages(base.TestCase):

    def setUp(self):
        super(TestImages, self).setUp()

        self.toxini = tox_ini.ToxIni()
        self.toxini.tox_ini_file = os.path.join(base.SAMPLEDIR,
                                                'tox.ini')

    def test_get_tox_ini(self):
        tox_ini_new = tox_ini.ToxIni()
        with mock.patch.object(tox_ini, '_tox_ini', tox_ini_new):
            self.assertEqual(tox_ini.get_tox_ini(),
                             tox_ini_new)

    def test_exists_ini_file(self):
        self.assertTrue(self.toxini.exists())

    def test_open_tox_ini(self):
        self.assertIn('tox', self.toxini._open_tox_ini().sections())

    def test_get_images(self):
        self.assertEqual(['foo', 'bar'],
                         self.toxini.get_images())

    def test_get_commands(self):
        self.assertEqual('foobar -c',
                         self.toxini.get_commands(['-c']))

        self.assertEqual('foobar -c blah',
                         self.toxini.get_commands(
                             ['-c'], section='testenv2'))

    def test_get_prep_commands(self):
        cmd = ['pip install -U  -r/dox/requirements.txt '
               '-r/dox/test-requirements.txt']
        self.assertEqual(
            self.toxini.get_prep_commands(),
            cmd)
