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
    return parser.parse_args()


def main():

    args = parse_args()
    setup_logging(get_log_level(args))

    return run_dox(args)


def run_dox(args):
    if not dox.runner.Runner(args).is_docker_installed():
        sys.exit(1)

    # Get Image
    if args.images is None:
        images = dox.images.get_images()
    else:
        images = args.images.split(',')

    # Get Command
    if args.command:
        command = dox.config.cmdline.CommandLine(args.extra_args)
        logger.debug("Command source is the command line")
    else:
        command = dox.commands.Commands(args.extra_args)
        logger.debug("Command source is %s" % command.source.source_name())

    # Run
    try:
        run = functools.partial(dox.runner.Runner(args).run,
                                command=command)
        map(run, images)
    except Exception:
        logger.error("Operation failed, aborting dox.", exc_info=args.debug)
        return 1
