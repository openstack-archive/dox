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

import dox.commands
import dox.images
import dox.runner


def main():
    parser = argparse.ArgumentParser(description='Run tests in docker.')
    parser.add_argument(dest='extra_args', nargs='*',
                        help='args to append to command, or command to run'
                             ' if -c is given')
    parser.add_argument('-i', '--image', dest='image',
                        help='Base image to use')
    parser.add_argument('-c', '--command', dest='command', default=False,
                        action='store_true',
                        help='Treat arguments as the entire command to run')
    parser.add_argument('-r', '--rebuild', dest='rebuild', default=False,
                        action='store_true',
                        help='Rebuild the test image')
    parser.add_argument('--rebuild-all', dest='rebuild_all', default=False,
                        action='store_true', help='Rebuild all images')
    args = parser.parse_args()

    image = args.image
    if args.image is None:
        image = dox.images.get_image()
    if args.command:
        command = " ".join(args.extra_args)
    else:
        command = dox.commands.Commands()
        if args.extra_args:
            command.append(args.extra_args)
    return dox.runner.Runner(args).run(image, command)
