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

import argparse
import functools
import logging
import os
import sys

import dox.commands
import dox.config.cmdline
import dox.images
import dox.runner

logger = logging.getLogger(__name__)


def get_log_level(args):
    if args.debug:
        return logging.DEBUG
    if args.quiet:
        return logging.WARN
    return logging.INFO


def setup_logging(level):
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s|%(name)s|%(message)s')
    handler.setFormatter(formatter)
    logger = logging.getLogger('dox')
    logger.setLevel(level)
    logger.addHandler(handler)


def parse_args():
    parser = argparse.ArgumentParser(description='Run tests in docker.')
    parser.add_argument(dest='extra_args', nargs='*',
                        help='args to append to command, or command to run'
                             ' if -c is given')
    parser.add_argument('-i', '--images', dest='images',
                        help='Base images to use')
    parser.add_argument('-e', '--environment', dest='environment',
                        default=None,
                        help='Run target environment.')
    parser.add_argument('-c', '--command', dest='command', default=False,
                        action='store_true',
                        help='Treat arguments as the entire command to run')
    parser.add_argument('-r', '--rebuild', dest='rebuild', default=False,
                        action='store_true',
                        help='Rebuild the test image')
    parser.add_argument('--rebuild-all', dest='rebuild_all', default=False,
                        action='store_true', help='Rebuild all images')
    parser.add_argument('-d', '--debug', dest='debug', default=False,
                        action='store_true', help='Debug mode')
    parser.add_argument('-q', '--quiet', dest='quiet', default=False,
                        action='store_true', help='Quiet output')
    parser.add_argument('-n', '--noop', dest='noop', default=False,
                        action='store_true',
                        help="Don't actually execute commands")
    parser.add_argument('--user-map', default=os.environ.get("DOX_USER_MAP"),
                        help='User to run the container to '
                        'format is user:uid:gid, with boot2docker use '
                        'docker:1000:10 (default to your current user)')
    parser.add_argument('--path-map', default=os.environ.get("DOX_PATH_MAP"),
                        help='with boot2docker, specify how osx path maps to '
                             'linux path. example --path-map /Users:/home, '
                             'means /Users is available as /home on docker '
                             'container')
    parser.add_argument('-k', '--keep', dest='keep_image', default=False,
                        action='store_true',
                        help="Keep test container after command finishes")
    return parser.parse_args()


def main():
    args = parse_args()
    setup_logging(get_log_level(args))

    return runner(args)


def run_dox(args, images, command, image_name):
    # Run
    try:
        run = functools.partial(dox.runner.Runner(args, image_name).run,
                                command=command)
        map(run, images)
    except Exception:
        logger.error("Operation failed, aborting dox.", exc_info=args.debug)
        return 1


def runner(args):
    options = {}
    args_images = None

    if not dox.runner.Runner(args).is_docker_installed():
        sys.exit(1)

    # Get Image
    if args.images:
        args_images = args.images.split(',')

    if args.command:
        command = dox.config.cmdline.CommandLine(args.extra_args)
        logger.debug("Command source is the command line")
        return run_dox(args, args_images, command)

    if args.environment:
        sections = args.environment.split(',')
    else:
        sections = ['_default']

    for section in sections:
        options['section'] = section

        if args_images:
            images = args_images
        else:
            images = dox.images.get_images(options)

        command = dox.commands.Commands(args.extra_args, options)
        logger.debug("Command source is %s, section %s" % (
            command.source.source_name(), section))

        # TODO(chmouel): add to section a proper image_name that include the
        # type of backend i.e: dox_yaml/tox_init
        run_dox(args, images, command, image_name=section)
