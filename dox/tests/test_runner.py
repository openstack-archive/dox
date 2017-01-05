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
import os
import shutil  # noqa
import tempfile

import mock

import dox.runner as doxrunner
from dox.tests import base


class FakeCommands(object):
    def __init__(self, commands=None, files_to_add=None):
        self.commands = commands or ["command1", "command2"]
        self.files_to_add = files_to_add or ["file1"]

    def prep_commands(self):
        return self.commands

    def get_add_files(self):
        return self.files_to_add


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

    def test_is_docker_installed(self):
        dr = doxrunner.Runner(argparse.Namespace(
            path_map=None,
            user_map=None))

        def mydocker_cmd(dr, *args):
            raise OSError
        dr._docker_cmd = mydocker_cmd
        self.assertFalse(dr.is_docker_installed())

        def mydocker_cmd(dr, *args):
            return True
        dr._docker_cmd = mydocker_cmd
        self.assertTrue(dr.is_docker_installed())

    def test_docker_cmd(self):
        dr = doxrunner.Runner(argparse.Namespace(user_map=None,
                                                 path_map=None,
                                                 debug=False))
        dr._run_shell_command = mock.MagicMock()
        dr._docker_cmd("version")
        dr._run_shell_command.assert_called_with(
            ['docker', 'version']
        )

        dr = doxrunner.Runner(argparse.Namespace(user_map=None,
                                                 path_map=None,
                                                 debug=True))
        dr._run_shell_command = mock.MagicMock()
        dr._docker_cmd("version")
        dr._run_shell_command.assert_called_with(
            ['docker', 'version']
        )

        dr = doxrunner.Runner(argparse.Namespace(user_map=None,
                                                 path_map=None,
                                                 debug=True))
        dr._run_shell_command = mock.Mock()
        dr._run_shell_command.side_effect = OSError("Boom")
        self.assertRaises(OSError, dr._docker_cmd, "version")

    def test_build_images_pass(self):
        dr = doxrunner.Runner(argparse.Namespace(path_map=None,
                                                 user_map=None))
        dr.have_test_image = mock.Mock()
        dr.return_value = True
        self.assertIsNone(dr.build_test_image("image", FakeCommands()))

    @mock.patch.multiple("shutil", rmtree=mock.DEFAULT,
                         copy=mock.DEFAULT)
    def test_build_images(self, rmtree, copy):
        my_temp_file = tempfile.mkdtemp()
        docker_written = os.path.join(my_temp_file, "Dockerfile")
        fk = FakeCommands(["toto1", "toto2"],
                          ["blah3", "blah4"])

        dr = doxrunner.Runner(argparse.Namespace(
            quiet=False, noop=False,
            rebuild=True, debug=True,
            path_map=None,
            user_map=None))
        m_docker_build = dr._docker_build = mock.Mock()
        with mock.patch.object(tempfile, "mkdtemp", return_value=my_temp_file):
            dr.build_test_image("myimage", fk)

        m_docker_build.assert_called_once_with(
            dr.test_image_name, my_temp_file)

        # Only the last one
        copy.assert_called_with('blah4',
                                os.path.join(my_temp_file, "blah4"))
        self.assertTrue(copy.called)
        self.assertTrue(rmtree.called)
        self.assertTrue(os.path.exists(docker_written))
        um = dr.user_map

        expected = """FROM %s
RUN useradd -M -U -d /src -u %s %s
ADD blah3 /dox/
ADD blah4 /dox/
WORKDIR /dox
RUN toto1

RUN toto2
""""" % ("myimage", um['uid'], um['username'])

        self.assertEqual(expected, open(docker_written, 'r').read())

    def test_have_base_image(self):
        dr = doxrunner.Runner(argparse.Namespace(
            rebuild=True,
            rebuild_all=False,
            path_map=None,
            user_map=None))
        dr._get_image_list = mock.MagicMock()
        self.assertFalse(dr.have_base_image())

        dr = doxrunner.Runner(argparse.Namespace(
            rebuild=False,
            rebuild_all=True,
            path_map=None,
            user_map=None))
        dr._get_image_list = mock.MagicMock()
        self.assertFalse(dr.have_base_image())

        dr = doxrunner.Runner(argparse.Namespace(
            rebuild=False,
            rebuild_all=False,
            path_map=None,
            user_map=None))
        dr._get_image_list = mock.MagicMock()
        dr._get_image_list.return_value = [dr.base_image_name]
        self.assertTrue(dr.have_base_image())

        dr = doxrunner.Runner(argparse.Namespace(
            rebuild=False,
            rebuild_all=False,
            path_map=None,
            user_map=None))
        dr._get_image_list = mock.MagicMock()
        dr._get_image_list.return_value = []
        self.assertFalse(dr.have_base_image())

    def test_have_test_image(self):
        # NOTE(chmou): this probably would need some refactoring with
        # have_base_image
        dr = doxrunner.Runner(argparse.Namespace(
            rebuild=True,
            rebuild_all=False,
            path_map=None,
            user_map=None))
        self.assertFalse(dr.have_test_image())

        dr = doxrunner.Runner(argparse.Namespace(
            rebuild=False,
            rebuild_all=True,
            path_map=None,
            user_map=None))
        self.assertFalse(dr.have_test_image())

        dr = doxrunner.Runner(argparse.Namespace(
            rebuild=False,
            rebuild_all=False,
            path_map=None,
            user_map=None))
        dr._get_image_list = mock.MagicMock()
        dr._get_image_list.return_value = [dr.test_image_name]
        self.assertTrue(dr.have_test_image())

        dr = doxrunner.Runner(argparse.Namespace(
            rebuild=False,
            rebuild_all=False,
            path_map=None,
            user_map=None))
        dr._get_image_list = mock.MagicMock()
        dr._get_image_list.return_value = []
        self.assertFalse(dr.have_test_image())
