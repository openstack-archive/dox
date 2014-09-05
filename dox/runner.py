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
        self.base_image_name = 'dox/%s/base' % self.project
        self.test_image_name = 'dox/%s/test' % self.project

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
            logger.info(e.stderr)
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

        out = process.communicate()
        if len(out) == 0 or not out[0] or not out[0].strip():
            out_text = ''
        out_text = out[0].strip().decode('utf-8')
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
                    uid=os.getuid(), gid=os.getgid(), user=os.getlogin()))
            for add_file in commands.get_add_files():
                shutil.copy(add_file, os.path.join(tempd, add_file))
                dockerfile.append("ADD %s /dox/" % add_file)
            dockerfile.append("WORKDIR /dox")
            for command in commands.prep_commands():
                dockerfile.append("RUN %s\n" % command)
            dockerfile = '\n'.join(dockerfile)
            open(os.path.join(tempd, 'Dockerfile'), 'w').write(dockerfile)
            logger.debug("Dockerfile:\n" + self._indent(dockerfile))
            self._docker_build(self.test_image_name, tempd)
        finally:
            shutil.rmtree(tempd)

    def run_commands(self, command):
        self._docker_run(
            '--privileged=true',
            '--rm', '--user=%s' % os.getlogin(),
            '-v', "%s:/src" % os.path.abspath('.'),
            '-w', '/src', self.test_image_name, *command)

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
