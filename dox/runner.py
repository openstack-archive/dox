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

__all__ = [
    'Runner',
]

import logging
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import textwrap

logger = logging.getLogger(__name__)


class Runner(object):

    def __init__(self, args):
        self.args = args
        self.project = os.path.basename(os.path.abspath('.'))
        self.base_image_name = 'dox_%s_base' % self.project
        self.test_image_name = 'dox_%s_test' % self.project
        self.user_map = self._get_user_mapping()
        self.path_map = self._get_path_mapping()

    def _get_user_mapping(self):
        """Get user mapping from command line or current user."""
        if self.args.user_map:
            username, uid, gid = self.args.user_map.split(':')
        else:
            username, uid, gid = (os.getlogin(), os.getuid(), os.getgid())
        return {'username': username, 'uid': int(uid), 'gid': int(gid)}

    def _get_path_mapping(self):
        """Get path mapping from command line."""
        if not self.args.path_map:
            return None
        local, remote = self.args.path_map.split(':')
        return {'local': local, 'remote': remote}

    def is_docker_installed(self):
        try:
            self._docker_cmd("version")
        except OSError as e:
            msg = 'docker does not seem installed'
            if e.errno == 2 and not self.args.debug:
                logger.error(msg)
            else:
                logger.exception(msg)
            return False
        return True

    def _docker_build(self, image, image_dir='.'):
        logger.info('Building image %s' % image)
        self._docker_cmd('build', '-t', image, image_dir)

    def _docker_run(self, *args):
        logger.info('Running docker')
        self._docker_cmd('run', *args)

    def _docker_cmd(self, *args):
        base_docker = ['docker']
        if self.args.debug:
            base_docker.append('-D')
        try:
            self._run_shell_command(base_docker + list(args))
        except Exception as e:
            logger.error("docker failed")
            logger.info(e)
            raise

    def _run_shell_command(self, cmd):

        logger.debug('shell: ' + ' '.join(cmd))
        if self.args.noop:
            return

        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        while True:
            output = process.stdout.read(1)

            if output == '' and process.poll() is not None:
                break

            if output != '' and not self.args.quiet:
                sys.stdout.write(output)
                sys.stdout.flush()

        if process.returncode:
            raise Exception(
                "%s returned %d" % (cmd, process.returncode))

    def _indent(self, text):
        wrapper = textwrap.TextWrapper(
            initial_indent='    ', subsequent_indent='        ')
        return '\n'.join([wrapper.fill(line) for line in text.split('\n')])

    def _get_image_list(self):

        process = subprocess.Popen(
            shlex.split('docker images'),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        stdout, _ = process.communicate()
        out_text = stdout.strip().decode('utf-8') if stdout else ""
        return dict([f.split()[:2] for f in out_text.split('\n')])

    def have_test_image(self):
        if self.args.rebuild or self.args.rebuild_all:
            return False
        if self.test_image_name in self._get_image_list():
            return True
        return False

    def build_test_image(self, image, commands):

        logger.debug(
            "Want test image %(image)s with %(prep_commands)s" % dict(
                image=self.test_image_name,
                prep_commands=commands.prep_commands()))
        if self.have_test_image():
            return

        dockerfile = []
        dockerfile.append("FROM %s" % image)
        try:
            tempd = tempfile.mkdtemp()
            dockerfile.append(
                "RUN useradd -M -U -d /src -u %(uid)s %(user)s" % dict(
                    uid=self.user_map['uid'],
                    gid=self.user_map['gid'],
                    user=self.user_map['username']))
            for add_file in commands.get_add_files():
                shutil.copy(add_file, os.path.join(tempd, add_file))
                dockerfile.append("ADD %s /dox/" % add_file)
            dockerfile.append("WORKDIR /dox")
            for command in commands.prep_commands():
                dockerfile.append("RUN %s\n" % command)
            dockerfile = '\n'.join(dockerfile)
            with open(os.path.join(tempd, 'Dockerfile'), 'w') as f:
                f.write(dockerfile)
            logger.debug("Dockerfile:\n" + self._indent(dockerfile))
            self._docker_build(self.test_image_name, tempd)
        finally:
            shutil.rmtree(tempd)

    def run_commands(self, command):
        path = os.path.abspath('.')
        if self.path_map:
            path = path.replace(self.path_map['local'],
                                self.path_map['remote'])
        docker_args = ['--privileged=true',
                       '--user=%s' % self.user_map['username'],
                       '-v', "%s:/src" % path,
                       '-w', '/src']
        if not self.args.keep_image:
            docker_args.append('--rm')
        docker_args.append(self.test_image_name)
        for c in command:
            docker_args.append(c)
        self._docker_run(*docker_args)

    def have_base_image(self):
        if self.args.rebuild_all:
            return False
        if self.base_image_name in self._get_image_list():
            return True
        return False

    def build_base_image(self):

        logger.debug("Want base image")
        if self.have_base_image():
            return
        self._docker_build(self.base_image_name)

    def run(self, image, command):
        logger.debug(
            "Going to run %(command)s in %(image)s" % dict(
                command=command.test_command(), image=image))
        if self.args.rebuild:
            logger.debug("Need to rebuild")

        if image is None:
            self.build_base_image()
        self.build_test_image(image, command)

        self.run_commands(shlex.split(command.test_command()))
