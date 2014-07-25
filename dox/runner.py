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
import shutil
import shlex
import tempfile
import textwrap

import sh

logger = logging.getLogger(__name__)


class Runner(object):

    def __init__(self, args):
        self.args = args
        self.project = os.path.basename(os.path.abspath('.'))
        self.base_image_name = 'dox/%s/base' % self.project
        self.test_image_name = 'dox/%s/test' % self.project

    def _indent(self, text):
        wrapper = textwrap.TextWrapper(
            initial_indent='    ', subsequent_indent='    ')
        return '\n'.join([wrapper.fill(line) for line in text.split('\n')])

    def build_test_image(self, image, commands):
        logger.debug(
            "Building test image %(image)s with %(prep_commands)s" % dict(
                image=self.base_image_name,
                prep_commands=commands.prep_commands()))
        tempd = tempfile.mkdtemp()
        with open(os.path.join(tempd, 'Dockerfile'), 'w') as dockerfile:
            dockerfile.write("FROM %s\n" % image)
            for add_file in commands.get_add_files():
                shutil.copy(add_file, os.path.join(tempd, add_file))
                dockerfile.write("ADD %s /dox\n" % add_file)
            dockerfile.write("WORKDIR /dox\n")
            for command in commands.prep_commands():
                dockerfile.write("RUN %s\n" % command)
        logger.debug(
            "Dockerfile:\n" +
            self._indent(sh.cat(os.path.join(tempd, 'Dockerfile')).stdout))
        try:
            if not self.args.noop:
                sh.docker.build('-t', self.test_image_name, tempd)
        except Exception as e:
            log.error("Test image build failed")
            log.info(e.message)
            raise
        finally:
            shutil.rmtree(tempd)

    def run_commands(self, command):
        try:
            if not self.args.noop:
                sh.docker.run(
                    '--rm',
                    '-v', "%s:/src" % os.path.abspath('.'),
                    '-w', '/src', self.test_image_name, *command)
        except sh.ErrorReturnCode as e:
            logger.error("Commands failed: %s" % e.message)
            raise

    def build_base_image(self):
        logger.info(
            "Building base image %s from Dockerfile" % self.base_image_name)
        if not self.args.noop:
            try:
                sh.docker.build('-t', self.base_image_name, '.')
            except sh.ErrorReturnCode as e:
                logger.error("Commands failed")
                logger.info(e.stderr)
                raise

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
