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
import argparse

import mock

import dox.runner as doxrunner
from dox.tests import base


class TestRunner(base.TestCase):

    def setUp(self):
        super(TestRunner, self).setUp()

    def test_user_mapping(self):
        dr = doxrunner.Runner(argparse.Namespace(user_map='foo:100:10',
                                                 path_map=None))
        self.assertEqual('foo', dr.user_map['username'])
        self.assertEqual(100, dr.user_map['uid'])
        self.assertEqual(10, dr.user_map['gid'])

    @mock.patch('os.getuid', return_value=12345)
    @mock.patch('os.getgid', return_value=67890)
    @mock.patch('pwd.getpwuid', return_value=['toto'])
    def test_user_mapping_default(self, os_uid, os_gid, os_username):
        dr = doxrunner.Runner(argparse.Namespace(user_map=None,
                                                 path_map=None))
        self.assertEqual('toto', dr.user_map['username'])
        self.assertEqual(12345, dr.user_map['uid'])
        self.assertEqual(67890, dr.user_map['gid'])

    def test_path_mapping(self):
        dr = doxrunner.Runner(argparse.Namespace(path_map='/Users:/home',
                                                 user_map=None))
        self.assertEqual('/Users', dr.path_map['local'])
        self.assertEqual('/home', dr.path_map['remote'])

    def test_path_mapping_extra_colon(self):
        dr = doxrunner.Runner(argparse.Namespace(path_map='/Users:/home:foo',
                                                 user_map=None))
        self.assertEqual('/Users', dr.path_map['local'])
        self.assertEqual('/home:foo', dr.path_map['remote'])

    def test_path_mapping_default(self):
        dr = doxrunner.Runner(argparse.Namespace(path_map=None,
                                                 user_map=None))
        self.assertEqual(None, dr.path_map)
