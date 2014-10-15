# -*- coding: utf-8 -*-
# Author: Chmouel Boudjnah <chmouel@chmouel.com>
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

import dox.cmd
from dox.tests import base

default_argp = argparse.Namespace(user_map=None, command=None,
                                  environment=None, extra_args=None,
                                  debug=None, noop=True,
                                  images=None, path_map=None)


class TestCmd(base.TestCase):

    @mock.patch('dox.runner.Runner.is_docker_installed',
                return_value=False)
    def test_runner(self, installed_mock):
        self.assertRaises(SystemExit, dox.cmd.runner, default_argp)

    @mock.patch('dox.cmd.run_dox')
    @mock.patch('dox.config.cmdline.CommandLine')
    def test_multiple_images_one_command(self, m_cmdline, m_run_dox):
        argp = default_argp
        argp.images = 'foo, bar'
        argp.command = '/bin/true'
        dox.cmd.runner(argp)

        self.assertTrue(m_cmdline.called)
        # silly but i'm not sure how to test that in a proper way
        self.assertEqual(['foo', 'bar'],
                         m_run_dox.call_args_list[0][0][1])

    @mock.patch('dox.cmd.run_dox')
    @mock.patch('dox.images.get_images')
    def test_multiple_environments(self, m_get_images, m_run_dox):
        argp = default_argp
        argp.environment = 'env1, env2'
        dox.cmd.runner(argp)

        self.assertEqual(2, m_get_images.call_count)
        self.assertEqual(2, m_run_dox.call_count)

    @mock.patch('dox.cmd.run_dox')
    @mock.patch('dox.images.get_images')
    def test_multiple_environments_images(self, m_get_images, m_run_dox):
        argp = default_argp
        argp.images = 'foo, bar'
        argp.environment = 'env1, env2'
        dox.cmd.runner(argp)

        self.assertEqual(0, m_get_images.call_count)
        self.assertEqual(2, m_run_dox.call_count)

    @mock.patch('dox.cmd.run_dox')
    @mock.patch('dox.images.get_images')
    def test_default(self, m_get_images, m_run_dox):
        dox.cmd.runner(default_argp)

        self.assertEqual('_default',
                         m_get_images.call_args_list[0][0][0].get('section'))

    @mock.patch('dox.runner.Runner')
    def test_run_dox(self, m_runner):
        dox.cmd.run_dox(default_argp, ['1', '2', '3'], '/bin/echo')
        self.assertEqual(1, m_runner.call_count)
